from flask import Flask, jsonify
from flask_cors import CORS
import os

# Import services
from services.nsfw_detection_service import NSFWDetectionService
from services.image_to_text_service import ImageToTextService
from services.id_card_service import IDCardService

# Import API modules
from apis.nsfw_detection_api import init_nsfw_api
from apis.image_to_text_api import init_ocr_api
from apis.id_card_api import init_id_card_api

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

# Initialize services
print("Initializing AI Services...")

# Initialize NSFW Detection Service
try:
    nsfw_service = NSFWDetectionService(threshold=0.5)
    print("✅ NSFW Detection Service initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize NSFW Detection Service: {e}")
    nsfw_service = None

# Initialize Image to Text Service
try:
    image_to_text_service = ImageToTextService()
    print("✅ Image to Text Service initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Image to Text Service: {e}")
    image_to_text_service = None

# Initialize ID Card Service
try:
    id_card_service = IDCardService()
    print("✅ ID Card Service initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize ID Card Service: {e}")
    id_card_service = None

# Initialize API routes
print("Setting up API routes...")

# Initialize NSFW API routes
init_nsfw_api(app, nsfw_service)
print("✅ NSFW API routes registered at /nsfw/*")

# Initialize OCR API routes
init_ocr_api(app, image_to_text_service)
print("✅ OCR API routes registered at /ocr/*")

# Initialize ID Card API routes
init_id_card_api(app, id_card_service)
print("✅ ID Card API routes registered at /id-card/*")

# Main routes
@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        "message": "AI Services API",
        "version": "2.0.0",
        "services": {
            "nsfw_detection": {
                "available": nsfw_service is not None,
                "endpoints": ["/nsfw/detect", "/nsfw/detect-base64", "/nsfw/batch-detect", "/nsfw/info"]
            },
            "image_to_text": {
                "available": image_to_text_service is not None,
                "endpoints": ["/ocr/extract-text", "/ocr/extract-text-base64", "/ocr/batch-extract-text", "/ocr/info"]
            },
            "id_card_processing": {
                "available": id_card_service is not None,
                "endpoints": ["/id-card/detect-and-extract", "/id-card/detect-and-extract-base64", "/id-card/info"]
            }
        },
        "general_endpoints": ["/health", "/model-info"],
        "documentation": "See README.md for detailed API documentation"
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Services API",
        "version": "2.0.0",
        "services": {
            "nsfw_detection": {
                "loaded": nsfw_service is not None,
                "status": "healthy" if nsfw_service is not None else "unavailable"
            },
            "image_to_text": {
                "loaded": image_to_text_service is not None,
                "status": "healthy" if image_to_text_service is not None else "unavailable"
            },
            "id_card_processing": {
                "loaded": id_card_service is not None,
                "status": "healthy" if id_card_service is not None else "unavailable"
            }
        }
    }), 200

@app.route('/model-info', methods=['GET'])
def model_info():
    """Get information about all loaded models"""
    info = {
        "nsfw_service": None,
        "ocr_service": None,
        "id_card_service": None
    }
    
    if nsfw_service is not None:
        info["nsfw_service"] = {
            "model_name": nsfw_service.model_name,
            "threshold": nsfw_service.threshold,
            "loaded": True,
            "endpoints": ["/nsfw/detect", "/nsfw/detect-base64", "/nsfw/batch-detect"]
        }
    
    if image_to_text_service is not None:
        info["ocr_service"] = image_to_text_service.get_model_info()
        info["ocr_service"]["endpoints"] = ["/ocr/extract-text", "/ocr/extract-text-base64", "/ocr/batch-extract-text"]
    
    if id_card_service is not None:
        info["id_card_service"] = id_card_service.get_model_info()
        info["id_card_service"]["endpoints"] = ["/id-card/detect-and-extract", "/id-card/detect-and-extract-base64"]
    
    return jsonify({
        "success": True,
        "version": "2.0.0",
        "models": info
    }), 200

