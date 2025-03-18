from drumtrackkit import db
from datetime import datetime

class Analysis(db.Model):
    __tablename__ = 'analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    analysis_type = db.Column(db.String(50))
    status = db.Column(db.String(20), default='pending')
    audio_file_path = db.Column(db.String(255))
    job_id = db.Column(db.String(36))
    parameters = db.Column(db.JSON)
    results = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Analysis {self.id} for User {self.user_id}>'
