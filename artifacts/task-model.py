from drumtrackkit import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


class Task(db.Model):
    """Model for background tasks and long-running operations"""
    __tablename__ = 'tasks'

    # For PostgreSQL, use UUID type
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # For SQLite fallback, use String
    # id = db.Column(db.String(36), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='queued')
    progress = db.Column(db.Integer, nullable=False, default=0)

    # For PostgreSQL, use JSONB
    parameters = db.Column(JSONB, nullable=True)
    result = db.Column(JSONB, nullable=True)
    error = db.Column(JSONB, nullable=True)
    # For SQLite fallback
    # parameters = db.Column(db.JSON, nullable=True)
    # result = db.Column(db.JSON, nullable=True)
    # error = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationship to user
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

    def __repr__(self):
        return f'<Task {self.id} ({self.type}, {self.status})>'