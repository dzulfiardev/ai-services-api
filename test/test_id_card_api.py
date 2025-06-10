#!/usr/bin/env python3
"""
Test script for ID Card API endpoints
"""

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

def test_id_card_info():
    """Test ID card service info endpoint"""
    print("Testing ID card service info...")
    response = requests.get(f"{API_URL}/id-card/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_id_card_detect_and_extract(image_path):
    """Test ID card detection and extraction with file upload"""
    print(f"Testing ID card detection and extraction: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'extract_data': 'true'}
            response = requests.post(f"{API_URL}/id-card/detect-and-extract", 
                                   files=files, data=data)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"Card detected: {data.get('card_detected', False)}")
            print(f"Bounding box: {data.get('bbox', 'None')}")
            print(f"Average confidence: {data.get('avg_confidence', 0):.2f}")
            
            extracted_data = data.get('extracted_data', {})
            print("Extracted data:")
            for field, value in extracted_data.items():
                if field != 'raw_text' and value:
                    print(f"  {field}: {value}")
            
            raw_text = extracted_data.get('raw_text', [])
            if raw_text:
                print(f"Raw text ({len(raw_text)} items): {raw_text[:5]}...")  # Show first 5 items
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except FileNotFoundError:
        print(f"Error: File not found - {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

def test_id_card_detect_and_extract_base64(image_path):
    """Test ID card detection and extraction with base64 image"""
    print(f"Testing ID card detection and extraction (base64): {image_path}")
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            "image_base64": image_data,
            "extract_data": True
        }
        
        response = requests.post(f"{API_URL}/id-card/detect-and-extract-base64", 
                               json=payload)
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        
        if result.get('success'):
            data = result.get('data', {})
            print(f"Card detected: {data.get('card_detected', False)}")
            print(f"Bounding box: {data.get('bbox', 'None')}")
            print(f"Average confidence: {data.get('avg_confidence', 0):.2f}")
            
            extracted_data = data.get('extracted_data', {})
            print("Extracted data:")
            for field, value in extracted_data.items():
                if field != 'raw_text' and value:
                    print(f"  {field}: {value}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except FileNotFoundError:
        print(f"Error: File not found - {image_path}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

def test_model_info():
    """Test model information endpoint"""
    print("Testing model info...")
    response = requests.get(f"{API_URL}/model-info")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}")
    print("-" * 50)

if __name__ == "__main__":
    print("ID Card API Test Client")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test model info
    test_model_info()
    
    # Test ID card service info
    test_id_card_info()
    
    # Test ID card detection and extraction
    test_id_card_detect_and_extract("../image_sample/imagetest-5.png")
    
    # Test base64 ID card detection and extraction
    test_id_card_detect_and_extract_base64("../image_sample/imagetest-5.png")
    
    print("Testing completed!")
