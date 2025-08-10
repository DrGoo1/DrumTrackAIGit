from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ..deps import get_db
from ..models import Kit
from pathlib import Path

router = APIRouter(prefix="/api/devseed")

@router.post("")
async def seed(db: Session = Depends(get_db)):
    base = Path("/app/samples/kits/default")
    lanes = ["kick","snare","hihat","tom","ride","crash"]
    mapping = {}
    for l in lanes:
        p = base / f"{l}.wav"
        if p.exists():
            mapping[l] = f"/samples/kits/default/{l}.wav"
    k = Kit(owner_user_id="dev-user", name="Default Dev Kit", slug="default-dev", visibility="global", mapping_json=mapping, updated_at=datetime.utcnow())
    db.add(k); db.commit()
    return {"ok": True, "kit_id": k.id, "mapping": mapping}
