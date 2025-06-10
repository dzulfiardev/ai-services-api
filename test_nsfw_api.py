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

def test_root_endpoint():
    """Test the root endpoint"""
    print("Testing root endpoint...")
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_nsfw_detect(image_path):
    """Test NSFW detection with uploaded image"""
    print(f"Testing NSFW detection: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{API_URL}/nsfw/detect", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_nsfw_detect_base64(image_path):
    """Test NSFW detection with base64 encoded image"""
    print(f"Testing NSFW detection (base64): {image_path}")
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        payload = {"image_base64": image_data}
        response = requests.post(f"{API_URL}/nsfw/detect-base64", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"File not found: {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_nsfw_batch_detect(image_paths):
    """Test batch NSFW detection with multiple images"""
    print(f"Testing batch NSFW detection: {image_paths}")
    try:
        files = []
        for path in image_paths:
            try:
                files.append(('images', open(path, 'rb')))
            except FileNotFoundError:
                print(f"File not found: {path}")
        
        if files:
            response = requests.post(f"{API_URL}/nsfw/batch-detect", files=files)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # Close file handles
            for _, file_handle in files:
                file_handle.close()
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 50)

def test_nsfw_info():
    """Test NSFW service info endpoint"""
    print("Testing NSFW service info...")
    response = requests.get(f"{API_URL}/nsfw/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)

def test_legacy_endpoints():
    """Test legacy endpoint redirects"""
    print("Testing legacy endpoint redirects...")
    
    # Test legacy NSFW endpoint
    try:
        response = requests.post(f"{API_URL}/detect-nsfw", files={})
        print(f"Legacy /detect-nsfw - Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing legacy endpoint: {e}")
    print("-" * 50)

if __name__ == "__main__":
    print("NSFW Detection API Test Client (New Structure)")
    print("=" * 60)
    
    # Test general endpoints
    test_root_endpoint()
    test_health_check()
    test_nsfw_info()
    
    # Test NSFW detection endpoints
    test_nsfw_detect("./image_sample/imagetest-5.png")
    test_nsfw_detect_base64("./image_sample/imagetest-5.png")
    test_nsfw_batch_detect(["./image_sample/imagetest-5.png"])
    
    # Test legacy endpoints
    test_legacy_endpoints()
    
    print("NSFW API testing completed!")
