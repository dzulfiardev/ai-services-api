# NSFW Detection REST API

A Flask-based REST API service for detecting NSFW (Not Safe For Work) content in images using machine learning.

## Features

- **Single Image Detection**: Upload an image file for NSFW detection
- **Base64 Image Support**: Send base64 encoded images
- **Batch Processing**: Process multiple images at once
- **Health Check**: Monitor API status
- **Error Handling**: Comprehensive error responses
- **File Validation**: Support for common image formats (PNG, JPG, JPEG, GIF, BMP, WEBP)

## Project Structure

```
dzul-ai-project/
├── app.py                          # Main Flask application
├── services/
│   ├── __init__.py
│   └── nsfw_detection_service.py   # NSFW detection service
├── test_api.py                     # API test client
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
  "service": "NSFW Detection API",
  "model_loaded": true,
  "version": "1.0.0"
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

## Testing

Run the test client to verify all endpoints:

```bash
python test_api.py
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

- **Model**: `Falconsai/nsfw_image_detection`
- **Framework**: Transformers pipeline
- **Task**: Image classification
- **Labels**: "safe", "nsfw"

## Development

### Adding New Features

1. Add service logic to `services/nsfw_detection_service.py`
2. Add API endpoints to `app.py`
3. Update tests in `test_api.py`
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
