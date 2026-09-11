from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required
from models import db, Patient, DentalToothCondition, ClinicSetting

dental_chart_bp = Blueprint('dental_chart', __name__)

@dental_chart_bp.route('/<int:patient_id>')
@login_required
def view_chart(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.index'))
        
    conditions = DentalToothCondition.query.filter_by(patient_id=patient_id).order_by(DentalToothCondition.tooth_number.asc()).all()
    chart_data = {c.tooth_number: c.to_dict() for c in conditions}
    settings = ClinicSetting.get_settings()
    
    return render_template('dental_chart.html', patient=patient, chart_data=chart_data, settings=settings)

@dental_chart_bp.route('/api/<int:patient_id>/update', methods=['POST'])
@login_required
def api_update_tooth(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        return jsonify({'success': False, 'error': 'Patient not found'}), 404
        
    data = request.get_json() or request.form
    tooth_number = int(data.get('tooth_number'))
    condition = data.get('condition', 'Healthy')
    surface = data.get('surface', 'Whole')
    notes = data.get('notes', '').strip()
    
    tooth_rec = DentalToothCondition.query.filter_by(patient_id=patient_id, tooth_number=tooth_number).first()
    if not tooth_rec:
        tooth_rec = DentalToothCondition(patient_id=patient_id, tooth_number=tooth_number)
        db.session.add(tooth_rec)
        
    tooth_rec.condition = condition
    tooth_rec.surface = surface
    tooth_rec.notes = notes
    tooth_rec.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'tooth': tooth_rec.to_dict()})

@dental_chart_bp.route('/<int:patient_id>/save-form', methods=['POST'])
@login_required
def save_form(patient_id):
    patient = db.session.get(Patient, patient_id)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients.index'))
        
    tooth_number = int(request.form.get('tooth_number'))
    condition = request.form.get('condition', 'Healthy')
    surface = request.form.get('surface', 'Whole')
    notes = request.form.get('notes', '').strip()
    
    tooth_rec = DentalToothCondition.query.filter_by(patient_id=patient_id, tooth_number=tooth_number).first()
    if not tooth_rec:
        tooth_rec = DentalToothCondition(patient_id=patient_id, tooth_number=tooth_number)
        db.session.add(tooth_rec)
        
    tooth_rec.condition = condition
    tooth_rec.surface = surface
    tooth_rec.notes = notes
    tooth_rec.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash(f'Tooth #{tooth_number} updated to {condition} ({surface})!', 'success')
    return redirect(request.referrer or url_for('patients.detail', patient_id=patient_id, tab='chart'))
