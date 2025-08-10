"""
DrumTracKAI v4/v5 Advanced Kits API Routes
User kit management and sample mapping
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from ..models import Kit
from ..deps import get_db, get_current_user, require_admin
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/kits", tags=["kits"])

# Request/Response Models
class KitCreate(BaseModel):
    name: str
    slug: Optional[str] = None
    visibility: str = "private"  # private|project|global
    mapping: Dict[str, str]  # {kick: url, snare: url, ...}

class KitUpdate(BaseModel):
    name: Optional[str] = None
    visibility: Optional[str] = None
    mapping: Optional[Dict[str, str]] = None

class KitResponse(BaseModel):
    id: str
    name: str
    slug: str
    visibility: str
    mapping: Dict[str, str]
    owner_user_id: str
    created_at: str
    updated_at: str

@router.get("/", response_model=List[KitResponse])
async def list_kits(
    request: Request,
    visibility: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List available kits"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        query = db.query(Kit)
        
        if visibility:
            query = query.filter(Kit.visibility == visibility)
        else:
            # Show user's private kits + global kits
            query = query.filter(
                (Kit.owner_user_id == user_id) | (Kit.visibility == "global")
            )
        
        kits = query.all()
        
        return [
            KitResponse(
                id=kit.id,
                name=kit.name,
                slug=kit.slug or kit.name.lower().replace(" ", "_"),
                visibility=kit.visibility,
                mapping=kit.mapping_json,
                owner_user_id=kit.owner_user_id,
                created_at=kit.created_at.isoformat(),
                updated_at=kit.updated_at.isoformat()
            )
            for kit in kits
        ]
        
    except Exception as e:
        logger.error(f"Error listing kits: {e}")
        raise HTTPException(status_code=500, detail="Failed to list kits")

@router.post("/", response_model=KitResponse)
async def create_kit(
    kit_data: KitCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new kit"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        # Generate slug if not provided
        slug = kit_data.slug or kit_data.name.lower().replace(" ", "_")
        
        # Check for duplicate slug
        existing = db.query(Kit).filter(Kit.slug == slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Kit with this slug already exists")
        
        # Validate mapping
        required_drums = ["kick", "snare", "hihat"]
        for drum in required_drums:
            if drum not in kit_data.mapping:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required drum: {drum}"
                )
        
        # Create kit
        kit = Kit(
            owner_user_id=user_id,
            name=kit_data.name,
            slug=slug,
            visibility=kit_data.visibility,
            mapping_json=kit_data.mapping
        )
        
        db.add(kit)
        db.commit()
        db.refresh(kit)
        
        return KitResponse(
            id=kit.id,
            name=kit.name,
            slug=kit.slug,
            visibility=kit.visibility,
            mapping=kit.mapping_json,
            owner_user_id=kit.owner_user_id,
            created_at=kit.created_at.isoformat(),
            updated_at=kit.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating kit: {e}")
        raise HTTPException(status_code=500, detail="Failed to create kit")

@router.get("/{kit_id}", response_model=KitResponse)
async def get_kit(
    kit_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific kit"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        kit = db.query(Kit).filter(Kit.id == kit_id).first()
        if not kit:
            raise HTTPException(status_code=404, detail="Kit not found")
        
        # Check access permissions
        if kit.visibility == "private" and kit.owner_user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return KitResponse(
            id=kit.id,
            name=kit.name,
            slug=kit.slug,
            visibility=kit.visibility,
            mapping=kit.mapping_json,
            owner_user_id=kit.owner_user_id,
            created_at=kit.created_at.isoformat(),
            updated_at=kit.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting kit: {e}")
        raise HTTPException(status_code=500, detail="Failed to get kit")

@router.put("/{kit_id}", response_model=KitResponse)
async def update_kit(
    kit_id: str,
    kit_data: KitUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a kit"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        kit = db.query(Kit).filter(Kit.id == kit_id).first()
        if not kit:
            raise HTTPException(status_code=404, detail="Kit not found")
        
        # Check ownership
        if kit.owner_user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        if kit_data.name is not None:
            kit.name = kit_data.name
        if kit_data.visibility is not None:
            kit.visibility = kit_data.visibility
        if kit_data.mapping is not None:
            kit.mapping_json = kit_data.mapping
        
        db.commit()
        db.refresh(kit)
        
        return KitResponse(
            id=kit.id,
            name=kit.name,
            slug=kit.slug,
            visibility=kit.visibility,
            mapping=kit.mapping_json,
            owner_user_id=kit.owner_user_id,
            created_at=kit.created_at.isoformat(),
            updated_at=kit.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating kit: {e}")
        raise HTTPException(status_code=500, detail="Failed to update kit")

@router.delete("/{kit_id}")
async def delete_kit(
    kit_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a kit"""
    try:
        user = get_current_user(request)
        user_id = user["user_id"]
        
        kit = db.query(Kit).filter(Kit.id == kit_id).first()
        if not kit:
            raise HTTPException(status_code=404, detail="Kit not found")
        
        # Check ownership
        if kit.owner_user_id != user_id and not user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        db.delete(kit)
        db.commit()
        
        return {"message": "Kit deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting kit: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete kit")

