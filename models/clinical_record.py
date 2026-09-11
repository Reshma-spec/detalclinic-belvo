from datetime import datetime
from models import db

class ClinicalRecord(db.Model):
    __tablename__ = 'clinical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id', ondelete='SET NULL'), nullable=True)
    visit_date = db.Column(db.String(10), nullable=False)
    
    chief_complaint = db.Column(db.Text, nullable=False)
    examination = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=False)
    procedure_performed = db.Column(db.Text, nullable=True)
    prescriptions = db.Column(db.Text, nullable=True)
    clinical_notes = db.Column(db.Text, nullable=True)
    follow_up_date = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def examination_findings(self):
        return self.examination or ''

    @examination_findings.setter
    def examination_findings(self, value):
        self.examination = value

    @property
    def treatment_done(self):
        return self.procedure_performed or ''

    @treatment_done.setter
    def treatment_done(self, value):
        self.procedure_performed = value

    @property
    def doctor_notes(self):
        return self.clinical_notes or ''

    @doctor_notes.setter
    def doctor_notes(self, value):
        self.clinical_notes = value

    def __repr__(self):
        return f'<ClinicalRecord #{self.id} for Patient {self.patient_id} on {self.visit_date}>'
