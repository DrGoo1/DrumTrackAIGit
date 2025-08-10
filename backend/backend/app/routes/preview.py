from fastapi import APIRouter, Body, HTTPException
from pathlib import Path
import json
import tempfile
import os

router = APIRouter(prefix="/api/preview")

@router.post("/render")
async def render_preview(payload: dict = Body(...)):
    """
    Render ~4 bars to a temp WAV for instant QA without touching the export queue.
    """
    bpm = float(payload.get("bpm", 120))
    bars = int(payload.get("bars", 4))
    sr = 48000
    dur_sec = (60.0 / bpm) * 4 * bars  # 4/4 bars
    
    # Mock implementation for now - in production, use RenderEngine
    job_id = f"preview_{payload.get('job_id','temp')}"
    out_dir = Path("/app/exports") / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a mock preview file (in production, render actual audio)
    preview_file = out_dir / "preview.wav"
    
    # For now, create a placeholder file
    with open(preview_file, 'wb') as f:
        # Write minimal WAV header for a silent file
        f.write(b'RIFF')
        f.write((36).to_bytes(4, 'little'))  # File size - 8
        f.write(b'WAVE')
        f.write(b'fmt ')
        f.write((16).to_bytes(4, 'little'))  # Subchunk1Size
        f.write((1).to_bytes(2, 'little'))   # AudioFormat (PCM)
        f.write((2).to_bytes(2, 'little'))   # NumChannels (stereo)
        f.write((sr).to_bytes(4, 'little'))  # SampleRate
        f.write((sr * 2 * 2).to_bytes(4, 'little'))  # ByteRate
        f.write((4).to_bytes(2, 'little'))   # BlockAlign
        f.write((16).to_bytes(2, 'little'))  # BitsPerSample
        f.write(b'data')
        f.write((0).to_bytes(4, 'little'))   # Subchunk2Size (no data)
    
    return {"url": f"/exports/{job_id}/preview.wav", "duration_sec": dur_sec}
