from datetime import datetime, date
from models import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    rx_number = db.Column(db.String(50), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=True)
    clinical_record_id = db.Column(db.Integer, db.ForeignKey('clinical_records.id'), nullable=True)
    prescription_date = db.Column(db.String(20), default=lambda: date.today().strftime('%Y-%m-%d'))
    diagnosis = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship('Patient', backref=db.backref('prescriptions', lazy=True, cascade='all, delete-orphan', order_by='Prescription.prescription_date.desc()'))
    doctor = db.relationship('Doctor', backref=db.backref('prescriptions', lazy=True))
    clinical_record = db.relationship('ClinicalRecord', backref=db.backref('prescription', uselist=False))
    items = db.relationship('PrescriptionItem', backref='prescription', lazy=True, cascade='all, delete-orphan')

class PrescriptionItem(db.Model):
    __tablename__ = 'prescription_items'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id', ondelete='CASCADE'), nullable=False)
    medicine_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False) # e.g. 500mg
    frequency = db.Column(db.String(100), nullable=False) # e.g. 1-0-1 after meals
    duration = db.Column(db.String(100), nullable=False) # e.g. 5 days
    instructions = db.Column(db.String(255), nullable=True)
