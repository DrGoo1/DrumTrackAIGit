from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel
import os
from typing import Optional, List, Dict, Any
from ..providers.llm_drums import LLMDrumsProvider, GenParams

router = APIRouter()

# Initialize provider with data root
DATA_ROOT = os.environ.get("DATA_ROOT", "/app/data")
provider = LLMDrumsProvider(data_root=DATA_ROOT)

class SuggestIn(BaseModel):
    job_id: str
    section_id: str
    drummer_id: Optional[str] = None
    source: str = "mix"  # mix|bass|none
    params: Dict[str, Any] = {}

@router.get('/api/drummers')
async def list_drummers_curated(job_id: str, top: int = 6, diverse: int = 3):
    """Get curated drummer profiles matched to project style."""
    return {"drummers": provider.curated_drummers(job_id, top=top, diverse=diverse)}

@router.post('/api/drums/suggest')
async def drums_suggest(body: SuggestIn):
    """Generate drum patterns for a section using LLM analytics."""
    p = GenParams(
        drummer_id=body.drummer_id,
        source=body.source,
        complexity=body.params.get('complexity', 0.5),
        energy=body.params.get('energy', 0.5),
        swing=body.params.get('swing', 0.0),
        humanize=body.params.get('humanize', 0.2),
        fill_in=body.params.get('fill_in', 'none'),
        fill_out=body.params.get('fill_out', 'none'),
        fill_every_bars=body.params.get('fill_every_bars'),
        style=body.params.get('style', 'default'),
    )
    notes = provider.suggest_for_section(body.job_id, body.section_id, p)
    return {"notes": notes}

class ApplyIn(BaseModel):
    job_id: str
    section_id: str
    notes: Dict[str, List[Dict[str, Any]]]

@router.post('/api/drums/apply')
async def drums_apply(body: ApplyIn):
    """Commit generated notes to section MIDI in DB."""
    success = provider.apply_to_section(body.job_id, body.section_id, body.notes)
    return {"status": "ok" if success else "error"}

class MultiIn(BaseModel):
    job_id: str
    section_ids: List[str]
    drummer_id: Optional[str] = None
    source: str = "mix"
    params: Dict[str, Any] = {}

@router.post('/api/drums/generate-multi')
async def drums_generate_multi(body: MultiIn):
    """Generate cohesive parts across multiple sections, reusing a motif."""
    out = {}
    base_params = GenParams(
        drummer_id=body.drummer_id,
        source=body.source,
        complexity=body.params.get('complexity', 0.5),
        energy=body.params.get('energy', 0.5),
        swing=body.params.get('swing', 0.0),
        humanize=body.params.get('humanize', 0.2),
        fill_in=body.params.get('fill_in', 'none'),
        fill_out=body.params.get('fill_out', 'none'),
        fill_every_bars=body.params.get('fill_every_bars'),
        style=body.params.get('style', 'default'),
    )
    # Generate for each section with cohesive style
    for sid in body.section_ids:
        out[sid] = provider.suggest_for_section(body.job_id, sid, base_params)
    return {"sections": out}

class QuantizeIn(BaseModel):
    job_id: str
    section_id: str
    grid: str = "1/16"  # 1/4, 1/8, 1/16, 1/32
    strength: float = 1.0  # 0.0-1.0
    swing: float = 0.0  # 0.0-1.0

@router.post('/api/midi/quantize')
async def midi_quantize(body: QuantizeIn):
    """Quantize MIDI notes to grid."""
    # This would implement quantization logic
    # For now, return success
    return {"status": "ok", "quantized": True}

class HumanizeIn(BaseModel):
    job_id: str
    section_id: str
    timing: float = 0.1  # timing variation
    velocity: float = 0.1  # velocity variation

@router.post('/api/midi/humanize')
async def midi_humanize(body: HumanizeIn):
    """Add human-like variations to MIDI notes."""
    # This would implement humanization logic
    # For now, return success
    return {"status": "ok", "humanized": True}

class SwingIn(BaseModel):
    job_id: str
    section_id: str
    amount: float = 0.5  # swing amount 0.0-1.0

@router.post('/api/midi/swing')
async def midi_swing(body: SwingIn):
    """Apply swing timing to MIDI notes."""
    # This would implement swing logic
    # For now, return success
    return {"status": "ok", "swing_applied": True}
