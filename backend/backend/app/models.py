"""
DrumTracKAI v4/v5 Advanced Database Models
Extends existing models with ChatGPT-5 integration features
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

def uid():
    return str(uuid.uuid4())

# Core WebDAW Models (existing)
class Job(Base):
    __tablename__ = 'jobs'
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, index=True)
    name = Column(String)
    status = Column(String, default='created')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Section(Base):
    __tablename__ = 'sections'
    id = Column(String, primary_key=True, default=uid)
    job_id = Column(String, index=True)
    name = Column(String)
    start = Column(Float)
    end = Column(Float)
    time_signature = Column(String, default='4/4')
    created_at = Column(DateTime, default=datetime.utcnow)

class TempoPoint(Base):
    __tablename__ = 'tempo_points'
    id = Column(String, primary_key=True, default=uid)
    job_id = Column(String, index=True)
    time_sec = Column(Float)
    bpm = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# v4/v5 Advanced Models (new from ChatGPT-5 pack)
class Kit(Base):
    __tablename__ = 'kits'
    id = Column(String, primary_key=True, default=uid)
    owner_user_id = Column(String, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, index=True)
    visibility = Column(String, default='private')  # private|project|global
    mapping_json = Column(JSON, nullable=False)     # {kick: url, snare: url, ...}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ExportJob(Base):
    __tablename__ = 'export_jobs'
    id = Column(String, primary_key=True, default=uid)
    job_id = Column(String, index=True)
    user_id = Column(String, index=True)
    mode = Column(String)  # midi|stems|stereo
    status = Column(String, default='queued')
    progress = Column(Integer, default=0)
    params_json = Column(JSON)
    result_path = Column(String)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class GrooveMetrics(Base):
    __tablename__ = 'groove_metrics'
    id = Column(String, primary_key=True, default=uid)
    job_id = Column(String, index=True)
    section_id = Column(String, index=True)
    metrics_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Persona(Base):
    __tablename__ = 'personas'
    id = Column(String, primary_key=True, default=uid)
    owner_user_id = Column(String, index=True)
    name = Column(String, nullable=False)
    a_profile_id = Column(String)
    b_profile_id = Column(String)
    morph = Column(Float, default=0.5)
    data_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Snapshot(Base):
    __tablename__ = 'snapshots'
    id = Column(String, primary_key=True, default=uid)
    job_id = Column(String, index=True)
    user_id = Column(String, index=True)
    name = Column(String)
    state_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReviewComment(Base):
    __tablename__ = 'review_comments'
    id = Column(String, primary_key=True, default=uid)
    job_id = Column(String, index=True)
    user_id = Column(String, index=True)
    section_id = Column(String, index=True)
    time_sec = Column(Float)
    text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Additional models for advanced features
class ImpulseResponse(Base):
    __tablename__ = 'impulse_responses'
    id = Column(String, primary_key=True, default=uid)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    category = Column(String)  # room|hall|plate|spring
    description = Column(Text)
    uploaded_by = Column(String, index=True)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReferenceLoop(Base):
    __tablename__ = 'reference_loops'
    id = Column(String, primary_key=True, default=uid)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    bpm = Column(Float)
    style = Column(String)
    bars = Column(Integer)
    tags = Column(JSON)  # Array of tags
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreferences(Base):
    __tablename__ = 'user_preferences'
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, index=True, unique=True)
    preferences_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ProcessingQueue(Base):
    __tablename__ = 'processing_queue'
    id = Column(String, primary_key=True, default=uid)
    job_type = Column(String)  # export|analysis|generation
    job_id = Column(String, index=True)
    user_id = Column(String, index=True)
    priority = Column(Integer, default=5)
    status = Column(String, default='queued')  # queued|running|completed|failed
    params_json = Column(JSON)
    result_json = Column(JSON)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
