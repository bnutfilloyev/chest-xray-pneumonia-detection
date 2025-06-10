"""
Statistics and Analytics endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import logging

from app.core.database import get_db
from app.models.database import Patient, Prediction, WeeklyStats, SystemStats
from app.models.schemas import (
    OverviewStats, WeeklyStatsResponse, DailyStats, 
    MonthlyAccuracy, APIResponse
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/overview", response_model=OverviewStats)
async def get_overview_stats(db: Session = Depends(get_db)):
    """Get overview statistics for dashboard"""
    try:
        # Basic counts
        total_patients = db.query(Patient).count()
        total_predictions = db.query(Prediction).count()
        
        # Today's predictions
        today = datetime.utcnow().date()
        predictions_today = db.query(Prediction).filter(
            func.date(Prediction.created_at) == today
        ).count()
        
        # Prediction type counts
        pneumonia_cases = db.query(Prediction).filter(
            Prediction.prediction == "PNEUMONIA"
        ).count()
        
        normal_cases = db.query(Prediction).filter(
            Prediction.prediction == "NORMAL"
        ).count()
        
        # Average confidence
        avg_confidence_result = db.query(func.avg(Prediction.confidence)).scalar()
        average_confidence = float(avg_confidence_result) if avg_confidence_result else 0.0
        
        # Get latest system stats for model accuracy
        latest_stats = db.query(SystemStats).order_by(desc(SystemStats.date)).first()
        model_accuracy = latest_stats.model_accuracy if latest_stats else 0.94
        
        # Active users (mock for now - would come from user sessions)
        active_users = 5
        
        return OverviewStats(
            total_patients=total_patients,
            total_predictions=total_predictions,
            predictions_today=predictions_today,
            pneumonia_cases=pneumonia_cases,
            normal_cases=normal_cases,
            average_confidence=average_confidence,
            model_accuracy=model_accuracy,
            active_users=active_users
        )
        
    except Exception as e:
        logger.error(f"Error getting overview stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get overview statistics")

@router.get("/weekly", response_model=List[WeeklyStatsResponse])
async def get_weekly_stats(
    weeks: int = Query(12, ge=1, le=52),
    db: Session = Depends(get_db)
):
    """Get weekly statistics for the past N weeks"""
    try:
        weekly_stats = db.query(WeeklyStats).order_by(
            desc(WeeklyStats.week_start)
        ).limit(weeks).all()
        
        return [WeeklyStatsResponse.from_orm(stat) for stat in weekly_stats]
        
    except Exception as e:
        logger.error(f"Error getting weekly stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get weekly statistics")

@router.get("/daily", response_model=List[DailyStats])
async def get_daily_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get daily prediction statistics"""
    try:
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        # Query predictions grouped by date
        daily_data = db.query(
            func.date(Prediction.created_at).label('date'),
            func.count(Prediction.id).label('predictions'),
            func.avg(Prediction.confidence).label('avg_confidence')
        ).filter(
            and_(
                func.date(Prediction.created_at) >= start_date,
                func.date(Prediction.created_at) <= end_date
            )
        ).group_by(
            func.date(Prediction.created_at)
        ).order_by(
            func.date(Prediction.created_at)
        ).all()
        
        # Convert to response format
        daily_stats = []
        for row in daily_data:
            daily_stats.append(DailyStats(
                date=row.date.isoformat(),
                predictions=row.predictions,
                accuracy=float(row.avg_confidence) if row.avg_confidence else 0.0
            ))
        
        return daily_stats
        
    except Exception as e:
        logger.error(f"Error getting daily stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get daily statistics")

