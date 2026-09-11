from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from routes.auth import login_required
from models import db, Patient, Appointment, ClinicalRecord, TreatmentPlan, Invoice, Prescription, DentalToothCondition, Doctor, Specialty, PatientTimeline

portal_bp = Blueprint('portal', __name__)

def patient_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'patient':
            flash('Access restricted to registered patients.', 'warning')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@portal_bp.route('/')
@patient_required
def dashboard():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first()
    
    if not patient:
        flash('Patient profile not linked to account. Please contact clinic reception.', 'danger')
        return redirect(url_for('auth.logout'))

    upcoming_appointment = Appointment.query.filter_by(patient_id=patient.id).filter(
        Appointment.status.in_(['Scheduled', 'Confirmed', 'Checked In'])
    ).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc()).first()

    recent_appointments = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.appointment_date.desc()).limit(5).all()
    recent_prescriptions = Prescription.query.filter_by(patient_id=patient.id).order_by(Prescription.prescription_date.desc()).limit(5).all()
    recent_clinical = ClinicalRecord.query.filter_by(patient_id=patient.id).order_by(ClinicalRecord.visit_date.desc()).limit(5).all()
    treatments = TreatmentPlan.query.filter_by(patient_id=patient.id).all()
    invoices = Invoice.query.filter_by(patient_id=patient.id).order_by(Invoice.invoice_date.desc()).all()
    tooth_conditions = DentalToothCondition.query.filter_by(patient_id=patient.id).all()
    timeline_events = PatientTimeline.query.filter_by(patient_id=patient.id).order_by(PatientTimeline.created_at.desc()).limit(10).all()

    conditions_summary = {}
    for c in tooth_conditions:
        if c.condition != 'Healthy':
            conditions_summary[c.condition] = conditions_summary.get(c.condition, 0) + 1

    return render_template(
        'patient_portal.html',
        patient=patient,
        upcoming_appointment=upcoming_appointment,
        recent_appointments=recent_appointments,
        recent_prescriptions=recent_prescriptions,
        recent_clinical=recent_clinical,
        treatments=treatments,
        invoices=invoices,
        conditions_summary=conditions_summary,
        timeline_events=timeline_events
    )

@portal_bp.route('/book-appointment', methods=['GET', 'POST'])
@patient_required
def book_appointment():
    user_id = session.get('user_id')
    patient = Patient.query.filter_by(user_id=user_id).first_or_404()
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        apt_date = request.form.get('appointment_date')
        apt_time = request.form.get('appointment_time')
        chief_complaint = request.form.get('chief_complaint', '').strip()
        
        if not doctor_id or not apt_date or not apt_time:
            flash('Doctor, date, and time slot are required.', 'danger')
            return redirect(url_for('portal.book_appointment'))
            
        # Check double booking
        existing = Appointment.query.filter_by(
            doctor_id=int(doctor_id),
            appointment_date=apt_date,
            appointment_time=apt_time
        ).filter(Appointment.status.in_(['Scheduled', 'Confirmed', 'Checked In', 'In Chair'])).first()
        
        if existing:
            flash('Selected time slot was just booked by another patient. Please choose a different slot.', 'warning')
            return redirect(url_for('portal.book_appointment'))
            
        token = Appointment.generate_token(apt_date)
        apt = Appointment(
            token_number=token,
            patient_id=patient.id,
            doctor_id=int(doctor_id),
            appointment_date=apt_date,
            appointment_time=apt_time,
            reason=chief_complaint or 'General Dental Consultation',
            status='Scheduled',
            notes='Booked online via Patient Portal'
        )
        db.session.add(apt)
        db.session.flush()
        
        # Log to timeline
        doc = db.session.get(Doctor, int(doctor_id))
        timeline = PatientTimeline(
            patient_id=patient.id,
            event_type='appointment',
            title=f'Appointment Scheduled with Dr. {doc.name if doc else "Doctor"}',
            description=f'Token #{token} for {apt_date} at {apt_time}. Reason: {apt.chief_complaint}',
            badge_color='info',
            icon='fa-calendar-check',
            created_by=patient.full_name
        )
        db.session.add(timeline)
        db.session.commit()
        
        flash(f'Appointment confirmed! Your Queue Token is #{token}.', 'success')
        return redirect(url_for('portal.dashboard'))
        
    doctors = Doctor.query.filter_by(is_active=True).all()
    specialties = Specialty.query.filter_by(is_active=True).all()
    return render_template('book_appointment.html', patient=patient, doctors=doctors, specialties=specialties)
