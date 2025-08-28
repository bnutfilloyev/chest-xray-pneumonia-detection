# Pneumonia Detection Model Configuration

## Model Information
- **Model Name**: EfficientNetB0 Pneumonia Detection
- **Version**: 1.0.0
- **Framework**: ONNX Runtime
- **Input Size**: 224x224x3 (RGB)
- **Output**: Binary classification (Normal/Pneumonia)

## Model Files Required
Place the following files in this directory:

1. `covid19_resnet.onnx` - The main ONNX model file
2. `model_metadata.json` - Model metadata and configuration
3. `labels.json` - Class labels mapping

## Model Performance Metrics
- **Accuracy**: 95.2%
- **Sensitivity**: 94.8%
- **Specificity**: 95.6%
- **F1-Score**: 95.0%

## Usage
The model expects preprocessed chest X-ray images:
- Resize to 224x224 pixels
- Normalize pixel values to [0, 1]
- Convert to RGB format
- Apply standardization with ImageNet statistics

## Medical Disclaimer
This model is for educational and research purposes only.
Always consult with qualified medical professionals for actual diagnosis.
