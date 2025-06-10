"""
Database-backed Predictions Management with ML Integration
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from PIL import Image
import io
import os
import uuid
import logging

from app.core.database import get_db
from app.models.database import Patient, Prediction, AuditLog
from app.models.schemas import (
    PredictionCreate, PredictionResponse, 
    PaginatedResponse, OverviewStats
)
from app.ml.model_service import ModelService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize model service
model_service = ModelService()

# File upload configuration
UPLOAD_DIR = "uploads/predictions"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/predict", response_model=PredictionResponse)
async def create_simple_prediction(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Simple prediction endpoint without patient association"""
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
        
        # Save file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create prediction record (no patient)
        prediction = Prediction(
            id=file_id,
            patient_id=None,  # No patient for simple prediction
            image_filename=filename,
            original_filename=file.filename,
            image_path=file_path,
            prediction=result['prediction'],
            confidence=result['confidence'],
            confidence_scores=result['probabilities'],
            inference_time=result.get('inference_time'),
            image_size=result.get('image_size'),
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        # Log audit trail
        audit = AuditLog(
            user_id="system",
            action_type="PREDICTION",
            entity_type="Prediction",
            entity_id=prediction.id,
            details={
                "prediction": result['prediction'],
                "confidence": result['confidence'],
                "filename": file.filename
            }
        )
        db.add(audit)
        db.commit()
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in simple prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/predict-with-patient", response_model=PredictionResponse)
async def create_prediction_with_patient(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    clinical_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Create prediction for a specific patient"""
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
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
        
        # Read and process image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Make prediction
        result = await model_service.predict_from_image(image)
        if not result:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
        # Save file
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create prediction record
        prediction = Prediction(
            id=file_id,
            patient_id=patient_id,
            image_filename=filename,
            original_filename=file.filename,
            image_path=file_path,
            prediction=result['prediction'],
            confidence=result['confidence'],
            confidence_scores=result['probabilities'],
            inference_time=result.get('inference_time'),
            image_size=result.get('image_size'),
            clinical_notes=clinical_notes
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        # Set patient info for response
        prediction.patient_info = {
            "patient_id": patient.patient_id,
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "age": patient.age,
            "gender": patient.gender
        }
        
        # Log audit trail
        audit = AuditLog(
            user_id="system",
            action_type="PREDICTION",
            entity_type="Prediction",
            entity_id=prediction.id,
            details={
                "patient_id": patient_id,
                "prediction": result['prediction'],
                "confidence": result['confidence'],
                "filename": file.filename
            }
        )
        db.add(audit)
        db.commit()
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating prediction with patient: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating prediction: {str(e)}")

@router.get("/predictions", response_model=PaginatedResponse[PredictionResponse])
async def get_predictions(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    patient_id: Optional[int] = Query(None),
    prediction_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get paginated list of predictions with filters"""
    try:
        query = db.query(Prediction).join(Patient, Prediction.patient_id == Patient.id, isouter=True)
        
        # Apply filters
        if patient_id:
            query = query.filter(Prediction.patient_id == patient_id)
        
        if prediction_type:
            query = query.filter(Prediction.prediction == prediction_type.upper())
        
        # Order by most recent
        query = query.order_by(desc(Prediction.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        predictions = query.offset(offset).limit(size).all()
        
        # Add patient info to each prediction
        for prediction in predictions:
            if prediction.patient:
                prediction.patient_info = {
                    "patient_id": prediction.patient.patient_id,
                    "first_name": prediction.patient.first_name,
                    "last_name": prediction.patient.last_name,
                    "age": prediction.patient.age,
                    "gender": prediction.patient.gender
                }
        
        # Calculate pages
        pages = (total + size - 1) // size
        
        return PaginatedResponse(
            items=predictions,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving predictions: {str(e)}")

@router.get("/predictions/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(prediction_id: str, db: Session = Depends(get_db)):
    """Get specific prediction by ID"""
    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Add patient info if available
        if prediction.patient:
            prediction.patient_info = {
                "patient_id": prediction.patient.patient_id,
                "first_name": prediction.patient.first_name,
                "last_name": prediction.patient.last_name,
                "age": prediction.patient.age,
                "gender": prediction.patient.gender
            }
        
        return prediction
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving prediction: {str(e)}")

@router.get("/predictions/patient/{patient_id}")
async def get_patient_predictions(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get all predictions for a specific patient"""
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get predictions
        predictions = db.query(Prediction).filter(
            Prediction.patient_id == patient_id
        ).order_by(desc(Prediction.created_at)).all()
        
        # Add patient info to each prediction
        for prediction in predictions:
            prediction.patient_info = {
                "patient_id": patient.patient_id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "age": patient.age,
                "gender": patient.gender
            }
        
        return {
            "patient": patient,
            "predictions": predictions,
            "total": len(predictions),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient predictions: {str(e)}")

@router.get("/stats/overview", response_model=OverviewStats)
async def get_overview_stats(db: Session = Depends(get_db)):
    """Get comprehensive overview statistics"""
    try:
        # Get date ranges
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        
        # Patient stats
        total_patients = db.query(Patient).count()
        
        # Prediction stats
        total_predictions = db.query(Prediction).count()
        predictions_today = db.query(Prediction).filter(
            func.date(Prediction.created_at) == today
        ).count()
        
        pneumonia_cases = db.query(Prediction).filter(
            Prediction.prediction == "PNEUMONIA"
        ).count()
        
        normal_cases = db.query(Prediction).filter(
            Prediction.prediction == "NORMAL"
        ).count()
        
        # Average confidence
        avg_confidence_result = db.query(func.avg(Prediction.confidence)).scalar()
        average_confidence = float(avg_confidence_result) if avg_confidence_result else 0
        
        # Mock model accuracy (you can implement actual accuracy tracking)
        model_accuracy = 0.94  # 94% mock accuracy
        
        # Active users (mock for now)
        active_users = 5
        
        return OverviewStats(
            total_patients=total_patients,
            total_predictions=total_predictions,
            predictions_today=predictions_today,
            pneumonia_cases=pneumonia_cases,
            normal_cases=normal_cases,
            average_confidence=round(average_confidence, 3),
            model_accuracy=model_accuracy,
            active_users=active_users
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating overview stats: {str(e)}")

@router.get("/stats/predictions")
async def get_prediction_statistics(db: Session = Depends(get_db)):
    """Get detailed prediction statistics"""
    try:
        total_predictions = db.query(Prediction).count()
        
        if total_predictions == 0:
            return {
                "total_predictions": 0,
                "pneumonia_cases": 0,
                "normal_cases": 0,
                "unique_patients": 0,
                "average_confidence": 0,
                "status": "success"
            }
        
        pneumonia_count = db.query(Prediction).filter(
            Prediction.prediction == "PNEUMONIA"
        ).count()
        
        normal_count = db.query(Prediction).filter(
            Prediction.prediction == "NORMAL"
        ).count()
        
        # Unique patients with predictions
        unique_patients = db.query(Prediction.patient_id).distinct().count()
        
        # Average confidence
        avg_confidence_result = db.query(func.avg(Prediction.confidence)).scalar()
        avg_confidence = float(avg_confidence_result) if avg_confidence_result else 0
        
        return {
            "total_predictions": total_predictions,
            "pneumonia_cases": pneumonia_count,
            "normal_cases": normal_count,
            "unique_patients": unique_patients,
            "average_confidence": round(avg_confidence, 3),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating prediction statistics: {str(e)}")

@router.put("/predictions/{prediction_id}/review")
async def review_prediction(
    prediction_id: str,
    reviewed_by: str = Form(...),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Mark prediction as reviewed by a medical professional"""
    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        prediction.reviewed = True
        prediction.reviewed_by = reviewed_by
        prediction.reviewed_at = datetime.utcnow()
        
        if notes:
            prediction.clinical_notes = notes
        
        db.commit()
        db.refresh(prediction)
        
        # Log audit trail
        audit = AuditLog(
            user_id=reviewed_by,
            action_type="PREDICTION",
            entity_type="Prediction",
            entity_id=prediction_id,
            details={"reviewed_by": reviewed_by, "notes": notes}
        )
        db.add(audit)
        db.commit()
        
        return {"message": "Prediction reviewed successfully", "prediction_id": prediction_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error reviewing prediction: {str(e)}")

@router.delete("/predictions/{prediction_id}")
async def delete_prediction(prediction_id: str, db: Session = Depends(get_db)):
    """Delete a prediction"""
    try:
        prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        # Delete associated file
        if prediction.image_path and os.path.exists(prediction.image_path):
            os.remove(prediction.image_path)
        
        # Delete prediction
        db.delete(prediction)
        db.commit()
        
        # Log audit trail
        audit = AuditLog(
            user_id="system",
            action_type="PREDICTION",
            entity_type="Prediction",
            entity_id=prediction_id,
            details={"prediction": prediction.prediction, "filename": prediction.original_filename}
        )
        db.add(audit)
        db.commit()
        
        return {"message": "Prediction deleted successfully", "prediction_id": prediction_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting prediction: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for predictions endpoint"""
    try:
        model_loaded = model_service.is_loaded()
        return {
            "status": "ok",
            "message": "Predictions endpoint is working",
            "model_loaded": model_loaded,
            "upload_dir": UPLOAD_DIR,
            "upload_dir_exists": os.path.exists(UPLOAD_DIR)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Health check failed: {str(e)}",
            "model_loaded": False
        }
