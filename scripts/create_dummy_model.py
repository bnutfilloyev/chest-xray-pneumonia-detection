#!/usr/bin/env python3
"""
Create a dummy ONNX model for development and testing purposes.
This creates a simple model with the correct input/output shapes for pneumonia detection.
"""

import numpy as np
import onnx
from onnx import helper, TensorProto
import os

def create_dummy_pneumonia_model():
    """Create a dummy ONNX model for pneumonia detection."""
    
    # Define model input and output
    input_shape = [1, 3, 224, 224]  # Batch, Channels, Height, Width
    output_shape = [1, 2]  # Batch, Classes (Normal, Pneumonia)
    
    # Create input tensor
    input_tensor = helper.make_tensor_value_info(
        'input',
        TensorProto.FLOAT,
        input_shape
    )
    
    # Create output tensor
    output_tensor = helper.make_tensor_value_info(
        'output',
        TensorProto.FLOAT,
        output_shape
    )
    
    # Create a simple dummy computation (just a matrix multiplication)
    # This is for testing only - not a real pneumonia detection model!
    
    # Flatten input: [1, 3, 224, 224] -> [1, 150528]
    flatten_node = helper.make_node(
        'Flatten',
        inputs=['input'],
        outputs=['flattened'],
        axis=1
    )
    
    # Create weight matrix: [150528, 2]
    weights = np.random.randn(150528, 2).astype(np.float32) * 0.01
    weights_tensor = helper.make_tensor(
        'weights',
        TensorProto.FLOAT,
        weights.shape,
        weights.flatten()
    )
    
    # Matrix multiplication
    matmul_node = helper.make_node(
        'MatMul',
        inputs=['flattened', 'weights'],
        outputs=['logits']
    )
    
    # Apply softmax to get probabilities
    softmax_node = helper.make_node(
        'Softmax',
        inputs=['logits'],
        outputs=['output'],
        axis=1
    )
    
    # Create the graph
    graph = helper.make_graph(
        nodes=[flatten_node, matmul_node, softmax_node],
        name='dummy_pneumonia_model',
        inputs=[input_tensor],
        outputs=[output_tensor],
        initializer=[weights_tensor]
    )
    
    # Create the model
    model = helper.make_model(graph, producer_name='dummy_model_creator')
    model.opset_import[0].version = 11
    
    # Set model metadata using the proper format
    metadata = model.metadata_props.add()
    metadata.key = "model_name"
    metadata.value = "Dummy Pneumonia Detection Model"
    
    metadata = model.metadata_props.add()
    metadata.key = "version"
    metadata.value = "1.0.0-dev"
    
    metadata = model.metadata_props.add()
    metadata.key = "description"
    metadata.value = "Dummy model for development only"
    
    return model

def main():
    """Create and save the dummy model."""
    print("Creating dummy ONNX model for pneumonia detection...")
    
    # Get the model directory
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
    model_path = os.path.join(model_dir, 'pneumonia_model.onnx')
    
    # Create the model
    model = create_dummy_pneumonia_model()
    
    # Validate the model
    try:
        onnx.checker.check_model(model)
        print("✅ Model validation passed")
    except Exception as e:
        print(f"❌ Model validation failed: {e}")
        return
    
    # Save the model
    try:
        onnx.save(model, model_path)
        print(f"✅ Dummy model saved to: {model_path}")
        print("\n⚠️  WARNING: This is a dummy model for development only!")
        print("   It will NOT provide accurate pneumonia detection.")
        print("   Replace with a properly trained model for production use.")
    except Exception as e:
        print(f"❌ Failed to save model: {e}")

if __name__ == "__main__":
    main()
