"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum

# Generic type for pagination
T = TypeVar('T')

# Enums
class GenderEnum(str, Enum):
    M = "M"
    F = "F"
    Other = "Other"

class PredictionEnum(str, Enum):
    normal = "NORMAL"
    pneumonia = "PNEUMONIA"

class ActionTypeEnum(str, Enum):
    login = "LOGIN"
    logout = "LOGOUT"
    prediction = "PREDICTION"
    export = "EXPORT"
    patient_create = "PATIENT_CREATE"
    patient_update = "PATIENT_UPDATE"
    patient_view = "PATIENT_VIEW"

# Patient schemas
class PatientBase(BaseModel):
    patient_id: str = Field(..., description="Unique patient identifier")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    medical_record_number: Optional[str] = Field(None, max_length=50)
    emergency_contact: Optional[Dict[str, Any]] = None
    insurance_info: Optional[Dict[str, Any]] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    medical_record_number: Optional[str] = Field(None, max_length=50)
    emergency_contact: Optional[Dict[str, Any]] = None
    insurance_info: Optional[Dict[str, Any]] = None

class PatientFilters(BaseModel):
    """Filters for patient queries"""
    search: Optional[str] = Field(None, description="Search in name or patient ID")
    gender: Optional[GenderEnum] = None
    age_min: Optional[int] = Field(None, ge=0, le=150)
    age_max: Optional[int] = Field(None, ge=0, le=150)
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Prediction schemas
class PredictionBase(BaseModel):
    clinical_notes: Optional[str] = None

class PredictionCreate(PredictionBase):
    patient_id: Optional[int] = None  # Allow predictions without patient

class PredictionResponse(BaseModel):
    id: str
    patient_id: Optional[int] = None  # Allow predictions without patient
    image_filename: str
    original_filename: Optional[str] = None
    prediction: PredictionEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_scores: Dict[str, float]
    inference_time: Optional[float] = None
    image_size: Optional[List[int]] = None
    clinical_notes: Optional[str] = None
    reviewed: bool = False
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    
    # Patient info
    patient_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Statistics schemas
class OverviewStats(BaseModel):
    total_patients: int
    total_predictions: int
    predictions_today: int
    pneumonia_cases: int
    normal_cases: int
    average_confidence: float
    model_accuracy: float
    active_users: int

class DailyStats(BaseModel):
    date: str
    predictions: int
    accuracy: float

class MonthlyAccuracy(BaseModel):
    month: str
    accuracy: float

class SystemStatsResponse(BaseModel):
    date: datetime
    total_patients: int
    total_predictions: int
    predictions_today: int
    pneumonia_cases: int
    normal_cases: int
    average_confidence: float
    model_accuracy: float
    active_users: int
    
    class Config:
        from_attributes = True

class WeeklyStatsResponse(BaseModel):
    week_start: datetime
    week_end: datetime
    predictions_count: int
    accuracy_rate: float
    pneumonia_detected: int
    normal_cases: int
    unique_patients: int
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    overview: OverviewStats
    recent_predictions: List[PredictionResponse]
    weekly_trends: List[WeeklyStatsResponse]
    monthly_accuracy: List[MonthlyAccuracy]

# Audit schemas
class AuditLogCreate(BaseModel):
    user_id: str
    action_type: ActionTypeEnum
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: int
    user_id: str
    action_type: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Export schemas
class ExportRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    patient_ids: Optional[List[int]] = None
    prediction_types: Optional[List[PredictionEnum]] = None
    include_images: bool = False

class ExportResponse(BaseModel):
    filename: str
    download_url: str
    file_size: int
    record_count: int
    created_at: datetime

# Response wrappers
class APIResponse(BaseModel):
    message: str
    status: str = "success"
    data: Optional[Any] = None

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ErrorResponse(BaseModel):
    message: str
    status: str = "error"
    detail: Optional[str] = None