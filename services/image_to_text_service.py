from PIL import Image
from transformers import pipeline, BlipProcessor, BlipForConditionalGeneration
import os
import torch

class ImageToTextService:
    def __init__(self, model_name="Salesforce/blip-image-captioning-base", use_gpu=True):
        """
        Initialize the Image to Text Service using BLIP model
        
        Args:
            model_name (str): The model to use for image-to-text (default: BLIP)
            use_gpu (bool): Whether to use GPU if available
        """
        self.model_name = model_name
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.processor = None
        self.model = None
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        """Load the BLIP model and processor"""
        try:
            # Load BLIP model for image captioning and text extraction
            self.processor = BlipProcessor.from_pretrained(self.model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(self.model_name)
            
            if self.device == "cuda":
                self.model = self.model.to(self.device)
            
            print(f"✅ BLIP Model {self.model_name} loaded successfully on {self.device}")
        except Exception as e:
            print(f"❌ Error loading BLIP model: {e}")
            print("Falling back to general image-to-text pipeline...")
            try:
                # Fallback to transformers pipeline
                self.pipeline = pipeline(
                    "image-to-text",
                    model="nlpconnect/vit-gpt2-image-captioning",
                    device=0 if self.device == "cuda" else -1
                )
                print("✅ Fallback image-to-text pipeline loaded successfully")
            except Exception as e2:
                print(f"❌ Error loading fallback model: {e2}")
                raise
    
    def extract_text_from_image(self, image_path, max_length=512):
        """
        Extract text/caption from an image file using BLIP
        
        Args:
            image_path (str): Path to the image file
            max_length (int): Maximum length of generated text
            
        Returns:
            dict: Extraction results with text and metadata
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if self.model is None and self.pipeline is None:
            raise RuntimeError("Model not loaded properly")
        
        try:
            # Open and process the image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using BLIP if available
            if self.processor is not None and self.model is not None:
                # Process image and generate caption/text
                inputs = self.processor(image, return_tensors="pt")
                
                if self.device == "cuda":
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate text with specified parameters
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=4,
                        early_stopping=True,
                        do_sample=False
                    )
                
                extracted_text = self.processor.decode(generated_ids[0], skip_special_tokens=True)
            else:
                # Use fallback pipeline
                result = self.pipeline(image)
                extracted_text = result[0]['generated_text'] if result else ""

            return {
                "image_path": image_path,
                "extracted_text": extracted_text.strip(),
                "text_length": len(extracted_text.strip()),
                "model_used": self.model_name,
                "success": True
            }
            
        except Exception as e:
            raise Exception(f"Error processing image {image_path}: {e}")
    
    def extract_text_from_pil_image(self, pil_image, max_length=512):
        """
        Extract text from a PIL Image object using BLIP
        
        Args:
            pil_image: PIL Image object
            max_length (int): Maximum length of generated text
            
        Returns:
            dict: Extraction results
        """
        if self.model is None and self.pipeline is None:
            raise RuntimeError("Model not loaded properly")
        
        try:
            # Convert to RGB if needed
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Extract text using BLIP if available
            if self.processor is not None and self.model is not None:
                # Process image and generate caption/text
                inputs = self.processor(pil_image, return_tensors="pt")
                
                if self.device == "cuda":
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate text with specified parameters
                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **inputs,
                        max_length=max_length,
                        num_beams=4,
                        early_stopping=True,
                        do_sample=False
                    )
                
                extracted_text = self.processor.decode(generated_ids[0], skip_special_tokens=True)
            else:
                # Use fallback pipeline
                result = self.pipeline(pil_image)
                extracted_text = result[0]['generated_text'] if result else ""
            
            return {
                "extracted_text": extracted_text.strip(),
                "text_length": len(extracted_text.strip()),
                "model_used": self.model_name,
                "success": True
            }
            
        except Exception as e:
            raise Exception(f"Error processing image: {e}")
    
    def batch_extract_text(self, image_paths, max_length=512):
        """
        Extract text from multiple images
        
        Args:
            image_paths (list): List of image file paths
            max_length (int): Maximum length of generated text
            
        Returns:
            list: List of extraction results for each image
        """
        results = []
        for path in image_paths:
            try:
                result = self.extract_text_from_image(path, max_length)
                results.append(result)
            except Exception as e:
                print(f"Failed to process {path}: {e}")
                results.append({
                    "image_path": path,
                    "error": str(e),
                    "success": False
                })
        return results
    
    def get_model_info(self):
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "model_loaded": self.model is not None or self.pipeline is not None,
            "gpu_available": torch.cuda.is_available(),
            "using_blip": self.processor is not None and self.model is not None,
            "using_pipeline_fallback": self.pipeline is not None
        }
