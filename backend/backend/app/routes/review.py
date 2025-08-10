from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from ..deps import get_db, get_current_user
from sqlalchemy.orm import Session
from ..models import ReviewComment
from datetime import datetime

router = APIRouter(prefix="/api/review", tags=["review"])

@router.get("/comments")
async def get_comments(
    job_id: str = Query(...),
    section_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get review comments for a job/section"""
    # Mock data for now - in production, query ReviewComment table
    mock_comments = [
        {
            "id": "comment_001",
            "job_id": job_id,
            "section_id": section_id or "all",
            "time_sec": 15.5,
            "text": "Great snare hit here, could use more velocity variation",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "comment_002", 
            "job_id": job_id,
            "section_id": section_id or "all",
            "time_sec": 32.2,
            "text": "Kick pattern feels rushed, try pulling back slightly",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return {"items": mock_comments}

@router.post("/comments")
async def add_comment(
    comment_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a new review comment"""
    # Mock implementation - in production, create ReviewComment record
    new_comment = {
        "id": f"comment_{datetime.now().timestamp()}",
        "job_id": comment_data.get("job_id"),
        "section_id": comment_data.get("section_id", "all"),
        "time_sec": comment_data.get("time_sec", 0),
        "text": comment_data.get("text", ""),
        "user_id": current_user.get("sub", "anonymous"),
        "created_at": datetime.now().isoformat()
    }
    
    return new_comment

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a review comment"""
    # Mock implementation
    return {"message": f"Comment {comment_id} deleted"}
