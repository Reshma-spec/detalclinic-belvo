from datetime import datetime
from models import db

class PatientTimeline(db.Model):
    __tablename__ = 'patient_timelines'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # registration, appointment, clinical, chart, treatment, prescription, invoice, payment
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    badge_color = db.Column(db.String(20), default='info') # primary, success, warning, danger, info, secondary
    icon = db.Column(db.String(50), default='fa-calendar-check')
    created_by = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref=db.backref('timeline_events', lazy=True, cascade='all, delete-orphan', order_by='PatientTimeline.created_at.desc()'))

    def __repr__(self):
        return f'<PatientTimeline {self.event_type} - {self.title}>'
