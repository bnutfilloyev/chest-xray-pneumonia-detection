"""
Database models for pneumonia detection system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    medical_record_number = Column(String(50))
    emergency_contact = Column(JSON)
    insurance_info = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    predictions = relationship("Prediction", back_populates="patient")

class Prediction(Base):
    """Prediction model"""
    __tablename__ = "predictions"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)  # Allow predictions without patient
    image_filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    image_path = Column(String(500))
    prediction = Column(String(20), nullable=False)  # NORMAL or PNEUMONIA
    confidence = Column(Float, nullable=False)
    confidence_scores = Column(JSON)  # {NORMAL: 0.2, PNEUMONIA: 0.8}
    inference_time = Column(Float)
    image_size = Column(JSON)  # [width, height]
    clinical_notes = Column(Text)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(100))
    reviewed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="predictions")

class AuditLog(Base):
    """Audit log for tracking user actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)  # Doctor/user identifier
    action_type = Column(String(50), nullable=False)  # LOGIN, PREDICTION, EXPORT, etc.
    entity_type = Column(String(50))  # PATIENT, PREDICTION
    entity_id = Column(String(50))  # ID of affected entity
    details = Column(JSON)  # Additional action details
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class SystemStats(Base):
    """System statistics for dashboard"""
    __tablename__ = "system_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    total_patients = Column(Integer, default=0)
    total_predictions = Column(Integer, default=0)
    predictions_today = Column(Integer, default=0)
    pneumonia_cases = Column(Integer, default=0)
    normal_cases = Column(Integer, default=0)
    average_confidence = Column(Float, default=0.0)
    model_accuracy = Column(Float, default=0.0)
    active_users = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WeeklyStats(Base):
    """Weekly statistics for charts"""
    __tablename__ = "weekly_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(DateTime(timezone=True), nullable=False)
    week_end = Column(DateTime(timezone=True), nullable=False)
    predictions_count = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    pneumonia_detected = Column(Integer, default=0)
    normal_cases = Column(Integer, default=0)
    unique_patients = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())