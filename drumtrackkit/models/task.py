from .. import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = "tasks"
    
    id = db.Column(db.Integer, primary_key=True)
    # Temporarily comment out the foreign key
    # user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)  # No foreign key for now
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Comment out relationship too
    # user = db.relationship("User", backref=db.backref("tasks", lazy=True))
    
    def __repr__(self):
        return f"<Task {self.title}>"
