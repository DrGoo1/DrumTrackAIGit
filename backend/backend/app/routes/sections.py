from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db, get_current_user
from ..models import Snapshot
from datetime import datetime

router = APIRouter(prefix="/api/sections")

# We persist arrangement & tempo as a small state blob in Snapshots for now
# (keeps schema simple; you can migrate to dedicated tables later)

@router.get("")
async def get_sections(job_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    s = db.query(Snapshot).filter(Snapshot.job_id==job_id).order_by(Snapshot.created_at.desc()).first()
    if not s or not s.state_json:
        return {"sections": [], "tempo_points": []}
    st = s.state_json or {}
    return {
        "sections": st.get("sections", []),
        "tempo_points": st.get("tempo_points", [])
    }

@router.post("")
async def save_sections(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    job_id = payload.get("job_id")
    if not job_id:
        raise HTTPException(400, "job_id required")
    state = {
        "sections": payload.get("sections", []),      # [{id,type,start_sec,end_sec,style,fill_in,fill_out,...}]
        "tempo_points": payload.get("tempo_points", []) # [{sec,bpm}]
    }
    snap = Snapshot(job_id=job_id, user_id=user["user_id"], name="arrangement+tempo", state_json=state)
    db.add(snap); db.commit()
    return {"ok": True, "snapshot_id": snap.id}
