from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add the drum_custom modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'GPT-5', 'Files_for_ChatGPT', 'drum_custom', 'More'))

# === Imports from your stack ===
# Adjust these names if your modules expose different classes/functions
try:
    from advanced_drummer_analysis import PhasedDrumAnalysis
except ImportError:
    try:
        from phased_drum_analysis import PhasedDrumAnalysis
    except ImportError:
        PhasedDrumAnalysis = None

try:
    from hybrid_drum_analysis_system import HybridDrumAnalysisSystem
except ImportError:
    HybridDrumAnalysisSystem = None

try:
    from drummer_style_database import DrummerStyleDatabase
except ImportError:
    DrummerStyleDatabase = None

try:
    from drummer_style_encoder import DrummerStyleEncoder, MIDIStyleGenerator
except ImportError:
    DrummerStyleEncoder = None
    MIDIStyleGenerator = None

# Optional higher-level generator for Pro tier
try:
    from drumtrackai_generation_service import DrumGenerationService
except ImportError:
    DrumGenerationService = None

# --- WebDAW DB interfaces (import from your app) ---
try:
    from ..db import SessionLocal
    from .. import models
except ImportError:
    # Fallback for development
    SessionLocal = None
    models = None

@dataclass
class SectionCtx:
    id: str
    start: float
    end: float
    time_signature: str

@dataclass
class GenParams:
    complexity: float = 0.5
    energy: float = 0.5
    swing: float = 0.0
    humanize: float = 0.2
    fill_in: str = "none"  # none|short|long
    fill_out: str = "none" # none|short|long
    fill_every_bars: Optional[int] = None  # cadence
    source: str = "mix"    # mix|bass|none
    drummer_id: Optional[str] = None
    style: str = "default"

