from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required
from models import db, Patient, Doctor, Appointment, ClinicalRecord, TreatmentPlan, Invoice, Payment, DentalToothCondition, ClinicSetting

patients_bp = Blueprint('patients', __name__)

def generate_patient_code():
    count = Patient.query.count() + 1
    year = datetime.now().year
    return f"PAT-{year}-{count:04d}"

@patients_bp.route('/')
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    gender_filter = request.args.get('gender', '').strip()
    blood_filter = request.args.get('blood_group', '').strip()
    
    query = Patient.query
    
    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            (Patient.full_name.ilike(search_like)) |
            (Patient.patient_code.ilike(search_like)) |
            (Patient.phone.ilike(search_like)) |
            (Patient.email.ilike(search_like))
        )
        
    if gender_filter:
        query = query.filter(Patient.gender == gender_filter)
        
    if blood_filter:
        query = query.filter(Patient.blood_group == blood_filter)
        
    patients = query.order_by(Patient.registration_date.desc()).all()
    doctors = Doctor.query.filter_by(is_active=True).all()
    settings = ClinicSetting.get_settings()
    
    return render_template(
        'patients.html',
        patients=patients,
        search_query=search_query,
        gender_filter=gender_filter,
        blood_filter=blood_filter,
        doctors=doctors,
        settings=settings
    )

@patients_bp.route('/add', methods=['POST'])
@login_required
def add():
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not full_name or not phone:
        flash('Patient Full Name and Phone Number are required.', 'danger')
        return redirect(url_for('patients.index'))
        
    age = request.form.get('age')
    age = int(age) if age and age.isdigit() else None
    
    patient = Patient(
        patient_code=generate_patient_code(),
        full_name=full_name,
        age=age,
        gender=request.form.get('gender', 'Other'),
        phone=phone,
        email=request.form.get('email', '').strip() or None,
        dob=request.form.get('dob', '').strip() or None,
        address=request.form.get('address', '').strip() or None,
        blood_group=request.form.get('blood_group', '').strip() or None,
        emergency_contact=request.form.get('emergency_contact', '').strip() or None,
        medical_history=request.form.get('medical_history', '').strip() or None,
        allergies=request.form.get('allergies', '').strip() or None,
        current_medications=request.form.get('current_medications', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None
    )
    
    db.session.add(patient)
    db.session.commit()
    
    # Initialize adult 32 teeth as Healthy in database for quick lookup
    for tooth_num in range(1, 33):
        condition = DentalToothCondition(
            patient_id=patient.id,
            tooth_number=tooth_num,
            condition='Healthy',
            surface='Whole',
            notes=''
        )
        db.session.add(condition)
    db.session.commit()
    
    flash(f'Patient {patient.full_name} ({patient.patient_code}) created successfully!', 'success')
    return redirect(url_for('patients.detail', patient_id=patient.id))

@patients_bp.route('/<int:patient_id>')
@login_required
def detail(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.index'))
        
    doctors = Doctor.query.filter_by(is_active=True).all()
    dental_conditions = DentalToothCondition.query.filter_by(patient_id=patient.id).order_by(DentalToothCondition.tooth_number.asc()).all()
    
    # Map tooth number to condition dict
    chart_data = {c.tooth_number: c.to_dict() for c in dental_conditions}
    
    # Fetch active tab
    active_tab = request.args.get('tab', 'overview')
    settings = ClinicSetting.get_settings()
    
    return render_template(
        'patient_detail.html',
        patient=patient,
        doctors=doctors,
        chart_data=chart_data,
        active_tab=active_tab,
        settings=settings
    )

@patients_bp.route('/<int:patient_id>/edit', methods=['POST'])
@login_required
def edit(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.index'))
        
    full_name = request.form.get('full_name', '').strip()
    phone = request.form.get('phone', '').strip()
    
    if not full_name or not phone:
        flash('Name and phone are required.', 'danger')
        return redirect(url_for('patients.detail', patient_id=patient.id))
        
    age = request.form.get('age')
    patient.full_name = full_name
    patient.phone = phone
    patient.age = int(age) if age and age.isdigit() else None
    patient.gender = request.form.get('gender', patient.gender)
    patient.email = request.form.get('email', '').strip() or None
    patient.dob = request.form.get('dob', '').strip() or None
    patient.address = request.form.get('address', '').strip() or None
    patient.blood_group = request.form.get('blood_group', '').strip() or None
    patient.emergency_contact = request.form.get('emergency_contact', '').strip() or None
    patient.medical_history = request.form.get('medical_history', '').strip() or None
    patient.allergies = request.form.get('allergies', '').strip() or None
    patient.current_medications = request.form.get('current_medications', '').strip() or None
    patient.notes = request.form.get('notes', '').strip() or None
    
    db.session.commit()
    flash('Patient profile updated successfully!', 'success')
    return redirect(url_for('patients.detail', patient_id=patient.id, tab='overview'))

@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.index'))
        
    name = patient.full_name
    db.session.delete(patient)
    db.session.commit()
    
    flash(f'Patient {name} and all related records deleted successfully.', 'info')
    return redirect(url_for('patients.index'))

@patients_bp.route('/<int:patient_id>/print-summary')
@login_required
def print_summary(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.index'))
    settings = ClinicSetting.get_settings()
    dental_conditions = DentalToothCondition.query.filter_by(patient_id=patient.id).all()
    chart_data = {c.tooth_number: c.to_dict() for c in dental_conditions}
    
    return render_template(
        'print_patient.html',
        patient=patient,
        settings=settings,
        chart_data=chart_data
    )
