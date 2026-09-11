from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, TreatmentPlan, Patient, Doctor, ClinicSetting

treatments_bp = Blueprint('treatments', __name__)

@treatments_bp.route('/')
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    doctor_filter = request.args.get('doctor_id', '').strip()
    
    query = TreatmentPlan.query.join(Patient)
    
    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            (Patient.full_name.ilike(search_like)) |
            (Patient.patient_code.ilike(search_like)) |
            (TreatmentPlan.treatment_name.ilike(search_like))
        )
        
    if status_filter:
        query = query.filter(TreatmentPlan.status == status_filter)
        
    if doctor_filter and doctor_filter.isdigit():
        query = query.filter(TreatmentPlan.doctor_id == int(doctor_filter))
        
    treatments = query.order_by(TreatmentPlan.created_at.desc()).all()
    patients = Patient.query.order_by(Patient.full_name.asc()).all()
    doctors = Doctor.query.filter_by(is_active=True).all()
    settings = ClinicSetting.get_settings()
    
    return render_template(
        'treatments.html',
        treatments=treatments,
        patients=patients,
        doctors=doctors,
        search_query=search_query,
        status_filter=status_filter,
        doctor_filter=doctor_filter,
        today_str=date.today().strftime('%Y-%m-%d'),
        settings=settings
    )

@treatments_bp.route('/add', methods=['POST'])
@login_required
def add():
    patient_id = request.form.get('patient_id')
    doctor_id = request.form.get('doctor_id')
    treatment_name = request.form.get('treatment_name', '').strip()
    
    if not patient_id or not doctor_id or not treatment_name:
        flash('Patient, Doctor, and Treatment Name are required.', 'danger')
        return redirect(request.referrer or url_for('treatments.index'))
        
    cost = request.form.get('estimated_cost', 0)
    try:
        cost = max(0.0, float(cost))
    except ValueError:
        cost = 0.0
        
    treatment = TreatmentPlan(
        patient_id=int(patient_id),
        doctor_id=int(doctor_id),
        treatment_name=treatment_name,
        tooth_number=request.form.get('tooth_number', '').strip() or None,
        description=request.form.get('description', '').strip() or None,
        estimated_cost=cost,
        status=request.form.get('status', 'Proposed'),
        start_date=request.form.get('start_date', '').strip() or None,
        expected_completion=request.form.get('expected_completion', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None
    )
    
    db.session.add(treatment)
    db.session.commit()
    
    flash(f'Treatment plan "{treatment_name}" created successfully!', 'success')
    return redirect(request.referrer or url_for('patients.detail', patient_id=patient_id, tab='treatments'))

@treatments_bp.route('/<int:treatment_id>/status', methods=['POST'])
@login_required
def update_status(treatment_id):
    treatment = db.session.get(TreatmentPlan, treatment_id)
    if not treatment:
        flash('Treatment plan not found.', 'danger')
        return redirect(url_for('treatments.index'))
        
    new_status = request.form.get('status')
    if new_status in ['Proposed', 'Accepted', 'In Progress', 'Completed', 'Cancelled']:
        treatment.status = new_status
        db.session.commit()
        flash(f'Treatment status updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
        
    return redirect(request.referrer or url_for('treatments.index'))

@treatments_bp.route('/<int:treatment_id>/edit', methods=['POST'])
@login_required
def edit(treatment_id):
    treatment = db.session.get(TreatmentPlan, treatment_id)
    if not treatment:
        flash('Treatment plan not found.', 'danger')
        return redirect(url_for('treatments.index'))
        
    treatment.doctor_id = int(request.form.get('doctor_id', treatment.doctor_id))
    treatment.treatment_name = request.form.get('treatment_name', treatment.treatment_name).strip()
    treatment.tooth_number = request.form.get('tooth_number', treatment.tooth_number).strip() or None
    treatment.description = request.form.get('description', treatment.description).strip() or None
    try:
        treatment.estimated_cost = max(0.0, float(request.form.get('estimated_cost', treatment.estimated_cost)))
    except ValueError:
        pass
    treatment.status = request.form.get('status', treatment.status)
    treatment.start_date = request.form.get('start_date', treatment.start_date).strip() or None
    treatment.expected_completion = request.form.get('expected_completion', treatment.expected_completion).strip() or None
    treatment.notes = request.form.get('notes', treatment.notes).strip() or None
    
    db.session.commit()
    flash('Treatment plan updated successfully.', 'success')
    return redirect(request.referrer or url_for('treatments.index'))

@treatments_bp.route('/<int:treatment_id>/delete', methods=['POST'])
@login_required
def delete(treatment_id):
    treatment = db.session.get(TreatmentPlan, treatment_id)
    if not treatment:
        flash('Treatment plan not found.', 'danger')
        return redirect(url_for('treatments.index'))
    patient_id = treatment.patient_id
    db.session.delete(treatment)
    db.session.commit()
    flash('Treatment plan removed.', 'info')
    return redirect(url_for('patients.detail', patient_id=patient_id, tab='treatments'))
