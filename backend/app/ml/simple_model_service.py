"""
Minimal Model Service for testing core functionality
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class SimpleModelService:
    """Simplified model service for testing"""
    
    def __init__(self):
        self.model_loaded = False
        self.class_names = ['NORMAL', 'PNEUMONIA']
        
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model_loaded
    
    def load_model(self) -> bool:
        """Load model (simplified)"""
        try:
            # For now, just simulate loading
            model_path = "/Users/bnutfilloyev/Developer/Freelance/pneumonia-app/backend/model/pneumonia_model.onnx"
            
            if os.path.exists(model_path):
                self.model_loaded = True
                logger.info("✅ Model loaded successfully (simulated)")
                return True
            else:
                logger.error(f"❌ Model file not found: {model_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def predict_from_image(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        """Predict from PIL Image (simplified)"""
        if not self.is_loaded():
            logger.error("Model not loaded")
            return None
        
        try:
            # Simulate prediction with random values for testing
            import random
            
            # Random prediction for testing
            prediction = random.choice(self.class_names)
            confidence = random.uniform(0.6, 0.95)
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'probabilities': {
                    'NORMAL': 1 - confidence if prediction == 'PNEUMONIA' else confidence,
                    'PNEUMONIA': confidence if prediction == 'PNEUMONIA' else 1 - confidence
                },
                'inference_time': 0.1,
                'image_size': image.size,
                'mode': 'simulated'
            }
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None
