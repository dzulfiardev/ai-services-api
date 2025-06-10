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

def test_upload_image(image_path):
    """Test uploading an image file"""
    print(f"Testing image upload: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_URL}/detect-nsfw", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_base64_image(image_path):
    """Test base64 encoded image"""
    print(f"Testing base64 image: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        payload = {"image_base64": image_data}
        response = requests.post(f"{API_URL}/detect-nsfw-base64", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_batch_upload(image_paths):
    """Test batch upload of multiple images"""
    print(f"Testing batch upload: {image_paths}")
    try:
        files = []
        for path in image_paths:
            try:
                files.append(('images', open(path, 'rb')))
            except FileNotFoundError:
                print(f"File not found: {path}")
        
        if files:
            response = requests.post(f"{API_URL}/batch-detect-nsfw", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # Close file handles
            for _, file_handle in files:
                file_handle.close()
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

if __name__ == "__main__":
    print("NSFW Detection API Test Client")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test single image upload
    test_upload_image("./image_sample/imagetest-5.png")
    
    # Test base64 image
    test_base64_image("./image_sample/imagetest-5.png")
    
    # Test batch upload
    test_batch_upload([
        "./image_sample/imagetest-5.png",
        "./image_generation/image_0a7c4312-5a20-40ba-a50b-37862a67daf5.png"
    ])
    
    print("Testing completed!")
