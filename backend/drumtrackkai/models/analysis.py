from datetime import datetime
from .. import db


class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    audio_file_path = db.Column(db.String(255))
    analysis_type = db.Column(db.String(50))
    results = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Analysis {self.id} for User {self.user_id}>'