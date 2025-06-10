"""
Database-backed Patient Management with comprehensive CRUD operations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from app.core.database import get_db
from app.models.database import Patient, Prediction, AuditLog
from app.models.schemas import (
    PatientCreate, PatientUpdate, PatientResponse,
    PaginatedResponse, PatientFilters
)

router = APIRouter()

# CRUD Operations

@router.get("/", response_model=PaginatedResponse[PatientResponse])
async def get_patients(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    gender: Optional[str] = Query(None),
    created_after: Optional[date] = Query(None),
    created_before: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get paginated list of patients with filters"""
    try:
        query = db.query(Patient)
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Patient.first_name.ilike(search_term),
                    Patient.last_name.ilike(search_term),
                    Patient.patient_id.ilike(search_term),
                    Patient.medical_record_number.ilike(search_term)
                )
            )
        
        if gender:
            query = query.filter(Patient.gender == gender)
            
        if created_after:
            query = query.filter(Patient.created_at >= created_after)
            
        if created_before:
            query = query.filter(Patient.created_at <= created_before)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        patients = query.offset(offset).limit(size).all()
        
        # Calculate pages
        pages = (total + size - 1) // size
        
        return PaginatedResponse(
            items=patients,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patients: {str(e)}")

@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db)
):
    """Create a new patient"""
    try:
        # Check if patient_id already exists
        existing = db.query(Patient).filter(Patient.patient_id == patient_data.patient_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Patient ID already exists")
        
        # Create new patient
        patient = Patient(**patient_data.dict())
        db.add(patient)
        db.commit()
        db.refresh(patient)
        
        # Log audit trail
        audit = AuditLog(
            user_id="system",
            action_type="PATIENT_CREATE",
            entity_type="Patient",
            entity_id=str(patient.id),
            details={"patient_id": patient.patient_id, "name": f"{patient.first_name} {patient.last_name}"}
        )
        db.add(audit)
        db.commit()
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating patient: {str(e)}")

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """Get patient by ID"""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patient: {str(e)}")

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """Update patient information"""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Update fields
        update_data = patient_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        patient.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(patient)
        
        # Log audit trail
        audit = AuditLog(
            user_id="system",
            action_type="PATIENT_UPDATE",
            entity_type="Patient",
            entity_id=str(patient.id),
            details={"updated_fields": list(update_data.keys())}
        )
        db.add(audit)
        db.commit()
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating patient: {str(e)}")

@router.delete("/{patient_id}")
async def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """Delete patient (soft delete by setting deleted_at)"""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Check if patient has predictions
        prediction_count = db.query(Prediction).filter(Prediction.patient_id == patient_id).count()
        
        if prediction_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete patient with {prediction_count} existing predictions"
            )
        
        # Delete patient
        db.delete(patient)
        db.commit()
        
        # Log audit trail
        audit = AuditLog(
            user_id="system",
            action_type="PATIENT_DELETE",
            entity_type="Patient",
            entity_id=str(patient.id),
            details={"patient_id": patient.patient_id, "name": f"{patient.first_name} {patient.last_name}"}
        )
        db.add(audit)
        db.commit()
        
        return {"message": "Patient deleted successfully", "patient_id": patient_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting patient: {str(e)}")

@router.get("/search/{query}")
async def search_patients(
    query: str,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search patients by name, patient_id, or medical record number"""
    try:
        search_term = f"%{query}%"
        patients = db.query(Patient).filter(
            or_(
                Patient.first_name.ilike(search_term),
                Patient.last_name.ilike(search_term),
                Patient.patient_id.ilike(search_term),
                Patient.medical_record_number.ilike(search_term)
            )
        ).limit(limit).all()
        
        return patients
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching patients: {str(e)}")

@router.get("/{patient_id}/predictions")
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
        
        # Get predictions with patient info
        predictions = db.query(Prediction).filter(Prediction.patient_id == patient_id).all()
        
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

@router.get("/{patient_id}/stats")
async def get_patient_stats(patient_id: int, db: Session = Depends(get_db)):
    """Get statistics for a specific patient"""
    try:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Calculate stats
        predictions = db.query(Prediction).filter(Prediction.patient_id == patient_id).all()
        total_predictions = len(predictions)
        pneumonia_count = len([p for p in predictions if p.prediction == "PNEUMONIA"])
        normal_count = total_predictions - pneumonia_count
        avg_confidence = sum(p.confidence for p in predictions) / total_predictions if total_predictions > 0 else 0
        
        return {
            "patient_id": patient_id,
            "total_predictions": total_predictions,
            "pneumonia_cases": pneumonia_count,
            "normal_cases": normal_count,
            "average_confidence": round(avg_confidence, 3),
            "last_prediction": predictions[-1].created_at if predictions else None,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating patient stats: {str(e)}")
