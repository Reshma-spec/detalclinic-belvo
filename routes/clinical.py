from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models import db, ClinicalRecord, Patient, Doctor, Appointment, ClinicSetting

clinical_bp = Blueprint('clinical', __name__)

@clinical_bp.route('/')
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    doctor_filter = request.args.get('doctor_id', '').strip()
    
    query = ClinicalRecord.query.join(Patient)
    
    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            (Patient.full_name.ilike(search_like)) |
            (Patient.patient_code.ilike(search_like)) |
            (ClinicalRecord.diagnosis.ilike(search_like)) |
            (ClinicalRecord.chief_complaint.ilike(search_like))
        )
        
    if doctor_filter and doctor_filter.isdigit():
        query = query.filter(ClinicalRecord.doctor_id == int(doctor_filter))
        
    records = query.order_by(ClinicalRecord.visit_date.desc(), ClinicalRecord.id.desc()).all()
    patients = Patient.query.order_by(Patient.full_name.asc()).all()
    doctors = Doctor.query.filter_by(is_active=True).all()
    settings = ClinicSetting.get_settings()
    
    return render_template(
        'clinical.html',
        records=records,
        patients=patients,
        doctors=doctors,
        search_query=search_query,
        doctor_filter=doctor_filter,
        today_str=date.today().strftime('%Y-%m-%d'),
        settings=settings
    )

@clinical_bp.route('/add', methods=['POST'])
@login_required
def add():
    patient_id = request.form.get('patient_id')
    doctor_id = request.form.get('doctor_id')
    visit_date = request.form.get('visit_date', date.today().strftime('%Y-%m-%d')).strip()
    chief_complaint = request.form.get('chief_complaint', '').strip()
    diagnosis = request.form.get('diagnosis', '').strip()
    
    if not patient_id or not doctor_id or not chief_complaint or not diagnosis:
        flash('Patient, Doctor, Chief Complaint, and Diagnosis are required.', 'danger')
        return redirect(request.referrer or url_for('clinical.index'))
        
    appointment_id = request.form.get('appointment_id')
    appointment_id = int(appointment_id) if appointment_id and appointment_id.isdigit() else None
    
    record = ClinicalRecord(
        patient_id=int(patient_id),
        doctor_id=int(doctor_id),
        appointment_id=appointment_id,
        visit_date=visit_date,
        chief_complaint=chief_complaint,
        examination=request.form.get('examination', '').strip() or None,
        diagnosis=diagnosis,
        procedure_performed=request.form.get('procedure_performed', '').strip() or None,
        prescriptions=request.form.get('prescriptions', '').strip() or None,
        clinical_notes=request.form.get('clinical_notes', '').strip() or None,
        follow_up_date=request.form.get('follow_up_date', '').strip() or None
    )
    
    db.session.add(record)
    
    # If appointment was attached, mark it completed if not already
    if appointment_id:
        appt = db.session.get(Appointment, appointment_id)
        if appt and appt.status != 'Completed':
            appt.status = 'Completed'
            
    db.session.commit()
    flash(f'Clinical record for {record.patient.full_name} saved successfully!', 'success')
    return redirect(request.referrer or url_for('patients.detail', patient_id=patient_id, tab='clinical'))

@clinical_bp.route('/<int:record_id>/print')
@login_required
def print_record(record_id):
    record = db.session.get(ClinicalRecord, record_id)
    if not record:
        flash('Clinical record not found.', 'danger')
        return redirect(url_for('clinical.index'))
    settings = ClinicSetting.get_settings()
    return render_template('print_clinical_record.html', record=record, settings=settings)

@clinical_bp.route('/<int:record_id>/delete', methods=['POST'])
@login_required
def delete(record_id):
    record = db.session.get(ClinicalRecord, record_id)
    if not record:
        flash('Record not found.', 'danger')
        return redirect(url_for('clinical.index'))
    patient_id = record.patient_id
    db.session.delete(record)
    db.session.commit()
    flash('Clinical record deleted.', 'info')
    return redirect(url_for('patients.detail', patient_id=patient_id, tab='clinical'))
