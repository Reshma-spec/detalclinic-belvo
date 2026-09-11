from datetime import datetime
from models import db

class DentalToothCondition(db.Model):
    __tablename__ = 'dental_tooth_conditions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    tooth_number = db.Column(db.Integer, nullable=False)  # 1-32 Universal, or 11-48 FDI
    condition = db.Column(db.String(50), default='Healthy')  # Healthy, Caries, Filled, Missing, Crown, Root Canal, Extraction Required, Implant, Other
    surface = db.Column(db.String(20), default='Whole')  # Occlusal, Mesial, Distal, Buccal, Lingual, Whole
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('patient_id', 'tooth_number', name='uq_patient_tooth'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'tooth_number': self.tooth_number,
            'condition': self.condition,
            'surface': self.surface,
            'notes': self.notes or '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M') if self.updated_at else ''
        }

    def __repr__(self):
        return f'<ToothCondition Patient:{self.patient_id} Tooth:{self.tooth_number} ({self.condition})>'
