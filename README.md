# AI Services REST API

A Flask-based REST API service for AI-powered image processing including NSFW detection, text extraction (OCR), and ID card detection & data extraction using machine learning.

## Features

- **NSFW Detection**: Upload images for Not Safe For Work content detection
- **Text Extraction (OCR)**: Extract text from images using advanced OCR models
- **ID Card Processing**: Detect ID cards in images and extract personal data with structured field parsing
- **Base64 Image Support**: Send base64 encoded images for all services
- **Batch Processing**: Process multiple images at once
- **Health Check**: Monitor API status and model loading
- **Error Handling**: Comprehensive error responses
- **File Validation**: Support for common image formats (PNG, JPG, JPEG, GIF, BMP, WEBP)

## Project Structure

```
api-services-api/
├── app.py                          # Main Flask application (modular)
├── app_legacy.py                   # Original monolithic app (backup)
├── demo.py                         # Interactive demo script
├── apis/                           # API modules
│   ├── __init__.py
│   ├── nsfw_detection_api.py       # NSFW detection endpoints
│   ├── image_to_text_api.py        # Image to text (OCR) endpoints
│   └── id_card_api.py              # ID card processing endpoints
├── services/
│   ├── __init__.py
│   ├── nsfw_detection_service.py   # NSFW detection service
│   ├── image_to_text_service.py    # Image to text (OCR) service
│   └── id_card_service.py          # ID card detection & extraction service
├── test_api.py                     # Legacy API test client
├── test_nsfw_api.py                # NSFW API test client
├── test_ocr_api.py                 # OCR API test client
├── test_id_card_api.py             # ID card API test client
├── requirements.txt                # Python dependencies
├── uploads/                        # Temporary upload directory
├── image_sample/
└── image_generation/
```

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Flask (if not in requirements):**
   ```bash
   pip install flask flask-cors
   ```

## Usage

### Start the API Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Services API",
  "version": "2.0.0",
  "services": {
    "nsfw_detection": {
      "loaded": true,
      "status": "healthy"
    },
    "image_to_text": {
      "loaded": true,
      "status": "healthy"
    },
    "id_card_processing": {
      "loaded": true,
      "status": "healthy"
    }
  }
}
```

#### 2. Single Image Detection (File Upload)
```bash
POST /detect-nsfw
Content-Type: multipart/form-data
```

**Request:**
- Field: `image` (file)

**Example with curl:**
```bash
curl -X POST -F "image=@./image_sample/imagetest-5.png" http://localhost:5000/detect-nsfw
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_nsfw": false,
    "confidence": 0.1234,
    "threshold": 0.5,
    "predictions": [
      {"label": "safe", "score": 0.8766},
      {"label": "nsfw", "score": 0.1234}
    ]
  }
}
```

#### 3. Base64 Image Detection
```bash
POST /detect-nsfw-base64
Content-Type: application/json
```

**Request:**
```json
{
  "image_base64": "base64_encoded_image_data"
}
```

**Example with Python:**
```python
import requests
import base64

