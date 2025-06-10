from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import traceback
import base64
from PIL import Image
from io import BytesIO

# Create blueprint for NSFW detection API
nsfw_bp = Blueprint('nsfw', __name__, url_prefix='/nsfw')

def init_nsfw_api(app, nsfw_service):
    """Initialize NSFW detection API routes"""
    
    def allowed_file(filename):
        """Check if file extension is allowed"""
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @nsfw_bp.route('/detect', methods=['POST'])
    def detect_nsfw():
        """
        Detect NSFW content in uploaded image
        
        Expected: multipart/form-data with 'image' file
        Returns: JSON with detection results
        """
        try:
            # Check if service is available
            if nsfw_service is None:
                return jsonify({
                    "error": "NSFW Detection Service not available",
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
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save uploaded file
            file.save(file_path)
            
            try:
                # Process image with NSFW detection
                result = nsfw_service.detect_nsfw(file_path)
                
                # Clean up uploaded file
                os.remove(file_path)
                
                # Return results
                return jsonify({
                    "success": True,
                    "data": {
                        "file_path": file_path,
                        "is_nsfw": result["is_nsfw"],
                        "confidence": result["confidence"],
                        "threshold": result["threshold"],
                        "predictions": result["all_predictions"]
                    }
                }), 200
                
            except Exception as e:
                # Clean up uploaded file in case of error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        except Exception as e:
            print(f"Error in detect_nsfw: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @nsfw_bp.route('/detect-base64', methods=['POST'])
    def detect_nsfw_base64():
        """
        Detect NSFW content from base64 encoded image
        
        Expected: JSON with 'image_base64' field
        Returns: JSON with detection results
        """
        try:
            # Check if service is available
            if nsfw_service is None:
                return jsonify({
                    "error": "NSFW Detection Service not available",
                    "success": False
                }), 503
            
            data = request.get_json()
            
            if not data or 'image_base64' not in data:
                return jsonify({
                    "error": "No base64 image data provided",
                    "success": False
                }), 400
            
            # Decode base64 image
            try:
                image_data = base64.b64decode(data['image_base64'])
                image = Image.open(BytesIO(image_data))
            except Exception as e:
                return jsonify({
                    "error": f"Invalid base64 image data: {str(e)}",
                    "success": False
                }), 400
            
            # Process image with NSFW detection
            result = nsfw_service.detect_nsfw_from_pil_image(image)
            
            # Return results
            return jsonify({
                "success": True,
                "data": {
                    "is_nsfw": result["is_nsfw"],
                    "confidence": result["confidence"],
                    "threshold": result["threshold"],
                    "predictions": result["all_predictions"]
                }
            }), 200
            
        except Exception as e:
            print(f"Error in detect_nsfw_base64: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @nsfw_bp.route('/batch-detect', methods=['POST'])
    def batch_detect_nsfw():
        """
        Detect NSFW content in multiple uploaded images
        
        Expected: multipart/form-data with multiple 'images' files
        Returns: JSON with detection results for all images
        """
        try:
            # Check if service is available
            if nsfw_service is None:
                return jsonify({
                    "error": "NSFW Detection Service not available",
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
                        # Process image with NSFW detection
                        result = nsfw_service.detect_nsfw(file_path)
                        
                        results.append({
                            "index": i,
                            "filename": file.filename,
                            "is_nsfw": result["is_nsfw"],
                            "confidence": result["confidence"],
                            "threshold": result["threshold"],
                            "predictions": result["all_predictions"],
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
            print(f"Error in batch_detect_nsfw: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @nsfw_bp.route('/info', methods=['GET'])
    def nsfw_info():
        """Get NSFW service information"""
        if nsfw_service is not None:
            info = {
                "model_name": nsfw_service.model_name,
                "threshold": nsfw_service.threshold,
                "loaded": True
            }
        else:
            info = {
                "loaded": False,
                "error": "Service not available"
            }
        
        return jsonify({
            "success": True,
            "service": "NSFW Detection",
            "info": info
        }), 200

    # Register the blueprint
    app.register_blueprint(nsfw_bp)
