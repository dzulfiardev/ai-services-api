from PIL import Image, ImageDraw
import torch
import cv2
import numpy as np
import re
import os
from typing import Dict, List, Tuple, Optional

class IDCardService:
    def __init__(self, use_gpu=True):
        """
        Initialize ID Card Detection and Extraction Service
        
        Args:
            use_gpu (bool): Whether to use GPU if available
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        self.card_detector = None
        self.ocr_engine = None
        self.layout_analyzer = None
        self._load_models()
    
    def _load_models(self):
        """Load all required models for ID card processing"""
        print("Loading ID Card processing models...")
        
        # 1. Load YOLOv8 for card detection
        try:
            from ultralytics import YOLO
            self.card_detector = YOLO('yolov8n.pt')  # You can fine-tune this for ID cards
            print("✅ YOLO card detector loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load YOLO detector: {e}")
        
        # 2. Load PaddleOCR for text extraction
        try:
            from paddleocr import PaddleOCR
            self.ocr_engine = PaddleOCR(
                use_angle_cls=True, 
                lang='en',  # Can support multiple languages
                use_gpu=self.device == "cuda",
                show_log=True
            )
            print("✅ PaddleOCR engine loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load PaddleOCR: {e}")
            # Fallback to EasyOCR
            try:
                import easyocr
                self.ocr_engine = easyocr.Reader(['en', 'id'], gpu=self.device == "cuda")
                print("✅ EasyOCR fallback loaded successfully")
            except Exception as e2:
                print(f"❌ Failed to load EasyOCR fallback: {e2}")
        
        # 3. Load LayoutLM for structured extraction (optional)
        try:
            from transformers import AutoTokenizer, AutoModel
            self.layout_tokenizer = AutoTokenizer.from_pretrained("microsoft/layoutlm-base-uncased")
            self.layout_model = AutoModel.from_pretrained("microsoft/layoutlm-base-uncased")
            if self.device == "cuda":
                self.layout_model = self.layout_model.to(self.device)
            print("✅ LayoutLM model loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load LayoutLM: {e}")
            self.layout_model = None
    
    def detect_id_card(self, image_path: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect ID card in image and return bounding box
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            Tuple[int, int, int, int]: Bounding box coordinates (x1, y1, x2, y2)
        """
        if not self.card_detector:
            return None
        
        try:
            results = self.card_detector(image_path)
            
            # Process YOLO results
            for result in results:
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    # Get the largest detected object (assuming it's the ID card)
                    largest_box = max(boxes.xyxy.cpu().numpy(), key=lambda x: (x[2]-x[0])*(x[3]-x[1]))
                    return tuple(map(int, largest_box))
            
            return None
        except Exception as e:
            print(f"Error in card detection: {e}")
            return None
    
    def crop_id_card(self, image_path: str, bbox: Optional[Tuple] = None) -> Image.Image:
        """
        Crop ID card from image
        
        Args:
            image_path (str): Path to the image
            bbox (Optional[Tuple]): Bounding box coordinates
            
        Returns:
            PIL.Image: Cropped ID card image
        """
        image = Image.open(image_path)
        
        if bbox:
            x1, y1, x2, y2 = bbox
            # Add some padding
            padding = 10
            x1 = max(0, x1 - padding)
            y1 = max(0, y1 - padding)
            x2 = min(image.width, x2 + padding)
            y2 = min(image.height, y2 + padding)
            
            return image.crop((x1, y1, x2, y2))
      
        return image
    
    def extract_text_with_coordinates(self, image: Image.Image, image_path) -> List[Dict]:
        """
        Extract text with coordinates using OCR
        
        Args:
            image (PIL.Image): ID card image
            
        Returns:
            List[Dict]: List of detected text with coordinates and confidence
        """
        if not self.ocr_engine:
            raise RuntimeError("OCR engine not loaded")
        
        # Convert PIL to numpy array for PaddleOCR
        img_array = np.array(image)
        
        # Debug information
        print(f"🔍 DEBUG: img_array shape: {image}")
        print(f"🔍 DEBUG: img_array shape: {img_array.shape}")
        print(f"🔍 DEBUG: img_array dtype: {img_array.dtype}")
        print(f"🔍 DEBUG: img_array min/max: {img_array.min()}/{img_array.max()}")
        print(f"🔍 DEBUG: OCR engine type: {type(self.ocr_engine)}")
        print(f"🔍 DEBUG: OCR engine has 'ocr' method: {hasattr(self.ocr_engine, 'ocr')}")
        
        try:
            if hasattr(self.ocr_engine, 'ocr'):  # PaddleOCR
                results = self.ocr_engine.ocr(img_array, cls=True)

                extracted_data = []
                if results and results[0]:
                    for line in results[0]:
                        bbox, (text, confidence) = line
                        extracted_data.append({
                            "text": text,
                            "confidence": confidence,
                            "bbox": bbox,
                            "center": self._get_bbox_center(bbox)
                        })
                return extracted_data
            
            else:  # EasyOCR
                # results = self.ocr_engine.readtext(img_array)
                results = self.ocr_engine.readtext(image_path)
                # print(f"🔍 DEBUG: EasyOCR: {results}")
                extracted_data = []
                for bbox, text, confidence in results:
                    extracted_data.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox,
                        "center": self._get_bbox_center(bbox)
                    })
                return extracted_data
                
        except Exception as e:
            raise Exception(f"Error in text extraction: {e}")
    
    def _get_bbox_center(self, bbox) -> Tuple[float, float]:
        """Get center point of bounding box"""
        if len(bbox) == 4 and len(bbox[0]) == 2:  # PaddleOCR format
            x_coords = [point[0] for point in bbox]
            y_coords = [point[1] for point in bbox]
        else:  # EasyOCR format
            x_coords = [bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]]
            y_coords = [bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]]
        
        center_x = sum(x_coords) / len(x_coords)
        center_y = sum(y_coords) / len(y_coords)
        return (center_x, center_y)
    
    def parse_id_card_data(self, extracted_text: List[Dict]) -> Dict[str, str]:
        """
        Parse extracted text into structured ID card data
        
        Args:
            extracted_text (List[Dict]): Raw OCR results
            
        Returns:
            Dict[str, str]: Structured ID card data
        """
        id_data = {
            "id_number": "",
            "name": "",
            "place_of_birth": "",
            "date_of_birth": "",
            "gender": "",
            "address": "",
            "religion": "",
            "marital_status": "",
            "occupation": "",
            "nationality": "",
            "valid_until": "",
            "raw_text": []
        }
        
        # Sort text by vertical position (top to bottom)
        sorted_text = sorted(extracted_text, key=lambda x: x["center"][1])
        
        for item in sorted_text:
            text = item["text"].strip()
            id_data["raw_text"].append(text)
            
            # ID Number pattern (Indonesian KTP: 16 digits)
            id_pattern = r'\b\d{16}\b'
            if re.search(id_pattern, text) and not id_data["id_number"]:
                id_data["id_number"] = text
            
            # Name detection (usually after "Nama" or first long text)
            if any(keyword in text.lower() for keyword in ["nama", "name"]) and len(text) > 10:
                id_data["name"] = text.replace("Nama", "").replace("Name", "").strip()
            
            # Date patterns (DD-MM-YYYY or DD/MM/YYYY or DD MM YYYY)
            date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b'
            if re.search(date_pattern, text) and not id_data["date_of_birth"]:
                id_data["date_of_birth"] = text
            
            # Gender detection
            if any(gender in text.lower() for gender in ["laki-laki", "perempuan", "male", "female"]):
                id_data["gender"] = text
            
            # Address detection (usually longer text with location indicators)
            if any(addr_keyword in text.lower() for addr_keyword in ["jl", "jalan", "rt", "rw", "kel", "kec", "JL"]):
                if not id_data["address"]:
                    id_data["address"] = text
                else:
                    id_data["address"] += " " + text
        
        return id_data
    
    def process_id_card(self, image_path: str) -> Dict:
        """
        Complete ID card processing pipeline
        
        Args:
            image_path (str): Path to the image containing ID card
            
        Returns:
            Dict: Complete processing results
        """
        try:
            # Step 1: Detect ID card
            bbox = self.detect_id_card(image_path)
            
            # Step 2: Crop ID card
            cropped_card = self.crop_id_card(image_path, bbox)
            
            # Step 3: Extract text with coordinates
            extracted_text = self.extract_text_with_coordinates(cropped_card, image_path)
            
            # Step 4: Parse structured data
            parsed_data = self.parse_id_card_data(extracted_text)
            
            return {
                "success": True,
                "image_path": image_path,
                "card_detected": bbox is not None,
                "bbox": bbox,
                "extracted_data": parsed_data,
                "raw_ocr_results": extracted_text,
                "confidence_scores": [item["confidence"] for item in extracted_text],
                "avg_confidence": np.mean([item["confidence"] for item in extracted_text]) if extracted_text else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            "card_detector": "YOLOv8" if self.card_detector else "Not loaded",
            "ocr_engine": "PaddleOCR" if hasattr(self.ocr_engine, 'ocr') else "EasyOCR" if self.ocr_engine else "Not loaded",
            "layout_analyzer": "LayoutLM" if self.layout_model else "Not loaded",
            "device": self.device,
            "gpu_available": torch.cuda.is_available()
        }
