from datetime import datetime
from models import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    patient_code = db.Column(db.String(20), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), default='Other')
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    emergency_contact = db.Column(db.String(100), nullable=True)
    
    medical_history = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    current_medications = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(Appointment.appointment_date)')
    clinical_records = db.relationship('ClinicalRecord', backref='patient', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(ClinicalRecord.visit_date)')
    treatment_plans = db.relationship('TreatmentPlan', backref='patient', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(TreatmentPlan.created_at)')
    invoices = db.relationship('Invoice', backref='patient', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(Invoice.invoice_date)')
    payments = db.relationship('Payment', backref='patient', lazy='dynamic', cascade='all, delete-orphan')
    dental_conditions = db.relationship('DentalToothCondition', backref='patient', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_billed(self):
        return sum(inv.total_amount for inv in self.invoices)

    @property
    def total_paid(self):
        return sum(inv.paid_amount for inv in self.invoices)

    @property
    def total_due(self):
        return sum(inv.balance_amount for inv in self.invoices)

    def __repr__(self):
        return f'<Patient {self.patient_code} - {self.full_name}>'
