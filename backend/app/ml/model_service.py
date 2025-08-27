"""
ONNX Model Service for Pneumonia Detection
"""
import os
import json
import logging
import time
from typing import Dict, Any, Optional, Tuple
import numpy as np
from PIL import Image
import base64
import io

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    ort = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelService:
    """Service for handling ONNX model inference."""
    
    def __init__(self):
        self.session = None
        self.input_name = None
        self.output_name = None
        self.class_names = ['NORMAL', 'PNEUMONIA']
        self.model_config = {}
        self.model_loaded = False
        
    async def load_model(self) -> bool:
        """Load the ONNX model."""
        try:
            if not ONNX_AVAILABLE:
                logger.error("ONNX Runtime not available")
                return False
            
            model_path = settings.onnx_model_path
            config_path = settings.model_config_path
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
            
            # Load model configuration
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.model_config = json.load(f)
                logger.info(f"Loaded model config: {self.model_config}")
            
            # Create ONNX Runtime session
            providers = ['CPUExecutionProvider']
            if ort.get_available_providers():
                available = ort.get_available_providers()
                if 'CUDAExecutionProvider' in available:
                    providers.insert(0, 'CUDAExecutionProvider')
            
            self.session = ort.InferenceSession(model_path, providers=providers)
            
            # Get input/output names
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            
            self.model_loaded = True
            logger.info(f"ONNX model loaded successfully from {model_path}")
            logger.info(f"Input name: {self.input_name}, Output name: {self.output_name}")
            logger.info(f"Providers: {self.session.get_providers()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            return False
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model_loaded and self.session is not None
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for model inference."""
        try:
            # Resize to model input size
            target_size = (settings.model_input_size, settings.model_input_size)
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array
            img_array = np.array(image, dtype=np.float32)
            
            # Normalize to [0, 1]
            img_array = img_array / 255.0
            
            # Standard ImageNet normalization for ResNet models
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            img_array = (img_array - mean) / std
            
            # Add batch dimension - keep HWC format for covid19_resnet model
            # Input shape: [1, height, width, channels]
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
            
            # Ensure float32 dtype
            img_array = img_array.astype(np.float32)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {e}")
            raise
    
    def postprocess_output(self, output: np.ndarray) -> Dict[str, Any]:
        """Postprocess model output."""
        try:
            # Apply softmax to get probabilities
            exp_output = np.exp(output - np.max(output))
            probabilities = exp_output / np.sum(exp_output)
            
            # Flatten probabilities if needed
            if probabilities.ndim > 1:
                probabilities = probabilities.flatten()
            
            # Get prediction
            predicted_class_idx = np.argmax(probabilities)
            predicted_class = self.class_names[predicted_class_idx]
            confidence = float(probabilities[predicted_class_idx])
            
            # Create probability dictionary
            prob_dict = {}
            for i, class_name in enumerate(self.class_names):
                if i < len(probabilities):
                    prob_dict[class_name] = float(probabilities[i])
                else:
                    prob_dict[class_name] = 0.0
            
            return {
                'prediction': predicted_class,
                'confidence': confidence,
                'probabilities': prob_dict
            }
            
        except Exception as e:
            logger.error(f"Error in output postprocessing: {e}")
            raise
    
    async def predict_from_image(self, image: Image.Image) -> Optional[Dict[str, Any]]:
        """Predict pneumonia from PIL Image."""
        if not self.is_loaded():
            logger.error("Model not loaded")
            return None
        
        try:
            start_time = time.time()
            
            # Preprocess image
            input_array = self.preprocess_image(image)
            
            # Run inference
            output = self.session.run([self.output_name], {self.input_name: input_array})
            
            # Postprocess output
            result = self.postprocess_output(output[0])
            
            # Add inference time
            inference_time = time.time() - start_time
            result['inference_time'] = inference_time
            
            logger.info(f"Prediction: {result['prediction']} (confidence: {result['confidence']:.4f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            return None
    
    async def predict_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Predict pneumonia from image file."""
        try:
            # Load and validate image
            image = Image.open(file_path)
            return await self.predict_from_image(image)
            
        except Exception as e:
            logger.error(f"Error loading image from file {file_path}: {e}")
            return None
    
    async def predict_from_base64(self, base64_data: str) -> Optional[Dict[str, Any]]:
        """Predict pneumonia from base64 encoded image."""
        try:
            # Decode base64
            image_data = base64.b64decode(base64_data)
            image = Image.open(io.BytesIO(image_data))
            
            return await self.predict_from_image(image)
            
        except Exception as e:
            logger.error(f"Error processing base64 image: {e}")
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        return {
            'loaded': self.is_loaded(),
            'config': self.model_config,
            'class_names': self.class_names,
            'input_size': settings.model_input_size,
            'confidence_threshold': settings.confidence_threshold,
            'providers': self.session.get_providers() if self.session else None
        }


if __name__ == "__main__":
    import asyncio
    from app.core.config import settings

    async def main():
        model_service = ModelService()
        success = await model_service.load_model()
        if success:
            print("Model loaded successfully!")
            print("Model Info:", model_service.get_model_info())
            
            # Test with a sample image
            test_image_path = "test_xray.png"
            if os.path.exists(test_image_path):
                result = await model_service.predict_from_file(test_image_path)
                print("Prediction Result:", result)
            else:
                print(f"Test image not found at {test_image_path}")
        else:
            print("Failed to load model")

    asyncio.run(main())