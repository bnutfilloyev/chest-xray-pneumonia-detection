# Pneumonia Detection Model Placeholder

This file serves as a placeholder for the actual ONNX model file.

## Model Requirements:
- Input: RGB images of size 224x224
- Output: Binary classification (Normal vs Pneumonia)
- Format: ONNX (Open Neural Network Exchange)

## To replace this placeholder:
1. Train or obtain a pneumonia detection model
2. Convert the model to ONNX format
3. Replace this file with the actual model file named 'pneumonia_model.onnx'

## Expected model characteristics:
- Architecture: EfficientNetB0 or similar
- Input shape: [batch_size, 3, 224, 224]
- Output shape: [batch_size, 2] (Normal, Pneumonia probabilities)
- Data type: float32

For development purposes, the application will handle the missing model gracefully.
