"""
Pneumonia Detection API - Database Version
Medical AI application with PostgreSQL backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database imports
from app.core.database import create_tables, engine
from app.models.database import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Pneumonia Detection API...")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    # Create upload directories
    upload_dirs = ["uploads/predictions", "uploads/temp", "uploads/archive"]
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pneumonia Detection API...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Pneumonia Detection API",
    description="Medical AI application for pneumonia detection using chest X-ray images with PostgreSQL backend",
    version="3.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Import database API router
from app.api.api_v1.api_db import api_router

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pneumonia Detection API - Database Version", 
        "status": "running",
        "version": "3.0.0",
        "backend": "PostgreSQL",
        "features": [
            "Patient Management",
            "AI Predictions",
            "Export Functionality", 
            "Audit Logging",
            "Statistics & Analytics"
        ]
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            db_status = "healthy" if result.fetchone() else "unhealthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check upload directories
    upload_status = all(
        os.path.exists(d) for d in ["uploads/predictions", "uploads/temp", "uploads/archive"]
    )
    
    # Check model availability
    try:
        from app.ml.simple_model_service import SimpleModelService
        model_service = SimpleModelService()
        model_status = "loaded" if model_service.is_loaded() else "not_loaded"
    except Exception as e:
        model_status = f"error: {str(e)}"
    
    health_status = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "uploads": "healthy" if upload_status else "unhealthy",
        "model": model_status,
        "version": "3.0.0"
    }
    
    return health_status

@app.get("/info")
async def get_system_info():
    """Get system information and statistics"""
    try:
        from app.models.database import Patient, Prediction
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        try:
            patient_count = db.query(Patient).count()
            prediction_count = db.query(Prediction).count()
        finally:
            db.close()
        
        return {
            "application": "Pneumonia Detection System",
            "version": "3.0.0",
            "backend": "FastAPI + PostgreSQL",
            "ai_model": "EfficientNet-B0 (ONNX)",
            "statistics": {
                "total_patients": patient_count,
                "total_predictions": prediction_count
            },
            "endpoints": {
                "patients": "/api/v1/patients/",
                "predictions": "/api/v1/predictions/",
                "exports": "/api/v1/exports/",
                "audit": "/api/v1/audit/"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_db:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