# Legacy compatibility endpoints (redirect to new endpoints)
@app.route('/detect-nsfw', methods=['POST'])
def legacy_detect_nsfw():
    """Legacy endpoint - redirects to new endpoint"""
    return jsonify({
        "error": "This endpoint has moved to /nsfw/detect",
        "success": False,
        "redirect": "/nsfw/detect",
        "message": "Please update your API calls to use the new endpoint structure"
    }), 301

@app.route('/detect-nsfw-base64', methods=['POST'])
def legacy_detect_nsfw_base64():
    """Legacy endpoint - redirects to new endpoint"""
    return jsonify({
        "error": "This endpoint has moved to /nsfw/detect-base64",
        "success": False,
        "redirect": "/nsfw/detect-base64",
        "message": "Please update your API calls to use the new endpoint structure"
    }), 301

@app.route('/batch-detect-nsfw', methods=['POST'])
def legacy_batch_detect_nsfw():
    """Legacy endpoint - redirects to new endpoint"""
    return jsonify({
        "error": "This endpoint has moved to /nsfw/batch-detect",
        "success": False,
        "redirect": "/nsfw/batch-detect",
        "message": "Please update your API calls to use the new endpoint structure"
    }), 301

@app.route('/extract-text', methods=['POST'])
def legacy_extract_text():
    """Legacy endpoint - redirects to new endpoint"""
    return jsonify({
        "error": "This endpoint has moved to /ocr/extract-text",
        "success": False,
        "redirect": "/ocr/extract-text",
        "message": "Please update your API calls to use the new endpoint structure"
    }), 301

@app.route('/extract-text-base64', methods=['POST'])
def legacy_extract_text_base64():
    """Legacy endpoint - redirects to new endpoint"""
    return jsonify({
        "error": "This endpoint has moved to /ocr/extract-text-base64",
        "success": False,
        "redirect": "/ocr/extract-text-base64",
        "message": "Please update your API calls to use the new endpoint structure"
    }), 301

@app.route('/batch-extract-text', methods=['POST'])
def legacy_batch_extract_text():
    """Legacy endpoint - redirects to new endpoint"""
    return jsonify({
        "error": "This endpoint has moved to /ocr/batch-extract-text",
        "success": False,
        "redirect": "/ocr/batch-extract-text",
        "message": "Please update your API calls to use the new endpoint structure"
    }), 301

# Error handlers
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
        "success": False,
        "available_endpoints": {
            "general": ["/", "/health", "/model-info"],
            "nsfw": ["/nsfw/detect", "/nsfw/detect-base64", "/nsfw/batch-detect", "/nsfw/info"],
            "ocr": ["/ocr/extract-text", "/ocr/extract-text-base64", "/ocr/batch-extract-text", "/ocr/info"],
            "id_card": ["/id-card/detect-and-extract", "/id-card/detect-and-extract-base64", "/id-card/info"]
        }
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({
        "error": "Method not allowed",
        "success": False
    }), 405

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting AI Services API v2.0")
    print("="*60)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"📋 Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
    print(f"📏 Max file size: {MAX_CONTENT_LENGTH // (1024*1024)}MB")
    print("\n📡 Available API Endpoints:")
    print("   General:")
    print("     GET  / - API information")
    print("     GET  /health - Health check")
    print("     GET  /model-info - Model information")
    print("   NSFW Detection:")
    print("     POST /nsfw/detect - Upload image file")
    print("     POST /nsfw/detect-base64 - Base64 encoded image")
    print("     POST /nsfw/batch-detect - Multiple images")
    print("     GET  /nsfw/info - Service information")
    print("   Text Extraction (OCR):")
    print("     POST /ocr/extract-text - Upload image file")
    print("     POST /ocr/extract-text-base64 - Base64 encoded image")
    print("     POST /ocr/batch-extract-text - Multiple images")
    print("     GET  /ocr/info - Service information")
    print("   ID Card Processing:")
    print("     POST /id-card/detect-and-extract - Upload ID card image")
    print("     POST /id-card/detect-and-extract-base64 - Base64 encoded ID card")
    print("     GET  /id-card/info - Service information")
    print("\n🔗 Legacy endpoints redirect to new structure")
    print("="*60)
    print("🌐 Server starting at http://localhost:5000")
    print("="*60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