@router.get("/presets/default")
async def get_default_kits():
    """Get default preset kits"""
    try:
        # Return default kits from your v4/v5 config
        default_kits = [
            {
                "id": "default_rock",
                "name": "Rock Kit",
                "slug": "rock_kit",
                "visibility": "global",
                "mapping": {
                    "kick": "/samples/drums/kick_rock.wav",
                    "snare": "/samples/drums/snare_rock.wav",
                    "hihat": "/samples/drums/hihat_rock.wav",
                    "crash": "/samples/drums/crash_rock.wav",
                    "ride": "/samples/drums/ride_rock.wav",
                    "tom": "/samples/drums/tom_rock.wav"
                },
                "owner_user_id": "system",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            },
            {
                "id": "default_jazz",
                "name": "Jazz Kit",
                "slug": "jazz_kit",
                "visibility": "global",
                "mapping": {
                    "kick": "/samples/drums/kick_jazz.wav",
                    "snare": "/samples/drums/snare_jazz.wav",
                    "hihat": "/samples/drums/hihat_jazz.wav",
                    "crash": "/samples/drums/crash_jazz.wav",
                    "ride": "/samples/drums/ride_jazz.wav",
                    "tom": "/samples/drums/tom_jazz.wav"
                },
                "owner_user_id": "system",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        ]
        
        return default_kits
        
    except Exception as e:
        logger.error(f"Error getting default kits: {e}")
        raise HTTPException(status_code=500, detail="Failed to get default kits")

@router.post("/{kit_id}/audition")
async def audition_kit(
    kit_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Generate audition preview for a kit"""
    try:
        user = get_current_user(request)
        
        # Get kit
        kit = db.query(Kit).filter(Kit.id == kit_id).first()
        if not kit:
            # Try default kits
            default_kits = await get_default_kits()
            kit_data = next((k for k in default_kits if k["id"] == kit_id), None)
            if not kit_data:
                raise HTTPException(status_code=404, detail="Kit not found")
            mapping = kit_data["mapping"]
        else:
            # Check access
            if kit.visibility == "private" and kit.owner_user_id != user["user_id"]:
                raise HTTPException(status_code=403, detail="Access denied")
            mapping = kit.mapping_json
        
        # Generate simple audition pattern
        audition_pattern = [
            {"lane": "kick", "time_sec": 0.0, "velocity": 100},
            {"lane": "snare", "time_sec": 0.5, "velocity": 90},
            {"lane": "hihat", "time_sec": 0.25, "velocity": 70},
            {"lane": "hihat", "time_sec": 0.75, "velocity": 70},
            {"lane": "kick", "time_sec": 1.0, "velocity": 100},
            {"lane": "snare", "time_sec": 1.5, "velocity": 90},
        ]
        
        return {
            "pattern": audition_pattern,
            "kit_mapping": mapping,
            "duration": 2.0,
            "bpm": 120
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating kit audition: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audition")
