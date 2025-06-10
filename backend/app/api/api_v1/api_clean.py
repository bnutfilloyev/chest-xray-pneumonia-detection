"""
Clean API Routes - Consolidated without authentication
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints.patients_clean import router as patients_router
from app.api.api_v1.endpoints.predictions import router as predictions_router

api_router = APIRouter()

# Include clean endpoints
api_router.include_router(patients_router, prefix="/patients", tags=["patients"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
