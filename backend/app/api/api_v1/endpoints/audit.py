"""
Audit logging and system monitoring endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.models.database import AuditLog, Patient, Prediction, SystemStats, WeeklyStats
from app.models.schemas import (
    AuditLogResponse, PaginatedResponse, 
    SystemStatsResponse, WeeklyStatsResponse,
    DashboardStats, OverviewStats, PredictionResponse,
    MonthlyAccuracy
)

router = APIRouter()

@router.get("/logs", response_model=PaginatedResponse[AuditLogResponse])
async def get_audit_logs(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    """Get paginated audit logs with filters"""
    try:
        query = db.query(AuditLog)
        
        # Apply filters
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if action:
            query = query.filter(AuditLog.action_type == action)
        
        if resource_type:
            query = query.filter(AuditLog.entity_type == resource_type)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        # Order by most recent
        query = query.order_by(desc(AuditLog.timestamp))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        logs = query.offset(offset).limit(size).all()
        
        # Calculate pages
        pages = (total + size - 1) // size
        
        return PaginatedResponse(
            items=logs,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit logs: {str(e)}")

@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log(log_id: int, db: Session = Depends(get_db)):
    """Get specific audit log by ID"""
    try:
        log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        return log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit log: {str(e)}")

@router.get("/logs/actions")
async def get_audit_actions(db: Session = Depends(get_db)):
    """Get list of all available audit actions"""
    try:
        actions = db.query(AuditLog.action_type).distinct().all()
        return {
            "actions": [action[0] for action in actions if action[0]],
            "total": len(actions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit actions: {str(e)}")

@router.get("/logs/users")
async def get_audit_users(db: Session = Depends(get_db)):
    """Get list of all users who have audit logs"""
    try:
        users = db.query(AuditLog.user_id).distinct().all()
        return {
            "users": [user[0] for user in users if user[0]],
            "total": len(users)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audit users: {str(e)}")

@router.get("/logs/stats")
async def get_audit_statistics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get audit log statistics for the specified number of days"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total logs in period
        total_logs = db.query(AuditLog).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).count()
        
        # Logs by action
        action_stats = db.query(
            AuditLog.action_type,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).group_by(AuditLog.action_type).all()
        
        # Logs by user
        user_stats = db.query(
            AuditLog.user_id,
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).group_by(AuditLog.user_id).all()
        
        # Daily activity
        daily_stats = db.query(
            func.date(AuditLog.timestamp).label('date'),
            func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).group_by(func.date(AuditLog.timestamp)).all()
        
        return {
            "period_days": days,
            "start_date": start_date.date(),
            "end_date": end_date.date(),
            "total_logs": total_logs,
            "actions": [{"action": row.action_type, "count": row.count} for row in action_stats],
            "users": [{"user_id": row.user_id, "count": row.count} for row in user_stats],
            "daily_activity": [{"date": str(row.date), "count": row.count} for row in daily_stats]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating audit statistics: {str(e)}")

@router.get("/system/stats", response_model=SystemStatsResponse)
async def get_system_stats(db: Session = Depends(get_db)):
    """Get latest system statistics"""
    try:
        # Get latest system stats
        latest_stats = db.query(SystemStats).order_by(desc(SystemStats.date)).first()
        
        if not latest_stats:
            # Return default stats if none exist
            return SystemStatsResponse(
                date=datetime.utcnow().date(),
                total_patients=0,
                total_predictions=0,
                daily_predictions=0,
                model_accuracy=0.94,
                system_uptime=0,
                memory_usage=0,
                cpu_usage=0,
                disk_usage=0
            )
        
        return latest_stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving system stats: {str(e)}")

@router.get("/system/weekly", response_model=List[WeeklyStatsResponse])
async def get_weekly_stats(
    weeks: int = Query(12, ge=1, le=52),
    db: Session = Depends(get_db)
):
    """Get weekly statistics for the specified number of weeks"""
    try:
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        weekly_stats = db.query(WeeklyStats).filter(
            WeeklyStats.week_start >= start_date,
            WeeklyStats.week_start <= end_date
        ).order_by(desc(WeeklyStats.week_start)).all()
        
        return weekly_stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving weekly stats: {str(e)}")

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get comprehensive dashboard statistics"""
    try:
        # Date ranges
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Patient stats
        total_patients = db.query(Patient).count()
        patients_this_week = db.query(Patient).filter(
            func.date(Patient.created_at) >= week_start
        ).count()
        patients_this_month = db.query(Patient).filter(
            func.date(Patient.created_at) >= month_start
        ).count()
        
        # Prediction stats
        total_predictions = db.query(Prediction).count()
        predictions_today = db.query(Prediction).filter(
            func.date(Prediction.created_at) == today
        ).count()
        predictions_this_week = db.query(Prediction).filter(
            func.date(Prediction.created_at) >= week_start
        ).count()
        predictions_this_month = db.query(Prediction).filter(
            func.date(Prediction.created_at) >= month_start
        ).count()
        
        # Prediction type breakdown
        pneumonia_cases = db.query(Prediction).filter(
            Prediction.prediction == "PNEUMONIA"
        ).count()
        normal_cases = db.query(Prediction).filter(
            Prediction.prediction == "NORMAL"
        ).count()
        
        # Accuracy and confidence
        avg_confidence_result = db.query(func.avg(Prediction.confidence)).scalar()
        average_confidence = float(avg_confidence_result) if avg_confidence_result else 0
        
        # Recent activity
        recent_patients = db.query(Patient).order_by(desc(Patient.created_at)).limit(5).all()
        recent_predictions = db.query(Prediction).order_by(desc(Prediction.created_at)).limit(5).all()
        
        # System performance (mock data)
        model_accuracy = 0.945
        
        # Create proper OverviewStats object
        overview_stats = OverviewStats(
            total_patients=total_patients,
            total_predictions=total_predictions,
            predictions_today=predictions_today,
            pneumonia_cases=pneumonia_cases,
            normal_cases=normal_cases,
            average_confidence=round(average_confidence, 3),
            model_accuracy=model_accuracy,
            active_users=5  # Mock active users
        )
        
        # Get recent predictions properly formatted
        recent_predictions_list = []
        for p in recent_predictions:
            pred_response = PredictionResponse(
                id=p.id,
                patient_id=p.patient_id,
                image_filename=p.image_filename,
                original_filename=p.original_filename,
                prediction=p.prediction,
                confidence=p.confidence,
                confidence_scores=p.confidence_scores or {},
                inference_time=p.inference_time,
                image_size=p.image_size,
                clinical_notes=p.clinical_notes,
                reviewed=p.reviewed,
                reviewed_by=p.reviewed_by,
                reviewed_at=p.reviewed_at,
                created_at=p.created_at,
                patient_info={
                    "first_name": p.patient.first_name if p.patient else "Unknown",
                    "last_name": p.patient.last_name if p.patient else "Patient"
                } if p.patient else None
            )
            recent_predictions_list.append(pred_response)
        
        # Get weekly trends - for now return empty list (could be implemented later)
        weekly_trends = []
        
        # Get monthly accuracy - for now return empty list (could be implemented later)  
        monthly_accuracy = []
        
        return DashboardStats(
            overview=overview_stats,
            recent_predictions=recent_predictions_list,
            weekly_trends=weekly_trends,
            monthly_accuracy=monthly_accuracy
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving dashboard stats: {str(e)}")

@router.post("/system/update-stats")
async def update_system_stats(db: Session = Depends(get_db)):
    """Update system statistics (typically called by a scheduled job)"""
    try:
        today = datetime.utcnow().date()
        
        # Calculate current stats
        total_patients = db.query(Patient).count()
        total_predictions = db.query(Prediction).count()
        daily_predictions = db.query(Prediction).filter(
            func.date(Prediction.created_at) == today
        ).count()
        
        # Check if stats for today already exist
        existing_stats = db.query(SystemStats).filter(SystemStats.date == today).first()
        
        if existing_stats:
            # Update existing
            existing_stats.total_patients = total_patients
            existing_stats.total_predictions = total_predictions
            existing_stats.daily_predictions = daily_predictions
        else:
            # Create new
            new_stats = SystemStats(
                date=today,
                total_patients=total_patients,
                total_predictions=total_predictions,
                daily_predictions=daily_predictions,
                model_accuracy=0.945,  # Mock value
                system_uptime=99.8,    # Mock value
                memory_usage=45.2,     # Mock value
                cpu_usage=23.1,        # Mock value
                disk_usage=67.8        # Mock value
            )
            db.add(new_stats)
        
        db.commit()
        
        return {"message": "System statistics updated successfully", "date": today}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating system stats: {str(e)}")

@router.delete("/logs/cleanup")
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db)
):
    """Clean up audit logs older than specified days"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Count logs to be deleted
        count = db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).count()
        
        # Delete old logs
        db.query(AuditLog).filter(AuditLog.timestamp < cutoff_date).delete()
        db.commit()
        
        return {
            "message": f"Cleaned up {count} audit logs older than {days} days",
            "cutoff_date": cutoff_date.date(),
            "deleted_count": count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cleaning up logs: {str(e)}")
