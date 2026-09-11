from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth import login_required
from models import db, Doctor, Specialty, Appointment, ClinicalRecord, Patient, PatientTimeline

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/')
def directory():
    specialty_id = request.args.get('specialty_id')
    search_q = request.args.get('search', '').strip()
    
    query = Doctor.query.filter_by(is_active=True)
    if specialty_id and specialty_id.isdigit():
        query = query.filter_by(specialty_id=int(specialty_id))
    if search_q:
        search_like = f"%{search_q}%"
        query = query.filter((Doctor.name.ilike(search_like)) | (Doctor.specialization.ilike(search_like)))
        
    doctors = query.all()
    specialties = Specialty.query.filter_by(is_active=True).all()
    
    return render_template('doctors_directory.html', doctors=doctors, specialties=specialties, selected_specialty=specialty_id, search_query=search_q)

@doctors_bp.route('/<int:doctor_id>')
def profile(doctor_id):
    doctor = db.session.get(Doctor, doctor_id)
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('doctors.directory'))
    return render_template('doctor_profile.html', doctor=doctor)

@doctors_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    
    if role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user_id).first()
    else:
        doctor = Doctor.query.filter_by(is_active=True).first()
        
    if not doctor:
        flash('Doctor record not found.', 'warning')
        return redirect(url_for('dashboard.index'))
        
    from datetime import date
    today_str = date.today().strftime('%Y-%m-%d')
    
    today_appointments = Appointment.query.filter_by(doctor_id=doctor.id, appointment_date=today_str).order_by(Appointment.appointment_time.asc()).all()
    waiting_patients = [a for a in today_appointments if a.status in ['Checked In', 'Scheduled', 'Confirmed']]
    in_chair = [a for a in today_appointments if a.status == 'In Chair']
    completed = [a for a in today_appointments if a.status == 'Completed']
    
    recent_clinical = ClinicalRecord.query.filter_by(doctor_id=doctor.id).order_by(ClinicalRecord.created_at.desc()).limit(5).all()

    return render_template(
        'doctor_dashboard.html',
        doctor=doctor,
        today_appointments=today_appointments,
        waiting_patients=waiting_patients,
        in_chair=in_chair,
        completed=completed,
        recent_clinical=recent_clinical,
        today_str=today_str
    )
