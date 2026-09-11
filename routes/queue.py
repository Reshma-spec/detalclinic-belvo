from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, Appointment, Doctor, ClinicSetting

queue_bp = Blueprint('queue', __name__)

@queue_bp.route('/')
@login_required
def index():
    today_str = date.today().strftime('%Y-%m-%d')
    doctor_filter = request.args.get('doctor_id', '').strip()
    
    query = Appointment.query.filter(
        Appointment.appointment_date == today_str,
        Appointment.status.notin_(['Cancelled', 'No Show'])
    )
    
    if doctor_filter and doctor_filter.isdigit():
        query = query.filter(Appointment.doctor_id == int(doctor_filter))
        
    queue_items = query.order_by(Appointment.appointment_time.asc()).all()
    
    # Categorize into queue sections
    waiting_list = [item for item in queue_items if item.status in ['Scheduled', 'Confirmed', 'Waiting']]
    in_treatment_list = [item for item in queue_items if item.status == 'In Treatment']
    completed_list = [item for item in queue_items if item.status == 'Completed']
    
    doctors = Doctor.query.filter_by(is_active=True).all()
    settings = ClinicSetting.get_settings()
    
    return render_template(
        'queue.html',
        waiting_list=waiting_list,
        in_treatment_list=in_treatment_list,
        completed_list=completed_list,
        doctors=doctors,
        doctor_filter=doctor_filter,
        today_str=today_str,
        settings=settings
    )

@queue_bp.route('/<int:appointment_id>/action', methods=['POST'])
@login_required
def queue_action(appointment_id):
    appt = db.session.get(Appointment, appointment_id)
    if not appt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('queue.index'))
        
    action = request.form.get('action')
    if action == 'call':
        appt.status = 'Waiting'
        flash(f'Token #{appt.token_number} ({appt.patient.full_name}) called to Waiting Area.', 'info')
    elif action == 'start_treatment':
        appt.status = 'In Treatment'
        flash(f'Treatment started for {appt.patient.full_name}.', 'primary')
    elif action == 'complete':
        appt.status = 'Completed'
        flash(f'Appointment completed for {appt.patient.full_name}.', 'success')
    elif action == 'skip':
        appt.status = 'No Show'
        flash(f'Patient marked as No Show / Skipped.', 'warning')
        
    db.session.commit()
    return redirect(url_for('queue.index'))