with open('image.png', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

response = requests.post('http://localhost:5000/detect-nsfw-base64', 
                        json={"image_base64": image_data})
print(response.json())
```

#### 4. Batch Image Detection
```bash
POST /batch-detect-nsfw
Content-Type: multipart/form-data
```

**Request:**
- Field: `images` (multiple files)

**Example with curl:**
```bash
curl -X POST \
  -F "images=@./image1.png" \
  -F "images=@./image2.jpg" \
  http://localhost:5000/batch-detect-nsfw
```

**Response:**
```json
{
  "success": true,
  "total_files": 2,
  "results": [
    {
      "index": 0,
      "filename": "image1.png",
      "is_nsfw": false,
      "confidence": 0.1234,
      "threshold": 0.5,
      "predictions": [...],
      "success": true
    },
    {
      "index": 1,
      "filename": "image2.jpg",
      "is_nsfw": true,
      "confidence": 0.8765,
      "threshold": 0.5,
      "predictions": [...],
      "success": true
    }
  ]
}
```

#### 5. Text Extraction from Image (File Upload)
```bash
POST /extract-text
Content-Type: multipart/form-data
```

**Request:**
- Field: `image` (file)
- Optional: `max_length` (form field, default: 512)

**Example with curl:**
```bash
curl -X POST -F "image=@./image_sample/imagetest-5.png" -F "max_length=1024" http://localhost:5000/extract-text
```

**Response:**
```json
{
  "success": true,
  "data": {
    "extracted_text": "Sample text extracted from image",
    "text_length": 32,
    "model_used": "microsoft/trocr-base-printed",
    "filename": "imagetest-5.png"
  }
}
```

#### 6. Base64 Image Text Extraction
```bash
POST /extract-text-base64
Content-Type: application/json
```

**Request:**
```json
{
  "image_base64": "base64_encoded_image_data",
  "max_length": 1024
}
```

**Example with Python:**
```python
import requests
import base64

with open('text_image.png', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

response = requests.post('http://localhost:5000/extract-text-base64', 
                        json={
                            "image_base64": image_data,
                            "max_length": 1024
                        })
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "data": {
    "extracted_text": "Sample text extracted from image",
    "text_length": 32,
    "model_used": "microsoft/trocr-base-printed"
  }
}
```

#### 7. Batch Text Extraction
```bash
POST /batch-extract-text
Content-Type: multipart/form-data
```

**Request:**
- Field: `images` (multiple files)
- Optional: `max_length` (form field, default: 512)

**Example with curl:**
```bash
curl -X POST \
  -F "images=@./image1.png" \
  -F "images=@./image2.jpg" \
  -F "max_length=1024" \
  http://localhost:5000/batch-extract-text
```

**Response:**
```json
{
  "success": true,
  "total_files": 2,
  "results": [
    {
      "index": 0,
      "filename": "image1.png",
      "extracted_text": "Text from first image",
      "text_length": 22,
      "model_used": "microsoft/trocr-base-printed",
      "success": true
    },
    {
      "index": 1,
      "filename": "image2.jpg",
      "extracted_text": "Text from second image",
      "text_length": 23,
      "model_used": "microsoft/trocr-base-printed",
      "success": true
    }
  ]
}
```

#### 8. ID Card Detection and Data Extraction (File Upload)
```bash
POST /id-card/detect-and-extract
Content-Type: multipart/form-data
```

**Request:**
- Field: `image` (file)
- Optional: `extract_data` (form field, default: true)

**Example with curl:**
```bash
curl -X POST -F "image=@./id_card.jpg" -F "extract_data=true" http://localhost:5000/id-card/detect-and-extract
```

**Response:**
```json
{
  "success": true,
  "data": {
    "card_detected": true,
    "bbox": [45, 67, 557, 391],
    "extracted_data": {
      "id_number": "1234567890123456",
      "name": "JOHN DOE",
      "place_of_birth": "JAKARTA",
      "date_of_birth": "01-01-1990",
      "gender": "LAKI-LAKI",
      "address": "JL. EXAMPLE NO. 123, RT 001/RW 002, KEL. EXAMPLE, KEC. EXAMPLE",
      "religion": "ISLAM",
      "marital_status": "KAWIN",
      "occupation": "ENGINEER",
      "nationality": "WNI",
      "valid_until": "SEUMUR HIDUP",
      "raw_text": ["REPUBLIK INDONESIA", "KARTU TANDA PENDUDUK", "1234567890123456", ...]
    },
    "raw_ocr_results": [
      {
        "text": "REPUBLIK INDONESIA",
        "confidence": 0.98,
        "bbox": [[100, 50], [300, 50], [300, 70], [100, 70]],
        "center": [200, 60]
      }
    ],
    "confidence_scores": [0.98, 0.95, 0.92],
    "avg_confidence": 0.95,
    "image_path": "uploads/temp_12345.jpg"
  }
}
```

#### 9. Base64 ID Card Processing
```bash
POST /id-card/detect-and-extract-base64
Content-Type: application/json
```

**Request:**
```json
{
  "image_base64": "base64_encoded_image_data",
  "extract_data": true
}
```

**Example with Python:**
```python
import requests
import base64

with open('id_card.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

response = requests.post('http://localhost:5000/id-card/detect-and-extract-base64', 
                        json={
                            "image_base64": image_data,
                            "extract_data": True
                        })
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "data": {
    "card_detected": true,
    "bbox": [45, 67, 557, 391],
    "extracted_data": {
      "id_number": "1234567890123456",
      "name": "JOHN DOE",
      "place_of_birth": "JAKARTA",
      "date_of_birth": "01-01-1990",
      "gender": "LAKI-LAKI",
      "address": "JL. EXAMPLE NO. 123, RT 001/RW 002",
      "religion": "ISLAM",
      "marital_status": "KAWIN",
      "occupation": "ENGINEER",
      "nationality": "WNI",
      "valid_until": "SEUMUR HIDUP",
      "raw_text": ["REPUBLIK INDONESIA", "KARTU TANDA PENDUDUK", ...]
    },
    "raw_ocr_results": [...],
    "confidence_scores": [0.98, 0.95, 0.92],
    "avg_confidence": 0.95
  }
}
```

#### 10. ID Card Service Information
```bash
GET /id-card/info
```

**Response:**
```json
{
  "success": true,
  "service_info": {
    "name": "ID Card Detection and Data Extraction",
    "version": "1.0.0",
    "models": {
      "card_detector": "YOLOv8n",
      "ocr_engine": "PaddleOCR",
      "layout_analyzer": "LayoutLM"
    },
    "capabilities": [
      "ID card detection",
      "Personal data extraction",
      "Multi-language OCR support",
      "Layout analysis",
      "Field validation"
    ],
    "supported_id_types": [
      "Indonesian KTP",
      "General ID cards"
    ],
    "supported_fields": [
      "id_number", "name", "place_of_birth", "date_of_birth",
      "gender", "address", "religion", "marital_status",
      "occupation", "nationality", "valid_until"
    ]
  }
}
```

#### 11. Model Information
```bash
GET /model-info
```

**Response:**
```json
{
  "success": true,
  "models": {
    "nsfw_service": {
      "model_name": "Falconsai/nsfw_image_detection",
      "threshold": 0.5,
      "loaded": true
    },
    "ocr_service": {
      "model_name": "Salesforce/blip-image-captioning-base",
      "device": "cuda",
      "model_loaded": true,
      "gpu_available": true,
      "using_blip": true
    },
    "id_card_service": {
      "card_detector": "YOLOv8n",
      "ocr_engine": "PaddleOCR",
      "layout_analyzer": "LayoutLM",
      "device": "cuda",
      "gpu_available": true
    }
  }
}
```

## API Endpoints Summary

### General Endpoints
- `GET /` - API information and available services
- `GET /health` - Health check and service status
- `GET /model-info` - Get information about loaded models

### NSFW Detection Endpoints (`/nsfw/*`)
- `POST /nsfw/detect` - Single image NSFW detection (file upload)
- `POST /nsfw/detect-base64` - Single image NSFW detection (base64)
- `POST /nsfw/batch-detect` - Batch NSFW detection (multiple files)
- `GET /nsfw/info` - NSFW service information

### Text Extraction (OCR) Endpoints (`/ocr/*`)
- `POST /ocr/extract-text` - Single image text extraction (file upload)
- `POST /ocr/extract-text-base64` - Single image text extraction (base64)
- `POST /ocr/batch-extract-text` - Batch text extraction (multiple files)
- `GET /ocr/info` - OCR service information

### ID Card Processing Endpoints (`/id-card/*`)
- `POST /id-card/detect-and-extract` - ID card detection and data extraction (file upload)
- `POST /id-card/detect-and-extract-base64` - ID card processing (base64)
- `GET /id-card/info` - ID card service information

### Legacy Endpoints (Redirects)
The old endpoints (`/detect-nsfw`, `/extract-text`, etc.) now redirect to the new structure with helpful error messages.

## Quick Start Examples

### Python Example - NSFW Detection
```python
import requests

# Upload file for NSFW detection
with open('image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/nsfw/detect',
        files={'image': f}
    )
    print(response.json())
```

### Python Example - Text Extraction
```python
import requests

# Upload file for text extraction
with open('document.png', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/ocr/extract-text',
        files={'image': f},
        data={'max_length': 1024}
    )
    print(response.json())
```

### Python Example - ID Card Processing
```python
import requests

# Upload ID card for detection and data extraction
with open('id_card.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/id-card/detect-and-extract',
        files={'image': f},
        data={'extract_data': True}
    )
    result = response.json()
    print("ID Card Data:", result['data']['extracted_data'])
```

### cURL Example - Base64 Image
```bash
# Convert image to base64
IMAGE_B64=$(base64 -w 0 image.jpg)

# Send for NSFW detection
curl -X POST http://localhost:5000/nsfw/detect-base64 \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\":\"$IMAGE_B64\"}"

# Send for text extraction
curl -X POST http://localhost:5000/ocr/extract-text-base64 \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\":\"$IMAGE_B64\", \"max_length\":1024}"
```

### cURL Example - ID Card Base64
```bash
# Convert ID card image to base64
ID_CARD_B64=$(base64 -w 0 id_card.jpg)

# Send for processing
curl -X POST http://localhost:5000/id-card/detect-and-extract-base64 \
  -H "Content-Type: application/json" \
  -d "{\"image_base64\":\"$ID_CARD_B64\", \"extract_data\":true}"
```

## Testing

Run the test clients to verify all endpoints:

**Test NSFW Detection:**
```bash
python test_api.py
```

**Test Text Extraction (OCR):**
```bash
python test_ocr_api.py
```

**Test ID Card Processing:**
```bash
python test_id_card_api.py
```

**Run Interactive Demo:**
```bash
python demo.py
```

## Configuration

- **Maximum file size**: 16MB
- **Supported formats**: PNG, JPG, JPEG, GIF, BMP, WEBP
- **Default threshold**: 0.5 (50% confidence)
- **Host**: 0.0.0.0 (accessible from all interfaces)
- **Port**: 5000

## Error Responses

The API returns structured error responses:

```json
{
  "error": "Error description",
  "success": false
}
```

Common error codes:
- `400`: Bad Request (invalid input)
- `404`: Not Found (invalid endpoint)
- `405`: Method Not Allowed
- `413`: File Too Large
- `500`: Internal Server Error
- `503`: Service Unavailable (model not loaded)

## Model Information

**NSFW Detection:**
- **Model**: `Falconsai/nsfw_image_detection`
- **Framework**: Transformers pipeline
- **Task**: Image classification
- **Labels**: "safe", "nsfw"

**Text Extraction (OCR):**
- **Primary Model**: `Salesforce/blip-image-captioning-base` (BLIP)
- **Fallback Model**: `microsoft/trocr-base-printed` (TrOCR)
- **Framework**: Transformers pipeline
- **Task**: Optical Character Recognition (OCR)
- **GPU Support**: Automatic detection and usage

**ID Card Processing:**
- **Detection Model**: `YOLOv8n` (fine-tunable for ID cards)
- **OCR Engine**: `PaddleOCR` (multi-language support)
- **Layout Analysis**: `LayoutLM` (document structure understanding)
- **Framework**: Ultralytics + PaddlePaddle + Transformers
- **Task**: Object detection + OCR + data extraction
- **Supported Languages**: Indonesian, English, and 80+ others
- **GPU Support**: Automatic detection and usage

## Supported ID Card Fields

The ID card service can extract the following fields from Indonesian KTP:

- **Personal Information:**
  - ID Number (NIK) - 16 digits
  - Full Name (Nama)
  - Place of Birth (Tempat Lahir)
  - Date of Birth (Tanggal Lahir)
  - Gender (Jenis Kelamin)
  - Address (Alamat)
  - Religion (Agama)
  - Marital Status (Status Perkawinan)
  - Occupation (Pekerjaan)
  - Nationality (Kewarganegaraan)
  - Valid Until (Berlaku Hingga)

**Note:** Field extraction accuracy depends on image quality and card condition.

## Development

### Adding New Features

1. Add service logic to `services/` directory (e.g., `new_service.py`)
2. Add API endpoints to `app.py`
3. Update tests in `test_api.py` or create new test files
4. Update this README

### Environment Variables

You can configure the API using environment variables:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## License

This project is for educational purposes.
