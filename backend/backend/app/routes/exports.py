"""
DrumTracKAI v4/v5 Advanced Exports API Routes
Professional export system with queued jobs
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..models import ExportJob, Job
from ..deps import get_db, get_current_user, get_export_service
from ..services.export_service import ExportService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/exports", tags=["exports"])

# Request/Response Models
class ExportRequest(BaseModel):
    job_id: str
    mode: str  # midi|stems|stereo
    params: Optional[Dict[str, Any]] = {}

class ExportResponse(BaseModel):
    export_id: str
    status: str
    progress: int
    url: Optional[str] = None
    error: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

@router.post("/", response_model=ExportResponse)
async def create_export(
    export_request: ExportRequest,
    request: Request,
    db: Session = Depends(get_db),
    export_service: ExportService = Depends(get_export_service)
):
    """Create a new export job"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Validate job exists and user has access
        job = db.query(Job).filter(Job.id == export_request.job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate export mode
        if export_request.mode not in ["midi", "stems", "stereo"]:
            raise HTTPException(status_code=400, detail="Invalid export mode")
        
        # Create export job
        export_id = export_service.create_export_job(
            job_id=export_request.job_id,
            user_id=user_id,
            mode=export_request.mode,
            params=export_request.params,
            db=db
        )
        
        # Get initial status
        status = export_service.get_export_status(export_id, db)
        
        return ExportResponse(
            export_id=export_id,
            status=status["status"],
            progress=status["progress"],
            url=status["url"],
            error=status["error"],
            created_at=status["created_at"],
            updated_at=status["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating export: {e}")
        raise HTTPException(status_code=500, detail="Failed to create export")

@router.get("/{export_id}", response_model=ExportResponse)
async def get_export_status(
    export_id: str,
    request: Request,
    db: Session = Depends(get_db),
    export_service: ExportService = Depends(get_export_service)
):
    """Get export job status"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Get export job
        export_job = db.query(ExportJob).filter(ExportJob.id == export_id).first()
        if not export_job:
            raise HTTPException(status_code=404, detail="Export job not found")
        
        # Check access
        if export_job.user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get status
        status = export_service.get_export_status(export_id, db)
        
        return ExportResponse(
            export_id=export_id,
            status=status["status"],
            progress=status["progress"],
            url=status["url"],
            error=status["error"],
            created_at=status["created_at"],
            updated_at=status["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get export status")

@router.get("/", response_model=List[ExportResponse])
async def list_exports(
    request: Request,
    job_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    export_service: ExportService = Depends(get_export_service)
):
    """List user's export jobs"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        query = db.query(ExportJob).filter(ExportJob.user_id == user_id)
        
        if job_id:
            query = query.filter(ExportJob.job_id == job_id)
        
        if status:
            query = query.filter(ExportJob.status == status)
        
        export_jobs = query.order_by(ExportJob.created_at.desc()).limit(limit).all()
        
        results = []
        for ej in export_jobs:
            try:
                status_data = export_service.get_export_status(ej.id, db)
                results.append(ExportResponse(
                    export_id=ej.id,
                    status=status_data["status"],
                    progress=status_data["progress"],
                    url=status_data["url"],
                    error=status_data["error"],
                    created_at=status_data["created_at"],
                    updated_at=status_data["updated_at"]
                ))
            except Exception as e:
                logger.warning(f"Error getting status for export {ej.id}: {e}")
                continue
        
        return results
        
    except Exception as e:
        logger.error(f"Error listing exports: {e}")
        raise HTTPException(status_code=500, detail="Failed to list exports")

@router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    request: Request,
    db: Session = Depends(get_db),
    export_service: ExportService = Depends(get_export_service)
):
    """Download completed export"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Get export job
        export_job = db.query(ExportJob).filter(ExportJob.id == export_id).first()
        if not export_job:
            raise HTTPException(status_code=404, detail="Export job not found")
        
        # Check access
        if export_job.user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if export is complete
        if export_job.status != "done":
            raise HTTPException(status_code=400, detail="Export not complete")
        
        if not export_job.result_path:
            raise HTTPException(status_code=404, detail="Export file not found")
        
        # Return file
        from pathlib import Path
        file_path = Path(export_job.result_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Export file not found")
        
        # Determine filename and media type
        if export_job.mode == "midi":
            filename = f"drums_midi_{export_id[:8]}.zip"
            media_type = "application/zip"
        elif export_job.mode == "stems":
            filename = f"drums_stems_{export_id[:8]}.zip"
            media_type = "application/zip"
        elif export_job.mode == "stereo":
            filename = f"drums_stereo_{export_id[:8]}.wav"
            media_type = "audio/wav"
        else:
            filename = f"drums_export_{export_id[:8]}"
            media_type = "application/octet-stream"
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading export: {e}")
        raise HTTPException(status_code=500, detail="Failed to download export")

@router.delete("/{export_id}")
async def delete_export(
    export_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete an export job"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Get export job
        export_job = db.query(ExportJob).filter(ExportJob.id == export_id).first()
        if not export_job:
            raise HTTPException(status_code=404, detail="Export job not found")
        
        # Check access
        if export_job.user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete file if it exists
        if export_job.result_path:
            from pathlib import Path
            file_path = Path(export_job.result_path)
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete export file {file_path}: {e}")
        
        # Delete database record
        db.delete(export_job)
        db.commit()
        
        return {"message": "Export deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting export: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete export")

@router.get("/presets/default")
async def get_export_presets():
    """Get default export presets"""
    try:
        presets = {
            "midi": {
                "name": "MIDI Export",
                "description": "Export drum patterns as MIDI files",
                "params": {
                    "quantize": True,
                    "include_velocity": True,
                    "separate_files": True
                }
            },
            "stems": {
                "name": "Stems Export",
                "description": "Export individual drum tracks as audio stems",
                "params": {
                    "format": "wav",
                    "bit_depth": 24,
                    "sample_rate": 48000,
                    "normalize": True
                }
            },
            "stereo": {
                "name": "Stereo Mix",
                "description": "Export final stereo drum mix",
                "params": {
                    "format": "wav",
                    "bit_depth": 24,
                    "sample_rate": 48000,
                    "normalize": True,
                    "apply_master_fx": True
                }
            }
        }
        
        return presets
        
    except Exception as e:
        logger.error(f"Error getting export presets: {e}")
        raise HTTPException(status_code=500, detail="Failed to get export presets")
