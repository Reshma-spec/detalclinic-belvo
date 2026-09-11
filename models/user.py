from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='receptionist')  # admin, doctor, receptionist, patient
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 1-to-1 relationship with Doctor profile if role is doctor
    doctor_profile = db.relationship('Doctor', backref='user_account', uselist=False, cascade='all, delete-orphan')
    # 1-to-1 relationship with Patient profile if role is patient
    patient_profile = db.relationship('Patient', backref='user_account', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_doctor(self):
        return self.role == 'doctor'

    def is_receptionist(self):
        return self.role == 'receptionist'

    def is_patient(self):
        return self.role == 'patient'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
