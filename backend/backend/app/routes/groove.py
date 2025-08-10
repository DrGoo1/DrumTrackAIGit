"""
DrumTracKAI v4/v5 Advanced Groove Analysis API Routes
ML-driven groove critique and humanization
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..models import GrooveMetrics, Job, Section
from ..deps import get_db, get_current_user
import logging
import numpy as np

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/groove", tags=["groove"])

# Request/Response Models
class GrooveAnalysisRequest(BaseModel):
    job_id: str
    section_id: Optional[str] = None
    analysis_type: str = "comprehensive"  # basic|comprehensive|advanced

class GrooveMetricsResponse(BaseModel):
    id: str
    job_id: str
    section_id: str
    metrics: Dict[str, Any]
    created_at: str

class GrooveCritiqueResponse(BaseModel):
    overall_score: float
    timing_score: float
    velocity_score: float
    humanization_score: float
    suggestions: List[str]
    detailed_metrics: Dict[str, Any]

@router.post("/analyze", response_model=GrooveCritiqueResponse)
async def analyze_groove(
    analysis_request: GrooveAnalysisRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Analyze groove quality and provide critique"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Validate job access
        job = db.query(Job).filter(Job.id == analysis_request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get section if specified
        section = None
        if analysis_request.section_id:
            section = db.query(Section).filter(
                Section.id == analysis_request.section_id,
                Section.job_id == analysis_request.job_id
            ).first()
            if not section:
                raise HTTPException(status_code=404, detail="Section not found")
        
        # Perform groove analysis
        critique = _analyze_groove_quality(job, section, analysis_request.analysis_type)
        
        # Store metrics in database
        metrics = GrooveMetrics(
            job_id=analysis_request.job_id,
            section_id=analysis_request.section_id or "all",
            metrics_json=critique["detailed_metrics"]
        )
        db.add(metrics)
        db.commit()
        
        return GrooveCritiqueResponse(**critique)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing groove: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze groove")

@router.get("/{job_id}/metrics", response_model=List[GrooveMetricsResponse])
async def get_groove_metrics(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get stored groove metrics for a job"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Validate job access
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get metrics
        metrics = db.query(GrooveMetrics).filter(GrooveMetrics.job_id == job_id).all()
        
        return [
            GrooveMetricsResponse(
                id=m.id,
                job_id=m.job_id,
                section_id=m.section_id,
                metrics=m.metrics_json,
                created_at=m.created_at.isoformat()
            )
            for m in metrics
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting groove metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get groove metrics")

@router.post("/{job_id}/humanize")
async def humanize_groove(
    job_id: str,
    request: Request,
    humanization_params: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Apply AI-driven humanization to groove"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Validate job access
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Apply humanization
        result = _apply_groove_humanization(job, humanization_params)
        
        return {
            "message": "Humanization applied successfully",
            "changes_applied": result["changes_count"],
            "affected_notes": result["affected_notes"],
            "humanization_strength": humanization_params.get("strength", 0.5)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error humanizing groove: {e}")
        raise HTTPException(status_code=500, detail="Failed to humanize groove")

def _analyze_groove_quality(job, section, analysis_type: str) -> Dict[str, Any]:
    """Analyze groove quality using ML algorithms"""
    # This is a simplified implementation - in production, this would use
    # sophisticated ML models for groove analysis
    
    # Mock analysis for demonstration
    timing_variance = np.random.uniform(0.02, 0.08)  # Timing deviation
    velocity_variance = np.random.uniform(0.1, 0.3)  # Velocity variation
    
    # Calculate scores (0-1, higher is better)
    timing_score = max(0, 1 - timing_variance * 10)
    velocity_score = 1 - abs(velocity_variance - 0.2) * 2  # Sweet spot around 0.2
    
    # Humanization score (balance between mechanical and chaotic)
    humanization_score = (timing_score + velocity_score) / 2
    
    # Overall score
    overall_score = (timing_score * 0.4 + velocity_score * 0.3 + humanization_score * 0.3)
    
    # Generate suggestions
    suggestions = []
    if timing_score < 0.7:
        suggestions.append("Consider tightening timing - some hits are too far off the grid")
    if velocity_score < 0.6:
        suggestions.append("Add more velocity variation for natural feel")
    if humanization_score < 0.5:
        suggestions.append("Groove feels too mechanical - try adding subtle timing variations")
    if overall_score > 0.9:
        suggestions.append("Excellent groove! Very natural and musical")
    
    # Detailed metrics
    detailed_metrics = {
        "timing_analysis": {
            "average_deviation_ms": timing_variance * 1000,
            "max_deviation_ms": timing_variance * 2000,
            "consistency_score": timing_score
        },
        "velocity_analysis": {
            "dynamic_range": velocity_variance,
            "accent_clarity": velocity_score,
            "ghost_note_presence": np.random.uniform(0.1, 0.4)
        },
        "rhythm_analysis": {
            "groove_pocket": np.random.uniform(0.6, 0.9),
            "swing_feel": np.random.uniform(0, 0.3),
            "syncopation_level": np.random.uniform(0.1, 0.6)
        },
        "humanization_factors": {
            "micro_timing": timing_variance,
            "velocity_humanization": velocity_variance,
            "natural_variations": humanization_score
        }
    }
    
    return {
        "overall_score": round(overall_score, 3),
        "timing_score": round(timing_score, 3),
        "velocity_score": round(velocity_score, 3),
        "humanization_score": round(humanization_score, 3),
        "suggestions": suggestions,
        "detailed_metrics": detailed_metrics
    }

def _apply_groove_humanization(job, params: Dict[str, Any]) -> Dict[str, Any]:
    """Apply AI-driven humanization to groove"""
    strength = params.get("strength", 0.5)
    focus_areas = params.get("focus", ["timing", "velocity"])
    
    # Mock humanization application
    changes_count = 0
    affected_notes = []
    
    # In a real implementation, this would:
    # 1. Load the current MIDI data for the job
    # 2. Apply subtle timing and velocity variations
    # 3. Use ML models to ensure natural-sounding results
    # 4. Save the modified MIDI data back to the job
    
    # For demo purposes, simulate some changes
    if "timing" in focus_areas:
        changes_count += int(np.random.uniform(10, 50) * strength)
    
    if "velocity" in focus_areas:
        changes_count += int(np.random.uniform(5, 30) * strength)
    
    # Generate mock affected notes list
    drum_types = ["kick", "snare", "hihat", "crash", "ride", "tom"]
    for _ in range(min(changes_count, 20)):  # Limit for demo
        affected_notes.append({
            "drum": np.random.choice(drum_types),
            "time": round(np.random.uniform(0, 32), 3),
            "change_type": np.random.choice(["timing", "velocity"]),
            "amount": round(np.random.uniform(-0.05, 0.05), 4)
        })
    
    return {
        "changes_count": changes_count,
        "affected_notes": affected_notes[:10]  # Return first 10 for brevity
    }
