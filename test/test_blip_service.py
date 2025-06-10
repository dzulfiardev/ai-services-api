#!/usr/bin/env python3
"""
Test script for BLIP-based Image to Text Service
"""

import sys
import os
# Add parent directory to path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_to_text_service import ImageToTextService
from PIL import Image
import requests

def test_blip_service():
    """Test the BLIP image-to-text service locally"""
    print("🧪 Testing BLIP Image-to-Text Service")
    print("=" * 50)
    
    try:
        # Initialize the service
        print("Initializing BLIP service...")
        service = ImageToTextService()
        print(f"✅ Service initialized successfully")
        
        # Get model info
        info = service.get_model_info()
        print(f"\n📊 Model Information:")
        print(f"   Model: {info['model_name']}")
        print(f"   Device: {info['device']}")
        print(f"   GPU Available: {info['gpu_available']}")
        print(f"   Using BLIP: {info['using_blip']}")
        print(f"   Using Fallback: {info.get('using_pipeline_fallback', False)}")
        
        # Test with sample image
        image_path = "../image_sample/imagetest-5.png"
        if os.path.exists(image_path):
            print(f"\n🖼️  Testing with image: {image_path}")
            result = service.extract_text_from_image(image_path, max_length=100)
            
            print(f"✅ Processing successful!")
            print(f"   Extracted text: '{result['extracted_text']}'")
            print(f"   Text length: {result['text_length']} characters")
            print(f"   Model used: {result['model_used']}")
        else:
            print(f"⚠️  Sample image not found: {image_path}")
            
    except Exception as e:
        print(f"❌ Error testing service: {e}")
        import traceback
        traceback.print_exc()

def test_api_endpoints():
    """Test the API endpoints with BLIP model"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy")
            print(f"   OCR Service loaded: {data.get('services', {}).get('image_to_text', {}).get('loaded', False)}")
        else:
            print(f"❌ API unhealthy (Status: {response.status_code})")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API - make sure server is running")
        return
    
    # Test model info endpoint
    try:
        response = requests.get(f"{base_url}/model-info")
        if response.status_code == 200:
            data = response.json()
            ocr_info = data.get('models', {}).get('ocr_service', {})
            print("📊 OCR Service Info:")
            print(f"   Model: {ocr_info.get('model_name', 'Unknown')}")
            print(f"   Using BLIP: {ocr_info.get('using_blip', False)}")
        else:
            print(f"❌ Failed to get model info (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error getting model info: {e}")
    
    # Test OCR endpoint
    image_path = "../image_sample/imagetest-5.png"
    if os.path.exists(image_path):
        try:
            with open(image_path, 'rb') as f:
                files = {'image': f}
                data = {'max_length': 100}
                response = requests.post(f"{base_url}/ocr/extract-text", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result['data']
                    print("🖼️  OCR Test Results:")
                    print(f"   Extracted: '{data['extracted_text']}'")
                    print(f"   Length: {data['text_length']} chars")
                    print(f"   Model: {data['model_used']}")
                else:
                    print(f"❌ OCR failed: {result.get('error')}")
            else:
                print(f"❌ OCR request failed (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error testing OCR: {e}")

def main():
    """Main test function"""
    print("🚀 BLIP Image-to-Text Service Tests")
    print("=" * 60)
    
    # Test 1: Local service test
    test_blip_service()
    
    # Test 2: API endpoints test
    test_api_endpoints()
    
    print("\n✅ Testing completed!")
    print("\n💡 Usage Tips:")
    print("   • BLIP is better for general image captioning")
    print("   • For ID cards, consider using EasyOCR (dedicated OCR)")
    print("   • For printed text, TrOCR might be more accurate")
    print("   • BLIP works well for natural scene descriptions")

if __name__ == "__main__":
    main()
