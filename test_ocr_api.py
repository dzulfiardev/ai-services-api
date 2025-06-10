import requests
import base64
import json

# API base URL
API_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_extract_text(image_path):
    """Test text extraction from uploaded image"""
    print(f"Testing text extraction: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_URL}/ocr/extract-text", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_extract_text_base64(image_path):
    """Test text extraction from base64 encoded image"""
    print(f"Testing base64 text extraction: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        payload = {
            "image_base64": image_data,
            "max_length": 1024
        }
        response = requests.post(f"{API_URL}/ocr/extract-text-base64", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_batch_extract_text(image_paths):
    """Test batch text extraction from multiple images"""
    print(f"Testing batch text extraction: {image_paths}")
    try:
        files = []
        for path in image_paths:
            try:
                files.append(('images', open(path, 'rb')))
            except FileNotFoundError:
                print(f"File not found: {path}")
        
        if files:
            # Add max_length parameter
            data = {'max_length': 1024}
            response = requests.post(f"{API_URL}/ocr/batch-extract-text", files=files, data=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # Close file handles
            for _, file_handle in files:
                file_handle.close()
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_ocr_info():
    """Test OCR service info endpoint"""
    print("Testing OCR service info...")
    response = requests.get(f"{API_URL}/ocr/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_model_info():
    """Test model information endpoint"""
    print("Testing model info...")
    response = requests.get(f"{API_URL}/model-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

if __name__ == "__main__":
    print("Image to Text API Test Client (New Structure)")
    print("=" * 60)
    
    # Test health check
    test_health_check()
    
    # Test model info
    test_model_info()
    
    # Test OCR service info
    test_ocr_info()
    
    # Test single image text extraction
    test_extract_text("./image_sample/imagetest-5.png")
    
    # Test base64 image text extraction
    test_extract_text_base64("./image_sample/imagetest-5.png")
    
    # Test batch text extraction
    test_batch_extract_text([
        "./image_sample/imagetest-5.png"
    ])
    
    print("Text extraction testing completed!")
