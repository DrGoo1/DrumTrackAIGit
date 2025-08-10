"""
DrumTracKAI v4/v5 Advanced Impulse Response API Routes
Professional reverb and convolution management
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..models import ImpulseResponse
from ..deps import get_db, get_current_user, require_admin
import os
import shutil
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/irs", tags=["impulse_responses"])

# Request/Response Models
class IRResponse(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str]
    is_public: bool
    uploaded_by: str
    created_at: str

class IRUpload(BaseModel):
    name: str
    category: str = "room"  # room|hall|plate|spring
    description: Optional[str] = None
    is_public: bool = False

@router.get("/", response_model=List[IRResponse])
async def list_irs(
    request: Request,
    category: Optional[str] = None,
    public_only: bool = False,
    db: Session = Depends(get_db)
):
    """List available impulse responses"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        query = db.query(ImpulseResponse)
        
        if category:
            query = query.filter(ImpulseResponse.category == category)
        
        if public_only:
            query = query.filter(ImpulseResponse.is_public == True)
        else:
            # Show user's private IRs + public IRs
            query = query.filter(
                (ImpulseResponse.uploaded_by == user_id) | 
                (ImpulseResponse.is_public == True)
            )
        
        irs = query.all()
        
        return [
            IRResponse(
                id=ir.id,
                name=ir.name,
                category=ir.category,
                description=ir.description,
                is_public=ir.is_public,
                uploaded_by=ir.uploaded_by,
                created_at=ir.created_at.isoformat()
            )
            for ir in irs
        ]
        
    except Exception as e:
        logger.error(f"Error listing IRs: {e}")
        raise HTTPException(status_code=500, detail="Failed to list impulse responses")

@router.post("/upload", response_model=IRResponse)
async def upload_ir(
    request: Request,
    file: UploadFile = File(...),
    name: str = "",
    category: str = "room",
    description: str = "",
    is_public: bool = False,
    db: Session = Depends(get_db)
):
    """Upload a new impulse response file"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Only admins can upload public IRs
        if is_public and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin privileges required for public IRs")
        
        # Validate file type
        if not file.filename.lower().endswith(('.wav', '.aiff', '.flac')):
            raise HTTPException(status_code=400, detail="Invalid file type. Use WAV, AIFF, or FLAC")
        
        # Create IR directory if it doesn't exist
        ir_dir = Path("/app/irs")
        ir_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        file_path = ir_dir / f"{file_id}{file_extension}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database record
        ir = ImpulseResponse(
            name=name or file.filename,
            file_path=str(file_path),
            category=category,
            description=description,
            uploaded_by=user_id,
            is_public=is_public
        )
        
        db.add(ir)
        db.commit()
        db.refresh(ir)
        
        return IRResponse(
            id=ir.id,
            name=ir.name,
            category=ir.category,
            description=ir.description,
            is_public=ir.is_public,
            uploaded_by=ir.uploaded_by,
            created_at=ir.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading IR: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload impulse response")

@router.get("/{ir_id}", response_model=IRResponse)
async def get_ir(
    ir_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get impulse response details"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        ir = db.query(ImpulseResponse).filter(ImpulseResponse.id == ir_id).first()
        if not ir:
            raise HTTPException(status_code=404, detail="Impulse response not found")
        
        # Check access
        if not ir.is_public and ir.uploaded_by != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return IRResponse(
            id=ir.id,
            name=ir.name,
            category=ir.category,
            description=ir.description,
            is_public=ir.is_public,
            uploaded_by=ir.uploaded_by,
            created_at=ir.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting IR: {e}")
        raise HTTPException(status_code=500, detail="Failed to get impulse response")

@router.get("/{ir_id}/download")
async def download_ir(
    ir_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Download impulse response file"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        ir = db.query(ImpulseResponse).filter(ImpulseResponse.id == ir_id).first()
        if not ir:
            raise HTTPException(status_code=404, detail="Impulse response not found")
        
        # Check access
        if not ir.is_public and ir.uploaded_by != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists
        file_path = Path(ir.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="IR file not found")
        
        return FileResponse(
            path=str(file_path),
            filename=f"{ir.name}{file_path.suffix}",
            media_type="audio/wav"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading IR: {e}")
        raise HTTPException(status_code=500, detail="Failed to download impulse response")

@router.delete("/{ir_id}")
async def delete_ir(
    ir_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete an impulse response"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        ir = db.query(ImpulseResponse).filter(ImpulseResponse.id == ir_id).first()
        if not ir:
            raise HTTPException(status_code=404, detail="Impulse response not found")
        
        # Check permissions
        if ir.uploaded_by != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete file
        file_path = Path(ir.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete IR file {file_path}: {e}")
        
        # Delete database record
        db.delete(ir)
        db.commit()
        
        return {"message": "Impulse response deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting IR: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete impulse response")

@router.get("/categories/list")
async def list_ir_categories():
    """Get available IR categories"""
    return {
        "categories": [
            {"id": "room", "name": "Room", "description": "Small to medium room reverbs"},
            {"id": "hall", "name": "Hall", "description": "Large hall and concert hall reverbs"},
            {"id": "plate", "name": "Plate", "description": "Classic plate reverb emulations"},
            {"id": "spring", "name": "Spring", "description": "Vintage spring reverb tanks"},
            {"id": "chamber", "name": "Chamber", "description": "Echo chambers and unique spaces"},
            {"id": "algorithmic", "name": "Algorithmic", "description": "Synthetic algorithmic reverbs"}
        ]
    }

@router.get("/presets/default")
async def get_default_irs():
    """Get default/built-in impulse responses"""
    return {
        "default_irs": [
            {
                "id": "default_room",
                "name": "Studio Room",
                "category": "room",
                "description": "Classic studio room reverb",
                "is_public": True,
                "uploaded_by": "system"
            },
            {
                "id": "default_hall",
                "name": "Concert Hall",
                "category": "hall", 
                "description": "Large concert hall reverb",
                "is_public": True,
                "uploaded_by": "system"
            },
            {
                "id": "default_plate",
                "name": "Vintage Plate",
                "category": "plate",
                "description": "Classic EMT 140 plate reverb",
                "is_public": True,
                "uploaded_by": "system"
            }
        ]
    }
