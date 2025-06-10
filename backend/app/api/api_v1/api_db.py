"""
Database-backed API Routes with comprehensive functionality
"""
from fastapi import APIRouter

# Import database-backed endpoints
from app.api.api_v1.endpoints.patients_db import router as patients_router
from app.api.api_v1.endpoints.predictions_db import router as predictions_router
from app.api.api_v1.endpoints.exports import router as exports_router
from app.api.api_v1.endpoints.audit import router as audit_router
from app.api.api_v1.endpoints.stats import router as stats_router

api_router = APIRouter()

# Include database endpoints
api_router.include_router(patients_router, prefix="/patients", tags=["patients"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
api_router.include_router(exports_router, prefix="/exports", tags=["exports"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit", "monitoring"])
api_router.include_router(stats_router, prefix="/stats", tags=["statistics"])
