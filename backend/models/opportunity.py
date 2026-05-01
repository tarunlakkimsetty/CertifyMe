from datetime import datetime
from extensions import db


class Opportunity(db.Model):
    __tablename__ = 'opportunities'
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.String(64), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.String(512), nullable=False)
    category = db.Column(db.String(128), nullable=False)
    future_opportunities = db.Column(db.String(255), nullable=False)
    max_applicants = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship('Admin', back_populates='opportunities')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'duration': self.duration,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'description': self.description,
            'skills': self.skills,
            'category': self.category,
            'future_opportunities': self.future_opportunities,
            'max_applicants': self.max_applicants,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def to_summary_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'duration': self.duration,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'description': self.description,
        }
