"""
Predictions endpoint with in-memory storage
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from PIL import Image
from typing import List, Optional, Dict, Any
from datetime import datetime
import io
import logging
import uuid

from app.ml.model_service import ModelService
from app.api.api_v1.endpoints.patients_clean import get_patient_by_id, patients_store

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize model service
model_service = ModelService()

# In-memory predictions storage
predictions_store: List[Dict[str, Any]] = []

def get_all_predictions() -> List[Dict[str, Any]]:
    """Get all predictions from in-memory store"""
    return predictions_store.copy()

def add_prediction(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """Add a new prediction to in-memory store"""
    prediction["id"] = str(uuid.uuid4())
    prediction["created_at"] = datetime.utcnow().isoformat() + "Z"
    predictions_store.append(prediction)
    return prediction

def get_predictions_by_patient(patient_id: int) -> List[Dict[str, Any]]:
    """Get all predictions for a specific patient"""
    return [p for p in predictions_store if p.get('patient_id') == patient_id]

@router.post("/predict")
async def create_prediction(file: UploadFile = File(...)):
    """
    Simple prediction endpoint for chest X-ray analysis
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Load model if not loaded
        if not model_service.is_loaded():
            success = await model_service.load_model()
            if not success:
                raise HTTPException(status_code=500, detail="Failed to load model")
        
        # Read and process image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Make prediction
        result = await model_service.predict_from_image(image)
        
        if not result:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
        # Create prediction record
        prediction_record = {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "prediction": result['prediction'],
            "confidence": result['confidence'],
            "probabilities": result['probabilities'],
            "inference_time": result['inference_time'],
            "image_size": result['image_size'],
            "image_mode": result['mode'],
            "status": "success"
        }
        
        # Add to in-memory storage
        saved_prediction = add_prediction(prediction_record)
        
        return {
            "message": "Prediction completed successfully",
            "prediction": saved_prediction
        }
        
    except Exception as e:
        logger.error(f"Error in prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict-with-patient")
async def create_prediction_with_patient(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None)
):
    """Create a new prediction for a specific patient"""
    try:
        # Verify patient exists
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Load model if not loaded
        if not model_service.is_loaded():
            success = await model_service.load_model()
            if not success:
                raise HTTPException(status_code=500, detail="Failed to load model")
        
        # Read and process the image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Get prediction from model
        result = await model_service.predict_from_image(image)
        
        if not result:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
        # Create prediction record with patient info
        prediction_record = {
            "patient_id": patient_id,
            "patient_info": {
                "patient_id": patient.get("patient_id"),
                "first_name": patient.get("first_name"),
                "last_name": patient.get("last_name"),
                "age": patient.get("age"),
                "gender": patient.get("gender")
            },
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content),
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "probabilities": result["probabilities"],
            "inference_time": result["inference_time"],
            "image_size": result["image_size"],
            "image_mode": result["mode"],
            "notes": notes,
            "status": "success"
        }
        
        # Add to in-memory storage
        saved_prediction = add_prediction(prediction_record)
        
        return {
            "message": "Prediction created successfully",
            "prediction": saved_prediction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prediction with patient: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating prediction: {str(e)}")

@router.get("/predictions")
async def list_predictions():
    """Get all predictions"""
    try:
        predictions = get_all_predictions()
        return {
            "predictions": predictions,
            "total": len(predictions),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error retrieving predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading predictions: {str(e)}")

@router.get("/predictions/patient/{patient_id}")
async def get_patient_predictions(patient_id: int):
    """Get all predictions for a specific patient"""
    try:
        # Verify patient exists
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        patient_predictions = get_predictions_by_patient(patient_id)
        
        return {
            "patient": patient,
            "predictions": patient_predictions,
            "total": len(patient_predictions),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving patient predictions: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading patient predictions: {str(e)}")

@router.get("/predictions/stats")
async def get_prediction_statistics():
    """Get prediction statistics"""
    try:
        predictions = get_all_predictions()
        
        total_predictions = len(predictions)
        if total_predictions == 0:
            return {
                "total_predictions": 0,
                "pneumonia_cases": 0,
                "normal_cases": 0,
                "unique_patients": 0,
                "average_confidence": 0,
                "status": "success"
            }
        
        pneumonia_count = len([p for p in predictions if p.get('prediction', '').upper() == 'PNEUMONIA'])
        normal_count = len([p for p in predictions if p.get('prediction', '').upper() == 'NORMAL'])
        
        # Get unique patients with predictions
        unique_patients = len(set(p.get('patient_id') for p in predictions if p.get('patient_id')))
        
        # Calculate average confidence
        avg_confidence = sum(p.get('confidence', 0) for p in predictions) / total_predictions
        
        return {
            "total_predictions": total_predictions,
            "pneumonia_cases": pneumonia_count,
            "normal_cases": normal_count,
            "unique_patients": unique_patients,
            "average_confidence": round(avg_confidence, 3),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error calculating prediction statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for predictions endpoint"""
    return {
        "status": "ok", 
        "message": "Predictions endpoint is working",
        "model_loaded": model_service.is_loaded(),
        "predictions_count": len(predictions_store)
    }
