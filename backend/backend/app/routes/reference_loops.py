from fastapi import APIRouter, Query, Depends
from typing import List, Optional
from ..deps import get_db, get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/reference_loops", tags=["reference_loops"])

@router.get("")
async def search_reference_loops(
    bpm: Optional[str] = Query(None),
    style: Optional[str] = Query(None),
    bars: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Search reference loops for Pocket Transfer"""
    # Mock data for now - in production, query your reference loop database
    mock_loops = [
        {"id": "loop_001", "name": "Classic Rock Pocket", "style": "rock", "bpm": 120, "bars": 4, "file_path": "/samples/loops/rock_120.wav"},
        {"id": "loop_002", "name": "Jazz Shuffle", "style": "jazz", "bpm": 140, "bars": 8, "file_path": "/samples/loops/jazz_140.wav"},
        {"id": "loop_003", "name": "Hip Hop Groove", "style": "hip-hop", "bpm": 95, "bars": 2, "file_path": "/samples/loops/hiphop_95.wav"},
        {"id": "loop_004", "name": "Latin Montuno", "style": "latin", "bpm": 110, "bars": 4, "file_path": "/samples/loops/latin_110.wav"},
        {"id": "loop_005", "name": "Funk Pocket", "style": "funk", "bpm": 105, "bars": 4, "file_path": "/samples/loops/funk_105.wav"},
    ]
    
    # Filter based on query parameters
    filtered = mock_loops
    if bpm:
        try:
            bpm_val = int(bpm)
            filtered = [l for l in filtered if abs(l["bpm"] - bpm_val) <= 10]
        except ValueError:
            pass
    
    if style:
        filtered = [l for l in filtered if style.lower() in l["style"].lower()]
    
    if bars:
        try:
            bars_val = int(bars)
            filtered = [l for l in filtered if l["bars"] == bars_val]
        except ValueError:
            pass
    
    return {"items": filtered}

@router.get("/{loop_id}")
async def get_reference_loop(loop_id: str, db: Session = Depends(get_db)):
    """Get specific reference loop details"""
    # Mock implementation
    return {
        "id": loop_id,
        "name": f"Reference Loop {loop_id}",
        "style": "rock",
        "bpm": 120,
        "bars": 4,
        "file_path": f"/samples/loops/{loop_id}.wav",
        "analysis": {
            "timing_variance": 0.02,
            "velocity_curve": [0.8, 0.6, 0.9, 0.7],
            "micro_timing": [0.0, -0.01, 0.005, -0.008]
        }
    }
