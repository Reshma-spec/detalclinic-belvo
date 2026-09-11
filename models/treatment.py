from datetime import datetime
from models import db

class TreatmentPlan(db.Model):
    __tablename__ = 'treatment_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    treatment_name = db.Column(db.String(150), nullable=False)
    tooth_number = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    estimated_cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(30), default='Proposed')  # Proposed, Accepted, In Progress, Completed, Cancelled
    start_date = db.Column(db.String(10), nullable=True)
    expected_completion = db.Column(db.String(10), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    invoices = db.relationship('Invoice', backref='treatment_plan', lazy='dynamic')

    def __repr__(self):
        return f'<TreatmentPlan {self.treatment_name} ({self.status})>'
