from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import os
import uuid
from werkzeug.utils import secure_filename
from services.nsfw_detection_service import NSFWDetectionService
from services.image_to_text_service import ImageToTextService
import traceback
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize NSFW Detection Service
try:
    nsfw_service = NSFWDetectionService(threshold=0.5)
    print("NSFW Detection Service initialized successfully")
except Exception as e:
    print(f"Failed to initialize NSFW Detection Service: {e}")
    nsfw_service = None

# Initialize Image to Text Service
try:
    image_to_text_service = ImageToTextService()
    print("Image to Text Service initialized successfully")
except Exception as e:
    print(f"Failed to initialize Image to Text Service: {e}")
    image_to_text_service = None

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Services API",
        "nsfw_model_loaded": nsfw_service is not None,
        "ocr_model_loaded": image_to_text_service is not None,
        "version": "1.0.0"
    }), 200

@app.route('/detect-nsfw', methods=['POST'])
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
                "error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}",
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

@app.route('/detect-nsfw-base64', methods=['POST'])
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

@app.route('/batch-detect-nsfw', methods=['POST'])
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
                        "error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}",
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

@app.route('/extract-text', methods=['POST'])
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
                "error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}",
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
                    "filename": file.filename
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

@app.route('/extract-text-base64', methods=['POST'])
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

@app.route('/batch-extract-text', methods=['POST'])
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
                        "error": f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}",
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

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about loaded models"""
    info = {
        "nsfw_service": None,
        "ocr_service": None
    }
    
    if nsfw_service is not None:
        info["nsfw_service"] = {
            "model_name": nsfw_service.model_name,
            "threshold": nsfw_service.threshold,
            "loaded": True
        }
    
    if image_to_text_service is not None:
        info["ocr_service"] = image_to_text_service.get_model_info()
    
    return jsonify({
        "success": True,
        "models": info
    }), 200

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "error": "File too large. Maximum size is 16MB",
        "success": False
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "success": False
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "error": "Method not allowed",
        "success": False
    }), 405

if __name__ == '__main__':
    print("Starting AI Services API...")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
    print("Available endpoints:")
    print("  GET  /health - Health check")
    print("  POST /detect-nsfw - Upload image file for detection")
    print("  POST /detect-nsfw-base64 - Send base64 encoded image")
    print("  POST /batch-detect-nsfw - Upload multiple images")
    print("  POST /extract-text - Upload image file for text extraction")
    print("  POST /extract-text-base64 - Send base64 encoded image for text extraction")
    print("  POST /batch-extract-text - Upload multiple images for text extraction")
    print("  GET  /model-info - Get information about loaded models")
    app.run(debug=True, host='0.0.0.0', port=5000)