class LLMDrumsProvider:
    def __init__(self, data_root: str):
        self.data_root = data_root
        self.analysis_cache = {}
        
        # Initialize components if available
        self.db = DrummerStyleDatabase() if DrummerStyleDatabase else None
        self.encoder = DrummerStyleEncoder() if DrummerStyleEncoder else None
        self.midi_gen = MIDIStyleGenerator() if MIDIStyleGenerator else None
        self.hybrid = HybridDrumAnalysisSystem() if HybridDrumAnalysisSystem else None
        self.pro_service = DrumGenerationService() if DrumGenerationService else None

    # ---------- Public API ----------
    def curated_drummers(self, job_id: str, top: int = 6, diverse: int = 3) -> List[Dict]:
        """Return a curated subset of drummer profiles matched to project style."""
        if not self.db:
            return self._fallback_drummers()
            
        # derive reference style vector from project analysis (cached if exists)
        ref_vec = self._compute_project_style_vector(job_id)
        try:
            results = self.db.get_drummers_by_style_similarity(ref_vec, threshold=0.6)
            return results[:top]
        except Exception:
            return self._fallback_drummers()

    def suggest_for_section(self, job_id: str, section_id: str, params: GenParams) -> Dict[str, List[Dict]]:
        """Generate per‑drum notes for a section. Returns dict of drum -> [{id, step/seconds, velocity}]."""
        if not SessionLocal or not models:
            return self._fallback_generation(params)
            
        try:
            with SessionLocal() as s:
                sec = s.query(models.Section).filter(models.Section.id==section_id).first()
                if not sec:
                    return {k: [] for k in ["kick","snare","hihat","ride","crash","tom"]}
                ctx = SectionCtx(id=sec.id, start=float(sec.start), end=float(sec.end), time_signature=sec.time_signature or "4/4")
                tempo_points = [
                    {"time": tp.time_sec, "bpm": tp.bpm}
                    for tp in s.query(models.TempoPoint).filter(models.TempoPoint.job_id==job_id).order_by(models.TempoPoint.time_sec)
                ]
        except Exception:
            return self._fallback_generation(params)

        length_sec = max(0.01, ctx.end - ctx.start)

        # Analysis path: always compute full mix + bass grid when stems exist and source != 'none'
        analysis = None
        bass_grid = None
        if params.source != 'none':
            analysis = self._analyze_job(job_id)
            if params.source in ("mix", "bass"):
                bass_grid = self._extract_bass(job_id)

        # Style vector: chosen drummer or encoded from analysis
        style_vec = None
        if params.drummer_id and self.db:
            try:
                style_vec = self.db.get_drummer_style_vector(params.drummer_id)
            except Exception:
                pass
                
        if style_vec is None and self.encoder:
            try:
                style_vec = self.encoder.encode_drummer_style(analysis=analysis, bass_grid=bass_grid)
            except Exception:
                pass

        # Generation strategy
        if self.pro_service:
            notes = self._generate_with_pro(job_id, ctx, style_vec, params, tempo_points)
        else:
            notes = self._generate_with_midi_gen(job_id, ctx, style_vec, params, tempo_points)

        return notes

    def apply_to_section(self, job_id: str, section_id: str, notes: Dict[str, List[Dict]]) -> bool:
        """Commit generated notes to section MIDI in DB."""
        if not SessionLocal or not models:
            return False
            
        try:
            with SessionLocal() as s:
                # Clear existing notes for this section
                s.query(models.Note).filter(models.Note.section_id==section_id).delete()
                
                # Add new notes
                for drum_type, drum_notes in notes.items():
                    for note in drum_notes:
                        db_note = models.Note(
                            section_id=section_id,
                            drum_type=drum_type,
                            time_sec=note.get('seconds', note.get('step', 0)),
                            velocity=note.get('velocity', 0.8),
                            note_id=note.get('id', f"{drum_type}_{note.get('step', 0)}")
                        )
                        s.add(db_note)
                s.commit()
                return True
        except Exception as e:
            print(f"Error applying notes to section: {e}")
            return False

    # ---------- Private helpers ----------
    def _compute_project_style_vector(self, job_id: str):
        """Compute or retrieve cached project style vector."""
        if job_id in self.analysis_cache:
            return self.analysis_cache[job_id].get('style_vector')
        
        # Fallback: return default style vector
        return "default_rock_style"

    def _analyze_job(self, job_id: str):
        """Run full mix analysis using PhasedDrumAnalysis."""
        if job_id in self.analysis_cache:
            return self.analysis_cache[job_id].get('analysis')
            
        if not PhasedDrumAnalysis:
            return None
            
        try:
            # This would analyze the actual audio files for the job
            # For now, return a mock analysis
            analysis = {
                'timing_precision': 0.85,
                'groove_score': 0.78,
                'complexity': 0.65,
                'energy': 0.72
            }
            
            if job_id not in self.analysis_cache:
                self.analysis_cache[job_id] = {}
            self.analysis_cache[job_id]['analysis'] = analysis
            return analysis
        except Exception:
            return None

    def _extract_bass(self, job_id: str):
        """Extract bass onset grid for kick coupling."""
        if job_id in self.analysis_cache:
            return self.analysis_cache[job_id].get('bass_grid')
            
        # Mock bass grid - would use actual bass analysis
        bass_grid = [0.0, 1.0, 2.0, 3.0, 4.0]  # Beat positions
        
        if job_id not in self.analysis_cache:
            self.analysis_cache[job_id] = {}
        self.analysis_cache[job_id]['bass_grid'] = bass_grid
        return bass_grid

    def _generate_with_pro(self, job_id: str, ctx: SectionCtx, style_vec, params: GenParams, tempo_points: List[Dict]) -> Dict[str, List[Dict]]:
        """Generate using Pro tier DrumGenerationService."""
        try:
            # Use the pro service for advanced generation
            result = self.pro_service.generate_drum_track(
                style=params.style,
                complexity=params.complexity,
                energy=params.energy,
                length_sec=ctx.end - ctx.start
            )
            return self._convert_to_webdaw_format(result, ctx)
        except Exception:
            return self._generate_with_midi_gen(job_id, ctx, style_vec, params, tempo_points)

    def _generate_with_midi_gen(self, job_id: str, ctx: SectionCtx, style_vec, params: GenParams, tempo_points: List[Dict]) -> Dict[str, List[Dict]]:
        """Generate using basic MIDIStyleGenerator."""
        if not self.midi_gen:
            return self._fallback_generation(params)
            
        try:
            # Basic MIDI generation
            length_sec = ctx.end - ctx.start
            avg_bpm = tempo_points[0]['bpm'] if tempo_points else 120
            
            # Generate basic patterns
            notes = {
                "kick": self._generate_kick_pattern(length_sec, avg_bpm, params),
                "snare": self._generate_snare_pattern(length_sec, avg_bpm, params),
                "hihat": self._generate_hihat_pattern(length_sec, avg_bpm, params),
                "ride": [],
                "crash": self._generate_crash_pattern(length_sec, avg_bpm, params),
                "tom": []
            }
            
            return notes
        except Exception:
            return self._fallback_generation(params)

    def _generate_kick_pattern(self, length_sec: float, bpm: float, params: GenParams) -> List[Dict]:
        """Generate kick drum pattern."""
        beat_duration = 60.0 / bpm
        notes = []
        
        # Basic kick on 1 and 3
        for beat in range(0, int(length_sec / beat_duration), 2):
            time_sec = beat * beat_duration
            if time_sec < length_sec:
                notes.append({
                    'id': f'kick_{beat}',
                    'seconds': time_sec,
                    'velocity': 0.8 + (params.energy - 0.5) * 0.4
                })
        
        return notes

    def _generate_snare_pattern(self, length_sec: float, bpm: float, params: GenParams) -> List[Dict]:
        """Generate snare drum pattern."""
        beat_duration = 60.0 / bpm
        notes = []
        
        # Basic snare on 2 and 4
        for beat in range(1, int(length_sec / beat_duration), 2):
            time_sec = beat * beat_duration
            if time_sec < length_sec:
                notes.append({
                    'id': f'snare_{beat}',
                    'seconds': time_sec,
                    'velocity': 0.7 + (params.energy - 0.5) * 0.3
                })
        
        return notes

    def _generate_hihat_pattern(self, length_sec: float, bpm: float, params: GenParams) -> List[Dict]:
        """Generate hi-hat pattern."""
        beat_duration = 60.0 / bpm
        subdivision = beat_duration / 2  # 8th notes
        notes = []
        
        # Basic 8th note hi-hat pattern
        time = 0.0
        note_id = 0
        while time < length_sec:
            notes.append({
                'id': f'hihat_{note_id}',
                'seconds': time,
                'velocity': 0.5 + (params.complexity - 0.5) * 0.3
            })
            time += subdivision
            note_id += 1
        
        return notes

    def _generate_crash_pattern(self, length_sec: float, bpm: float, params: GenParams) -> List[Dict]:
        """Generate crash cymbal pattern."""
        notes = []
        
        # Crash at the beginning if it's a long section
        if length_sec > 8.0:
            notes.append({
                'id': 'crash_0',
                'seconds': 0.0,
                'velocity': 0.9
            })
        
        return notes

    def _convert_to_webdaw_format(self, result: Dict, ctx: SectionCtx) -> Dict[str, List[Dict]]:
        """Convert pro service result to WebDAW format."""
        # This would convert the pro service output to the expected format
        # For now, return a basic structure
        return {
            "kick": [],
            "snare": [],
            "hihat": [],
            "ride": [],
            "crash": [],
            "tom": []
        }

    def _fallback_drummers(self) -> List[Dict]:
        """Fallback drummer list when DB is not available."""
        return [
            {"drummer_id": "john_bonham", "drummer_name": "John Bonham", "style": "rock", "confidence": 0.9},
            {"drummer_id": "neil_peart", "drummer_name": "Neil Peart", "style": "progressive", "confidence": 0.85},
            {"drummer_id": "buddy_rich", "drummer_name": "Buddy Rich", "style": "jazz", "confidence": 0.88},
            {"drummer_id": "keith_moon", "drummer_name": "Keith Moon", "style": "rock", "confidence": 0.82},
            {"drummer_id": "stewart_copeland", "drummer_name": "Stewart Copeland", "style": "new_wave", "confidence": 0.79},
            {"drummer_id": "travis_barker", "drummer_name": "Travis Barker", "style": "punk", "confidence": 0.76}
        ]

    def _fallback_generation(self, params: GenParams) -> Dict[str, List[Dict]]:
        """Fallback generation when components are not available."""
        return {
            "kick": [{"id": "kick_0", "seconds": 0.0, "velocity": 0.8}],
            "snare": [{"id": "snare_1", "seconds": 0.5, "velocity": 0.7}],
            "hihat": [{"id": "hihat_0", "seconds": 0.0, "velocity": 0.5}, {"id": "hihat_1", "seconds": 0.25, "velocity": 0.4}],
            "ride": [],
            "crash": [],
            "tom": []
        }
