from datetime import datetime
from models import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    appointment_date = db.Column(db.String(10), nullable=False)  # YYYY-MM-DD
    appointment_time = db.Column(db.String(10), nullable=False)  # HH:MM
    duration_minutes = db.Column(db.Integer, default=30)
    appointment_type = db.Column(db.String(50), default='Consultation')
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='Scheduled')  # Scheduled, Confirmed, Waiting, In Treatment, Completed, Cancelled, No Show
    token_number = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def chief_complaint(self):
        return self.reason or ''

    @chief_complaint.setter
    def chief_complaint(self, value):
        self.reason = value

    clinical_records = db.relationship('ClinicalRecord', backref='appointment', lazy='dynamic')

    @classmethod
    def check_conflict(cls, doctor_id, appointment_date, appointment_time, exclude_id=None):
        query = cls.query.filter(
            cls.doctor_id == doctor_id,
            cls.appointment_date == appointment_date,
            cls.appointment_time == appointment_time,
            cls.status.notin_(['Cancelled', 'No Show'])
        )
        if exclude_id:
            query = query.filter(cls.id != exclude_id)
        return query.first()

    @classmethod
    def generate_token(cls, appointment_date):
        count = cls.query.filter_by(appointment_date=appointment_date).count()
        return 101 + count

    def __repr__(self):
        return f'<Appointment #{self.id} on {self.appointment_date} {self.appointment_time} ({self.status})>'
