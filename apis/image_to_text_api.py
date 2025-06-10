from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import traceback
import base64
from PIL import Image
from io import BytesIO

# Create blueprint for Image to Text API
ocr_bp = Blueprint('ocr', __name__, url_prefix='/ocr')

def init_ocr_api(app, image_to_text_service):
    """Initialize Image to Text API routes"""
    
    def allowed_file(filename):
        """Check if file extension is allowed"""
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @ocr_bp.route('/extract-text', methods=['POST'])
    def extract_text():
        """
        Extract text from uploaded image using OCR
        
        Expected: multipart/form-data with 'image' file
        Returns: JSON with extracted text
        """
        try:
            # Check if service is available
            if image_to_text_service is None:
                return jsonify({
                    "error": "Image to Text Service not available",
                    "success": False
                }), 503
            
            # Check if file is present in request
            if 'image' not in request.files:
                return jsonify({
                    "error": "No image file provided",
                    "success": False
                }), 400
            
            file = request.files['image']
            
            # Check if file is selected
            if file.filename == '':
                return jsonify({
                    "error": "No image file selected",
                    "success": False
                }), 400
            
            # Check if file type is allowed
            if not allowed_file(file.filename):
                return jsonify({
                    "error": f"File type not allowed. Supported types: png, jpg, jpeg, gif, bmp, webp",
                    "success": False
                }), 400
            
            # Get optional max_length parameter
            max_length = request.form.get('max_length', 512, type=int)
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save uploaded file
            file.save(file_path)
            
            try:
                # Process image with OCR
                result = image_to_text_service.extract_text_from_image(file_path, max_length)
                
                # Clean up uploaded file
                os.remove(file_path)
                
                # Return results
                return jsonify({
                    "success": True,
                    "data": {
                        "extracted_text": result["extracted_text"],
                        "text_length": result["text_length"],
                        "model_used": result["model_used"],
                        "filename": file.filename,
                        "results": result
                    }
                }), 200
                
            except Exception as e:
                # Clean up uploaded file in case of error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        except Exception as e:
            print(f"Error in extract_text: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @ocr_bp.route('/extract-text-base64', methods=['POST'])
    def extract_text_base64():
        """
        Extract text from base64 encoded image
        
        Expected: JSON with 'image_base64' field
        Returns: JSON with extracted text
        """
        try:
            # Check if service is available
            if image_to_text_service is None:
                return jsonify({
                    "error": "Image to Text Service not available",
                    "success": False
                }), 503
            
            data = request.get_json()
            
            if not data or 'image_base64' not in data:
                return jsonify({
                    "error": "No base64 image data provided",
                    "success": False
                }), 400
            
            # Get optional max_length parameter
            max_length = data.get('max_length', 512)
            
            # Decode base64 image
            try:
                image_data = base64.b64decode(data['image_base64'])
                image = Image.open(BytesIO(image_data))
            except Exception as e:
                return jsonify({
                    "error": f"Invalid base64 image data: {str(e)}",
                    "success": False
                }), 400
            
            # Process image with OCR
            result = image_to_text_service.extract_text_from_pil_image(image, max_length)
            
            # Return results
            return jsonify({
                "success": True,
                "data": {
                    "extracted_text": result["extracted_text"],
                    "text_length": result["text_length"],
                    "model_used": result["model_used"]
                }
            }), 200
            
        except Exception as e:
            print(f"Error in extract_text_base64: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @ocr_bp.route('/batch-extract-text', methods=['POST'])
    def batch_extract_text():
        """
        Extract text from multiple uploaded images
        
        Expected: multipart/form-data with multiple 'images' files
        Returns: JSON with text extraction results for all images
        """
        try:
            # Check if service is available
            if image_to_text_service is None:
                return jsonify({
                    "error": "Image to Text Service not available",
                    "success": False
                }), 503
            
            # Check if files are present in request
            if 'images' not in request.files:
                return jsonify({
                    "error": "No image files provided",
                    "success": False
                }), 400
            
            files = request.files.getlist('images')
            
            if not files or len(files) == 0:
                return jsonify({
                    "error": "No image files selected",
                    "success": False
                }), 400
            
            # Get optional max_length parameter
            max_length = request.form.get('max_length', 512, type=int)
            
            results = []
            uploaded_files = []
            
            try:
                # Process each file
                for i, file in enumerate(files):
                    if file.filename == '':
                        results.append({
                            "index": i,
                            "filename": "",
                            "error": "Empty filename",
                            "success": False
                        })
                        continue
                    
                    if not allowed_file(file.filename):
                        results.append({
                            "index": i,
                            "filename": file.filename,
                            "error": f"File type not allowed. Supported types: png, jpg, jpeg, gif, bmp, webp",
                            "success": False
                        })
                        continue
                    
                    # Generate unique filename
                    file_extension = file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    # Save uploaded file
                    file.save(file_path)
                    uploaded_files.append(file_path)
                    
                    try:
                        # Process image with OCR
                        result = image_to_text_service.extract_text_from_image(file_path, max_length)
                        
                        results.append({
                            "index": i,
                            "filename": file.filename,
                            "extracted_text": result["extracted_text"],
                            "text_length": result["text_length"],
                            "model_used": result["model_used"],
                            "success": True
                        })
                        
                    except Exception as e:
                        results.append({
                            "index": i,
                            "filename": file.filename,
                            "error": str(e),
                            "success": False
                        })
                
                # Clean up all uploaded files
                for file_path in uploaded_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                return jsonify({
                    "success": True,
                    "total_files": len(files),
                    "results": results
                }), 200
                
            except Exception as e:
                # Clean up uploaded files in case of error
                for file_path in uploaded_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                raise e
                
        except Exception as e:
            print(f"Error in batch_extract_text: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @ocr_bp.route('/info', methods=['GET'])
    def ocr_info():
        """Get OCR service information"""
        if image_to_text_service is not None:
            info = image_to_text_service.get_model_info()
        else:
            info = {
                "loaded": False,
                "error": "Service not available"
            }
        
        return jsonify({
            "success": True,
            "service": "Image to Text (OCR)",
            "info": info
        }), 200

    # Register the blueprint
    app.register_blueprint(ocr_bp)