@router.get("/monthly-accuracy", response_model=List[MonthlyAccuracy])
async def get_monthly_accuracy(
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """Get monthly accuracy statistics"""
    try:
        # For now, return mock data with realistic accuracy values
        # In a real system, this would be calculated from validated predictions
        monthly_accuracy = []
        
        current_date = datetime.utcnow()
        for i in range(months):
            month_date = current_date - timedelta(days=30 * i)
            month_name = month_date.strftime("%Y-%m")
            
            # Mock accuracy with some variation (92-96%)
            base_accuracy = 0.94
            variation = (i % 3) * 0.01 - 0.01  # -0.01, 0, 0.01
            accuracy = base_accuracy + variation
            
            monthly_accuracy.append(MonthlyAccuracy(
                month=month_name,
                accuracy=accuracy
            ))
        
        return list(reversed(monthly_accuracy))  # Chronological order
        
    except Exception as e:
        logger.error(f"Error getting monthly accuracy: {e}")
        raise HTTPException(status_code=500, detail="Failed to get monthly accuracy")

@router.get("/patient-demographics")
async def get_patient_demographics(db: Session = Depends(get_db)):
    """Get patient demographic statistics"""
    try:
        # Check if we have any patients first
        patient_count = db.query(func.count(Patient.id)).scalar()
        
        if patient_count == 0:
            # Return empty demographics if no patients
            return {
                "gender_distribution": [],
                "age_groups": [],
                "predictions_by_gender": []
            }
        
        # Gender distribution
        gender_stats = db.query(
            Patient.gender,
            func.count(Patient.id).label('count')
        ).group_by(Patient.gender).all()
        
        # Age groups
        age_groups = db.query(
            case(
                (Patient.age < 18, 'Under 18'),
                (and_(Patient.age >= 18, Patient.age < 35), '18-34'),
                (and_(Patient.age >= 35, Patient.age < 55), '35-54'),
                (and_(Patient.age >= 55, Patient.age < 75), '55-74'),
                (Patient.age >= 75, '75+'),
                else_='Unknown'
            ).label('age_group'),
            func.count(Patient.id).label('count')
        ).group_by('age_group').all()
        
        # Predictions by patient gender - use left join to handle cases where there might be patients without predictions
        prediction_by_gender = db.query(
            Patient.gender,
            Prediction.prediction,
            func.count(Prediction.id).label('count')
        ).outerjoin(Prediction, Patient.id == Prediction.patient_id).group_by(
            Patient.gender, Prediction.prediction
        ).all()
        
        return {
            "gender_distribution": [
                {"gender": row.gender or "Unknown", "count": row.count} 
                for row in gender_stats
            ],
            "age_groups": [
                {"age_group": row.age_group, "count": row.count} 
                for row in age_groups
            ],
            "predictions_by_gender": [
                {
                    "gender": row.gender or "Unknown", 
                    "prediction": row.prediction or "No predictions", 
                    "count": row.count
                } 
                for row in prediction_by_gender if row.count > 0
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting demographics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patient demographics")

@router.get("/model-performance")
async def get_model_performance(db: Session = Depends(get_db)):
    """Get model performance metrics"""
    try:
        # Confidence distribution
        confidence_ranges = db.query(
            func.case(
                [(Prediction.confidence < 0.5, 'Very Low (< 50%)'),
                 (and_(Prediction.confidence >= 0.5, Prediction.confidence < 0.7), 'Low (50-70%)'),
                 (and_(Prediction.confidence >= 0.7, Prediction.confidence < 0.9), 'High (70-90%)'),
                 (Prediction.confidence >= 0.9, 'Very High (90%+)')],
                else_='Unknown'
            ).label('confidence_range'),
            func.count(Prediction.id).label('count')
        ).group_by('confidence_range').all()
        
        # Average inference time
        avg_inference_time = db.query(func.avg(Prediction.inference_time)).scalar()
        
        # Predictions over time (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_predictions = db.query(
            func.date(Prediction.created_at).label('date'),
            func.count(Prediction.id).label('count'),
            func.avg(Prediction.confidence).label('avg_confidence')
        ).filter(
            Prediction.created_at >= thirty_days_ago
        ).group_by(
            func.date(Prediction.created_at)
        ).order_by(
            func.date(Prediction.created_at)
        ).all()
        
        return {
            "confidence_distribution": [
                {"range": row.confidence_range, "count": row.count}
                for row in confidence_ranges
            ],
            "average_inference_time": float(avg_inference_time) if avg_inference_time else 0.0,
            "daily_predictions": [
                {
                    "date": row.date.isoformat(),
                    "count": row.count,
                    "avg_confidence": float(row.avg_confidence) if row.avg_confidence else 0.0
                }
                for row in daily_predictions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to get model performance metrics")

@router.post("/update-system-stats")
async def update_system_stats(
    model_accuracy: float,
    predictions_processed: int,
    db: Session = Depends(get_db)
):
    """Update system statistics (admin endpoint)"""
    try:
        today = datetime.utcnow().date()
        
        # Check if stats for today already exist
        existing_stats = db.query(SystemStats).filter(
            func.date(SystemStats.date) == today
        ).first()
        
        if existing_stats:
            existing_stats.model_accuracy = model_accuracy
            existing_stats.predictions_processed = predictions_processed
            existing_stats.updated_at = datetime.utcnow()
        else:
            new_stats = SystemStats(
                date=today,
                model_accuracy=model_accuracy,
                predictions_processed=predictions_processed
            )
            db.add(new_stats)
        
        db.commit()
        
        return APIResponse(
            message="System statistics updated successfully",
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error updating system stats: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update system statistics")
