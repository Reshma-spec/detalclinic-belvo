from flask import Blueprint, render_template, session
from models import ClinicSetting, Specialty, Doctor

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/')
def index():
    settings = ClinicSetting.get_settings()
    specialties = Specialty.query.filter_by(is_active=True).all()
    doctors = Doctor.query.filter_by(is_active=True).limit(6).all()
    user_role = session.get('role')
    user_name = session.get('username')

    return render_template(
        'landing.html',
        settings=settings,
        specialties=specialties,
        doctors=doctors,
        user_role=user_role,
        user_name=user_name
    )
