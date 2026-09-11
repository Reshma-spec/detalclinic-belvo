from datetime import datetime
from models import db

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), default='General Dentistry')
    license_number = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    consultation_fee = db.Column(db.Float, default=50.0)
    working_days = db.Column(db.String(100), default='Mon, Tue, Wed, Thu, Fri, Sat')
    working_hours_start = db.Column(db.String(10), default='09:00')
    working_hours_end = db.Column(db.String(10), default='18:00')
    color_code = db.Column(db.String(20), default='#0ea5e9')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic')
    clinical_records = db.relationship('ClinicalRecord', backref='doctor', lazy='dynamic')
    treatment_plans = db.relationship('TreatmentPlan', backref='doctor', lazy='dynamic')
    invoices = db.relationship('Invoice', backref='doctor', lazy='dynamic')

    def __repr__(self):
        return f'<Doctor Dr. {self.name} - {self.specialization}>'
