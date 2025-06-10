#!/usr/bin/env python3
"""
AI Services API Demo Script
Demonstrates both NSFW detection and text extraction capabilities
"""

import requests
import base64
import json
import time

# API Configuration
API_URL = "http://localhost:5000"

def check_api_health():
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy!")
            print(f"   Service: {data.get('service', 'Unknown')}")
            print(f"   NSFW Model: {'✅' if data.get('nsfw_model_loaded') else '❌'}")
            print(f"   OCR Model: {'✅' if data.get('ocr_model_loaded') else '❌'}")
            return True
        else:
            print(f"❌ API unhealthy (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def demo_nsfw_detection(image_path):
    """Demonstrate NSFW detection"""
    print(f"\n🔍 Testing NSFW Detection with: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            response = requests.post(f"{API_URL}/nsfw/detect", files={'image': f})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"   Result: {'🔞 NSFW' if result['is_nsfw'] else '✅ Safe'}")
                print(f"   Confidence: {result['confidence']:.3f}")
                print(f"   Threshold: {result['threshold']}")
            else:
                print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except FileNotFoundError:
        print(f"   ❌ File not found: {image_path}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def demo_text_extraction(image_path):
    """Demonstrate text extraction"""
    print(f"\n📄 Testing Text Extraction with: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            response = requests.post(
                f"{API_URL}/ocr/extract-text", 
                files={'image': f},
                data={'max_length': 1024}
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                text = result['extracted_text']
                if text.strip():
                    print(f"   ✅ Text found ({result['text_length']} chars)")
                    print(f"   Text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
                else:
                    print("   ℹ️  No text detected in image")
                print(f"   Model: {result['model_used']}")
            else:
                print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except FileNotFoundError:
        print(f"   ❌ File not found: {image_path}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def demo_base64_processing(image_path):
    """Demonstrate base64 image processing"""
    print(f"\n🔄 Testing Base64 Processing with: {image_path}")
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Test NSFW detection with base64
        nsfw_payload = {"image_base64": image_data}
        response = requests.post(f"{API_URL}/nsfw/detect-base64", json=nsfw_payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                print(f"   NSFW: {'🔞' if result['is_nsfw'] else '✅'} (confidence: {result['confidence']:.3f})")
            else:
                print(f"   ❌ NSFW Error: {data.get('error')}")
        
        # Test text extraction with base64
        ocr_payload = {"image_base64": image_data, "max_length": 512}
        response = requests.post(f"{API_URL}/ocr/extract-text-base64", json=ocr_payload)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data['data']
                text = result['extracted_text']
                print(f"   OCR: {'✅' if text.strip() else 'ℹ️'} ({result['text_length']} chars)")
                if text.strip():
                    print(f"        '{text[:50]}{'...' if len(text) > 50 else ''}'")
            else:
                print(f"   ❌ OCR Error: {data.get('error')}")
                
    except FileNotFoundError:
        print(f"   ❌ File not found: {image_path}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def get_model_info():
    """Get information about loaded models"""
    print("\n🤖 Model Information:")
    try:
        response = requests.get(f"{API_URL}/model-info")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                models = data['models']
                
                if models.get('nsfw_service'):
                    nsfw = models['nsfw_service']
                    print(f"   NSFW: {nsfw['model_name']} (threshold: {nsfw['threshold']})")
                
                if models.get('ocr_service'):
                    ocr = models['ocr_service']
                    print(f"   OCR: {ocr['model_name']} (device: {ocr['device']})")
                    print(f"        GPU Available: {'✅' if ocr['gpu_available'] else '❌'}")
                    print(f"        Using TrOCR: {'✅' if ocr['using_trocr'] else '❌'}")
            else:
                print(f"   ❌ Error: {data.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main demo function"""
    print("🚀 AI Services API Demo")
    print("=" * 50)
    
    # Check API health
    if not check_api_health():
        print("\n❌ Cannot proceed - API is not available")
        print("Please make sure the API is running with: python app.py")
        return
    
    # Get model information
    get_model_info()
    
    # Test with sample image
    sample_image = "./image_sample/imagetest-5.png"
    
    # Demo NSFW detection
    demo_nsfw_detection(sample_image)
    
    # Demo text extraction
    demo_text_extraction(sample_image)
    
    # Demo base64 processing
    demo_base64_processing(sample_image)
    
    print("\n✅ Demo completed!")
    print("\nAPI Endpoints Summary (New Structure):")
    print("  • General: /, /health, /model-info")
    print("  • NSFW Detection: /nsfw/detect, /nsfw/detect-base64, /nsfw/batch-detect, /nsfw/info")
    print("  • Text Extraction: /ocr/extract-text, /ocr/extract-text-base64, /ocr/batch-extract-text, /ocr/info")

if __name__ == "__main__":
    main()
