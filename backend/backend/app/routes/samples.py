from fastapi import APIRouter
from pathlib import Path

router = APIRouter(prefix="/api/samples")

@router.get("/kits/default")
async def list_default_kit():
    """
    Lists a conventional drum kit from /samples/kits/default/*
    """
    base = Path("/app/samples/kits/default")
    lanes = ["kick","snare","hihat","tom","ride","crash"]
    out = {}
    for l in lanes:
        p = base / f"{l}.wav"
        if p.exists():
            out[l] = f"/samples/kits/default/{l}.wav"
    return {"kit_map": out, "lanes": lanes}

@router.get("/dirs")
async def list_dirs():
    """
    Lists subfolders under /samples to help QA quickly browse assets
    """
    base = Path("/app/samples")
    return {"dirs": [f"/samples/{p.name}/" for p in base.iterdir() if p.is_dir()]}
