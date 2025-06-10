"""
Simple Patient Management - No authentication, in-memory storage
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()

# Simple patient data model
class SimplePatient(BaseModel):
    id: Optional[int] = None
    patient_id: str
    first_name: str
    last_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[str] = None

# In-memory storage - clean implementation
patients_store: List[Dict[str, Any]] = []
next_patient_id = 1

def get_next_id() -> int:
    """Get next available ID"""
    global next_patient_id
    current_id = next_patient_id
    next_patient_id += 1
    return current_id

@router.get("/", response_model=List[SimplePatient])
async def get_patients():
    """Get all patients"""
    try:
        return patients_store
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading patients: {str(e)}")

@router.post("/", response_model=SimplePatient)
async def create_patient(patient: SimplePatient):
    """Create a new patient"""
    try:
        # Check if patient_id already exists
        if any(p.get('patient_id') == patient.patient_id for p in patients_store):
            raise HTTPException(status_code=400, detail="Patient ID already exists")
        
        # Add new patient
        new_patient = patient.dict()
        new_patient['id'] = get_next_id()
        new_patient['created_at'] = datetime.now().isoformat()
        
        patients_store.append(new_patient)
        
        return new_patient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating patient: {str(e)}")

@router.get("/{patient_id}", response_model=SimplePatient)
async def get_patient(patient_id: int):
    """Get patient by ID"""
    try:
        patient = next((p for p in patients_store if p.get('id') == patient_id), None)
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        return patient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting patient: {str(e)}")

@router.put("/{patient_id}", response_model=SimplePatient)
async def update_patient(patient_id: int, patient_update: SimplePatient):
    """Update patient"""
    try:
        patient_index = next((i for i, p in enumerate(patients_store) if p.get('id') == patient_id), None)
        
        if patient_index is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Update patient data
        updated_patient = patient_update.dict()
        updated_patient['id'] = patient_id
        updated_patient['created_at'] = patients_store[patient_index].get('created_at')
        
        patients_store[patient_index] = updated_patient
        
        return updated_patient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating patient: {str(e)}")

@router.delete("/{patient_id}")
async def delete_patient(patient_id: int):
    """Delete patient"""
    try:
        patient_index = next((i for i, p in enumerate(patients_store) if p.get('id') == patient_id), None)
        
        if patient_index is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        deleted_patient = patients_store.pop(patient_index)
        
        return {"message": "Patient deleted successfully", "patient_id": patient_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting patient: {str(e)}")

@router.get("/search/{query}")
async def search_patients(query: str):
    """Search patients by name or patient_id"""
    try:
        query = query.lower()
        
        matching_patients = [
            p for p in patients_store 
            if query in p.get('first_name', '').lower() 
            or query in p.get('last_name', '').lower()
            or query in p.get('patient_id', '').lower()
        ]
        
        return matching_patients
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching patients: {str(e)}")

# Helper functions for external use
def get_patient_by_id(patient_id: int) -> Optional[Dict[str, Any]]:
    """Helper function to get patient by ID - for use by other modules"""
    return next((p for p in patients_store if p.get('id') == patient_id), None)
