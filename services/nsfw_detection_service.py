from PIL import Image
from transformers import pipeline
import os

class NSFWDetectionService:
    def __init__(self, model_name="Falconsai/nsfw_image_detection", threshold=0.5):
        """
        Initialize the NSFW Detection Service
        
        Args:
            model_name (str): The model to use for detection
            threshold (float): Confidence threshold for NSFW detection
        """
        self.model_name = model_name
        self.threshold = threshold
        self.classifier = None
        self._load_model()
    
    def _load_model(self):
        """Load the classification model"""
        try:
            self.classifier = pipeline(
                "image-classification", 
                model=self.model_name, 
                use_fast=True
            )
            print(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise
    
    def detect_nsfw(self, image_path):
        """
        Detect if an image contains NSFW content
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            dict: Detection results with classification and confidence
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if self.classifier is None:
            raise RuntimeError("Model not loaded properly")
        
        try:
            # Open and process the image
            img = Image.open(image_path)
            result = self.classifier(img)
            
            # Check for NSFW content
            nsfw_labels = [label for label in result if label["label"].lower() == "nsfw"]
            is_nsfw = any(label["score"] > self.threshold for label in nsfw_labels)
            confidence = max([label["score"] for label in nsfw_labels], default=0.0)
            
            return {
                "image_path": image_path,
                "is_nsfw": is_nsfw,
                "confidence": round(confidence, 4),
                "threshold": self.threshold,
                "all_predictions": result
            }
            
        except Exception as e:
            raise Exception(f"Error processing image {image_path}: {e}")
    
    def detect_nsfw_from_pil_image(self, pil_image):
        """
        Detect NSFW content from PIL Image object
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            dict: Detection results
        """
        if self.classifier is None:
            raise RuntimeError("Model not loaded properly")
        
        try:
            result = self.classifier(pil_image)
            
            # Check for NSFW content
            nsfw_labels = [label for label in result if label["label"].lower() == "nsfw"]
            is_nsfw = any(label["score"] > self.threshold for label in nsfw_labels)
            confidence = max([label["score"] for label in nsfw_labels], default=0.0)
            
            return {
                "is_nsfw": is_nsfw,
                "confidence": round(confidence, 4),
                "threshold": self.threshold,
                "all_predictions": result
            }
            
        except Exception as e:
            raise Exception(f"Error processing image: {e}")
    
    def batch_detect(self, image_paths):
        """
        Detect NSFW content in multiple images
        
        Args:
            image_paths (list): List of image file paths
            
        Returns:
            list: List of detection results for each image
        """
        results = []
        for path in image_paths:
            try:
                result = self.detect_nsfw(path)
                results.append(result)
            except Exception as e:
                print(f"Failed to process {path}: {e}")
                results.append({
                    "image_path": path,
                    "error": str(e)
                })
        return results
