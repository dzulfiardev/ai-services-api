from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import traceback
import base64
from PIL import Image
from io import BytesIO
import json

# Create blueprint for ID Card API
id_card_bp = Blueprint('id_card', __name__, url_prefix='/id-card')

def init_id_card_api(app, id_card_service):
    """Initialize ID Card API routes"""
    
    def allowed_file(filename):
        """Check if file extension is allowed"""
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @id_card_bp.route('/detect-and-extract', methods=['POST'])
    def detect_and_extract_id_card():
        """
        Detect and extract data from ID card in uploaded image
        
        Expected: multipart/form-data with 'image' file
        Returns: JSON with detected ID card data
        """
        try:
            # Check if service is available
            if id_card_service is None:
                return jsonify({
                    "error": "ID Card Service not available",
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
            unique_filename = f"id_card_{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save uploaded file
            file.save(file_path)
            
            try:
                # Process ID card
                result = id_card_service.process_id_card(file_path)
                
                # Clean up uploaded file
                os.remove(file_path)
                
                # Return results
                if result["success"]:
                    return jsonify({
                        "success": True,
                        "data": {
                            "filename": file.filename,
                            "card_detected": result["card_detected"],
                            "extracted_data": result["extracted_data"],
                            "confidence": {
                                "average": round(result["avg_confidence"], 4),
                                "individual_scores": [round(score, 4) for score in result["confidence_scores"]]
                            },
                            "processing_info": {
                                "bbox": result["bbox"],
                                "total_text_items": len(result["raw_ocr_results"])
                            }
                        }
                    }), 200
                else:
                    return jsonify({
                        "success": False,
                        "error": result["error"]
                    }), 500
                
            except Exception as e:
                # Clean up uploaded file in case of error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        except Exception as e:
            print(f"Error in detect_and_extract_id_card: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @id_card_bp.route('/detect-and-extract-base64', methods=['POST'])
    def detect_and_extract_id_card_base64():
        """
        Detect and extract data from ID card in base64 encoded image
        
        Expected: JSON with 'image_base64' field
        Returns: JSON with detected ID card data
        """
        try:
            # Check if service is available
            if id_card_service is None:
                return jsonify({
                    "error": "ID Card Service not available",
                    "success": False
                }), 503
            
            data = request.get_json()
            
            if not data or 'image_base64' not in data:
                return jsonify({
                    "error": "No base64 image data provided",
                    "success": False
                }), 400
            
            # Decode base64 image and save temporarily
            try:
                image_data = base64.b64decode(data['image_base64'])
                image = Image.open(BytesIO(image_data))
                
                # Save temporary file
                unique_filename = f"id_card_{uuid.uuid4().hex}.jpg"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                image.save(file_path)
                
            except Exception as e:
                return jsonify({
                    "error": f"Invalid base64 image data: {str(e)}",
                    "success": False
                }), 400
            
            try:
                # Process ID card
                result = id_card_service.process_id_card(file_path)
                
                # Clean up temporary file
                os.remove(file_path)
                
                # Return results
                if result["success"]:
                    return jsonify({
                        "success": True,
                        "data": {
                            "card_detected": result["card_detected"],
                            "extracted_data": result["extracted_data"],
                            "confidence": {
                                "average": round(result["avg_confidence"], 4),
                                "individual_scores": [round(score, 4) for score in result["confidence_scores"]]
                            },
                            "processing_info": {
                                "bbox": result["bbox"],
                                "total_text_items": len(result["raw_ocr_results"])
                            }
                        }
                    }), 200
                else:
                    return jsonify({
                        "success": False,
                        "error": result["error"]
                    }), 500
                    
            except Exception as e:
                # Clean up temporary file in case of error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        except Exception as e:
            print(f"Error in detect_and_extract_id_card_base64: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @id_card_bp.route('/detect-only', methods=['POST'])
    def detect_id_card_only():
        """
        Only detect ID card location in image without text extraction
        
        Expected: multipart/form-data with 'image' file
        Returns: JSON with detection results
        """
        try:
            # Check if service is available
            if id_card_service is None:
                return jsonify({
                    "error": "ID Card Service not available",
                    "success": False
                }), 503
            
            # Check if file is present in request
            if 'image' not in request.files:
                return jsonify({
                    "error": "No image file provided",
                    "success": False
                }), 400
            
            file = request.files['image']
            
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({
                    "error": "Invalid file",
                    "success": False
                }), 400
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"detect_{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save uploaded file
            file.save(file_path)
            
            try:
                # Detect ID card only
                bbox = id_card_service.detect_id_card(file_path)
                
                # Clean up uploaded file
                os.remove(file_path)
                
                return jsonify({
                    "success": True,
                    "data": {
                        "filename": file.filename,
                        "card_detected": bbox is not None,
                        "bbox": bbox,
                        "message": "ID card detected" if bbox else "No ID card detected"
                    }
                }), 200
                
            except Exception as e:
                # Clean up uploaded file in case of error
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e
                
        except Exception as e:
            print(f"Error in detect_id_card_only: {str(e)}")
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @id_card_bp.route('/batch-process', methods=['POST'])
    def batch_process_id_cards():
        """
        Process multiple ID card images
        
        Expected: multipart/form-data with multiple 'images' files
        Returns: JSON with processing results for all images
        """
        try:
            # Check if service is available
            if id_card_service is None:
                return jsonify({
                    "error": "ID Card Service not available",
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
                            "error": f"File type not allowed",
                            "success": False
                        })
                        continue
                    
                    # Generate unique filename
                    file_extension = file.filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"batch_{i}_{uuid.uuid4().hex}.{file_extension}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    # Save uploaded file
                    file.save(file_path)
                    uploaded_files.append(file_path)
                    
                    try:
                        # Process ID card
                        result = id_card_service.process_id_card(file_path)
                        
                        if result["success"]:
                            results.append({
                                "index": i,
                                "filename": file.filename,
                                "card_detected": result["card_detected"],
                                "extracted_data": result["extracted_data"],
                                "avg_confidence": round(result["avg_confidence"], 4),
                                "success": True
                            })
                        else:
                            results.append({
                                "index": i,
                                "filename": file.filename,
                                "error": result["error"],
                                "success": False
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
                
                successful_results = [r for r in results if r.get("success", False)]
                
                return jsonify({
                    "success": True,
                    "total_files": len(files),
                    "successful_extractions": len(successful_results),
                    "results": results
                }), 200
                
            except Exception as e:
                # Clean up uploaded files in case of error
                for file_path in uploaded_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                raise e
                
        except Exception as e:
            print(f"Error in batch_process_id_cards: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "error": f"Internal server error: {str(e)}",
                "success": False
            }), 500

    @id_card_bp.route('/info', methods=['GET'])
    def id_card_service_info():
        """Get ID Card service information"""
        if id_card_service is not None:
            info = id_card_service.get_model_info()
        else:
            info = {
                "loaded": False,
                "error": "Service not available"
            }
        
        return jsonify({
            "success": True,
            "service": "ID Card Detection and Extraction",
            "info": info,
            "supported_formats": ["PNG", "JPG", "JPEG", "GIF", "BMP", "WEBP"],
            "capabilities": [
                "ID Card Detection",
                "Text Extraction",
                "Structured Data Parsing",
                "Batch Processing"
            ]
        }), 200

    # Register the blueprint
    app.register_blueprint(id_card_bp)
