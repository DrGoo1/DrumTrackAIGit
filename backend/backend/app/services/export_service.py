"""
DrumTracKAI v4/v5 Advanced Export Service
Professional-grade export system with MIDI, stems, and stereo rendering
"""

import os
import json
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import soundfile as sf
from sqlalchemy.orm import Session
from ..models import ExportJob, Job, Section
from ..deps import get_db
import threading
import logging

logger = logging.getLogger(__name__)

class RenderEngine:
    """Professional audio rendering engine"""
    
    def __init__(self, sr=48000):
        self.sr = sr
        self.export_dir = Path('/app/exports')
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def render_from_job(self, params: Dict) -> Dict[str, str]:
        """Render audio from job parameters"""
        try:
            mode = params.get('mode') or params.get('export_mode')
            job_id = params.get('job_id', 'unknown')
            midi_lanes = params.get('midi_lanes', {})
            kit_map = params.get('kit_map', {})
            
            out_dir = self.export_dir / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize synth with kit mapping
            from .synth import SamplerSynth
            synth = SamplerSynth(sr=self.sr, kit_map=kit_map)
            
            # Render each lane
            lane_audio = {}
            for lane, events in midi_lanes.items():
                if events:
                    audio = synth.render_lane(events)
                    # Apply processing chain
                    from .mix_chains import build_channel_chain
                    chain = build_channel_chain(lane, self.sr, params)
                    processed_audio = chain.process(audio)
                    lane_audio[lane] = processed_audio
            
            # Mix down
            from .mix_chains import build_buses
            buses = build_buses(self.sr, params)
            stereo = buses.mixdown(lane_audio, params)
            
            paths = {}
            
            if mode == 'stems':
                # Export individual stems in a zip
                zip_path = out_dir / 'stems.zip'
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for lane, audio in lane_audio.items():
                        stem_path = out_dir / f"{lane}.wav"
                        sf.write(stem_path, audio, self.sr, subtype='PCM_24')
                        zf.write(stem_path, arcname=f"{lane}.wav")
                        stem_path.unlink()  # Clean up individual files
                paths['zip'] = str(zip_path)
                
            elif mode == 'stereo':
                # Export stereo mix
                stereo_path = out_dir / 'drums_stereo.wav'
                sf.write(stereo_path, stereo, self.sr, subtype='PCM_24')
                paths['stereo'] = str(stereo_path)
                
            elif mode == 'midi':
                # Export MIDI files
                zip_path = out_dir / 'midi_export.zip'
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for lane, events in midi_lanes.items():
                        if events:
                            midi_content = self._events_to_midi(events, lane)
                            zf.writestr(f"{lane}.mid", midi_content)
                    zf.writestr('README.txt', 'DrumTracKAI MIDI Export\nGenerated with v4/v5 engine')
                paths['zip'] = str(zip_path)
            
            return paths
            
        except Exception as e:
            logger.error(f"Render error: {e}")
            raise
    
    def _events_to_midi(self, events: List[Dict], lane: str) -> bytes:
        """Convert events to MIDI bytes (simplified implementation)"""
        # This is a placeholder - implement proper MIDI file generation
        midi_header = b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x00\x60'
        midi_track = b'MTrk\x00\x00\x00\x04\x00\xFF\x2F\x00'
        return midi_header + midi_track

class ExportService:
    """Main export service"""
    
    def __init__(self):
        self.render_engine = RenderEngine()
        self.active_jobs = {}
    
    def queue_export(self, export_job_id: str):
        """Queue an export job for background processing"""
        thread = threading.Thread(
            target=self._run_export, 
            args=(export_job_id,), 
            daemon=True
        )
        thread.start()
        self.active_jobs[export_job_id] = thread
    
    def _run_export(self, export_job_id: str):
        """Run export job in background"""
        from ..deps import SessionLocal
        
        db: Session = SessionLocal()
        try:
            ej = db.query(ExportJob).get(export_job_id)
            if not ej:
                logger.error(f"Export job {export_job_id} not found")
                return
            
            # Update status
            ej.status = 'running'
            ej.progress = 5
            db.commit()
            
            # Render
            logger.info(f"Starting export job {export_job_id}")
            paths = self.render_engine.render_from_job(ej.params_json)
            
            # Complete
            ej.status = 'done'
            ej.progress = 100
            ej.result_path = paths.get('zip') or paths.get('stereo')
            db.commit()
            
            logger.info(f"Export job {export_job_id} completed: {ej.result_path}")
            
        except Exception as e:
            logger.error(f"Export job {export_job_id} failed: {e}")
            ej = db.query(ExportJob).get(export_job_id)
            if ej:
                ej.status = 'error'
                ej.error = str(e)
                db.commit()
        finally:
            db.close()
            if export_job_id in self.active_jobs:
                del self.active_jobs[export_job_id]
    
    def get_export_status(self, export_job_id: str, db: Session) -> Dict:
        """Get export job status"""
        ej = db.query(ExportJob).get(export_job_id)
        if not ej:
            raise ValueError("Export job not found")
        
        return {
            "status": ej.status,
            "progress": ej.progress,
            "url": ej.result_path,
            "error": ej.error,
            "created_at": ej.created_at.isoformat() if ej.created_at else None,
            "updated_at": ej.updated_at.isoformat() if ej.updated_at else None
        }
    
    def create_export_job(self, job_id: str, user_id: str, mode: str, params: Dict, db: Session) -> str:
        """Create a new export job"""
        ej = ExportJob(
            job_id=job_id,
            user_id=user_id,
            mode=mode,
            status='queued',
            params_json=params
        )
        db.add(ej)
        db.commit()
        db.refresh(ej)
        
        # Queue for processing
        self.queue_export(ej.id)
        
        return ej.id
