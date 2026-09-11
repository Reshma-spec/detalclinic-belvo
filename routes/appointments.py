from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required
from models import db, Appointment, Patient, Doctor, ClinicSetting

appointments_bp = Blueprint('appointments', __name__)

@appointments_bp.route('/')
@login_required
def index():
    date_filter = request.args.get('date', '').strip()
    doctor_filter = request.args.get('doctor_id', '').strip()
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()
    
    query = Appointment.query.join(Patient)
    
    if date_filter:
        query = query.filter(Appointment.appointment_date == date_filter)
    if doctor_filter and doctor_filter.isdigit():
        query = query.filter(Appointment.doctor_id == int(doctor_filter))
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            (Patient.full_name.ilike(search_like)) |
            (Patient.patient_code.ilike(search_like)) |
            (Patient.phone.ilike(search_like))
        )
        
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.appointment_time.asc()).all()
    patients = Patient.query.order_by(Patient.full_name.asc()).all()
    doctors = Doctor.query.filter_by(is_active=True).order_by(Doctor.name.asc()).all()
    settings = ClinicSetting.get_settings()
    
    today_str = date.today().strftime('%Y-%m-%d')
    
    return render_template(
        'appointments.html',
        appointments=appointments,
        patients=patients,
        doctors=doctors,
        date_filter=date_filter,
        doctor_filter=doctor_filter,
        status_filter=status_filter,
        search_query=search_query,
        today_str=today_str,
        settings=settings
    )

@appointments_bp.route('/add', methods=['POST'])
@login_required
def add():
    patient_id = request.form.get('patient_id')
    doctor_id = request.form.get('doctor_id')
    appointment_date = request.form.get('appointment_date', '').strip()
    appointment_time = request.form.get('appointment_time', '').strip()
    appointment_type = request.form.get('appointment_type', 'Consultation')
    duration = int(request.form.get('duration_minutes', 30))
    reason = request.form.get('reason', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not patient_id or not doctor_id or not appointment_date or not appointment_time:
        flash('Patient, Doctor, Date, and Time are required.', 'danger')
        return redirect(url_for('appointments.index'))
        
    # Check for double booking conflict
    conflict = Appointment.check_conflict(int(doctor_id), appointment_date, appointment_time)
    if conflict:
        flash(f'Warning: Dr. {conflict.doctor.name} already has an active appointment ({conflict.status}) at {appointment_time} on {appointment_date}. Please pick a different slot.', 'danger')
        return redirect(url_for('appointments.index'))
        
    # Generate daily queue token number
    today_count = Appointment.query.filter_by(appointment_date=appointment_date).count()
    token_num = today_count + 1
    
    appt = Appointment(
        patient_id=int(patient_id),
        doctor_id=int(doctor_id),
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        duration_minutes=duration,
        appointment_type=appointment_type,
        reason=reason,
        status='Scheduled',
        token_number=token_num,
        notes=notes
    )
    
    db.session.add(appt)
    db.session.commit()
    
    flash(f'Appointment successfully booked for {appt.patient.full_name} on {appointment_date} at {appointment_time}! (Token #{token_num})', 'success')
    return redirect(request.referrer or url_for('appointments.index'))

@appointments_bp.route('/<int:appointment_id>/status', methods=['POST'])
@login_required
def update_status(appointment_id):
    appt = db.session.get(Appointment, appointment_id)
    if not appt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.index'))
        
    new_status = request.form.get('status')
    if new_status in ['Scheduled', 'Confirmed', 'Waiting', 'In Treatment', 'Completed', 'Cancelled', 'No Show']:
        appt.status = new_status
        db.session.commit()
        flash(f'Appointment status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
        
    return redirect(request.referrer or url_for('appointments.index'))

@appointments_bp.route('/<int:appointment_id>/edit', methods=['POST'])
@login_required
def edit(appointment_id):
    appt = db.session.get(Appointment, appointment_id)
    if not appt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.index'))
        
    doctor_id = int(request.form.get('doctor_id', appt.doctor_id))
    appointment_date = request.form.get('appointment_date', appt.appointment_date).strip()
    appointment_time = request.form.get('appointment_time', appt.appointment_time).strip()
    
    # Conflict check excluding this appointment
    conflict = Appointment.check_conflict(doctor_id, appointment_date, appointment_time, exclude_id=appt.id)
    if conflict:
        flash(f'Conflict: Dr. {conflict.doctor.name} already has an appointment booked at {appointment_time} on {appointment_date}.', 'danger')
        return redirect(url_for('appointments.index'))
        
    appt.doctor_id = doctor_id
    appt.appointment_date = appointment_date
    appt.appointment_time = appointment_time
    appt.appointment_type = request.form.get('appointment_type', appt.appointment_type)
    appt.duration_minutes = int(request.form.get('duration_minutes', appt.duration_minutes))
    appt.status = request.form.get('status', appt.status)
    appt.reason = request.form.get('reason', appt.reason).strip()
    appt.notes = request.form.get('notes', appt.notes).strip()
    
    db.session.commit()
    flash('Appointment updated successfully!', 'success')
    return redirect(request.referrer or url_for('appointments.index'))

@appointments_bp.route('/<int:appointment_id>/delete', methods=['POST'])
@login_required
def delete(appointment_id):
    appt = db.session.get(Appointment, appointment_id)
    if not appt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments.index'))
        
    db.session.delete(appt)
    db.session.commit()
    flash('Appointment deleted successfully.', 'info')
    return redirect(request.referrer or url_for('appointments.index'))
