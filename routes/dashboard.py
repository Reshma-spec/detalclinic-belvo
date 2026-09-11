from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, session, jsonify
from routes.auth import login_required
from models import db, Patient, Doctor, Appointment, TreatmentPlan, Invoice, InventoryItem, Payment, ClinicSetting

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    today_str = date.today().strftime('%Y-%m-%d')
    current_month_str = date.today().strftime('%Y-%m')
    
    # KPI Calculations
    today_appointments_count = Appointment.query.filter_by(appointment_date=today_str).count()
    total_patients_count = Patient.query.count()
    
    # New patients this month
    new_patients_count = Patient.query.filter(
        Patient.registration_date >= datetime(date.today().year, date.today().month, 1)
    ).count()
    
    # Today's Revenue (from Payments made today)
    today_payments = Payment.query.filter_by(payment_date=today_str).all()
    today_revenue = sum(p.amount for p in today_payments)
    
    # Total Outstanding Balance
    all_invoices = Invoice.query.all()
    pending_payments_total = sum(inv.balance_amount for inv in all_invoices)
    
    # Active Treatments
    active_treatments_count = TreatmentPlan.query.filter(
        TreatmentPlan.status.in_(['Accepted', 'In Progress'])
    ).count()
    
    # Low stock items count & list
    all_inventory = InventoryItem.query.all()
    low_stock_items = [item for item in all_inventory if item.is_low_stock]
    low_stock_count = len(low_stock_items)
    
    # Today's appointments list
    today_appointments = Appointment.query.filter_by(appointment_date=today_str)        .order_by(Appointment.appointment_time.asc()).all()
        
    # Recent Patients
    recent_patients = Patient.query.order_by(Patient.registration_date.desc()).limit(5).all()
    
    # Upcoming Appointments (Next 7 days excluding today)
    tomorrow_str = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    next_week_str = (date.today() + timedelta(days=7)).strftime('%Y-%m-%d')
    upcoming_appointments = Appointment.query.filter(
        Appointment.appointment_date >= tomorrow_str,
        Appointment.appointment_date <= next_week_str
    ).order_by(Appointment.appointment_date.asc(), Appointment.appointment_time.asc()).limit(6).all()
    
    # Prepare 6-month Revenue Trend data for Chart.js
    month_labels = []
    revenue_data = []
    
    for i in range(5, -1, -1):
        target_month_date = date.today() - timedelta(days=i*30)
        m_str = target_month_date.strftime('%Y-%m')
        m_label = target_month_date.strftime('%b %Y')
        month_labels.append(m_label)
        
        # Sum payments in this month
        month_payments = Payment.query.filter(Payment.payment_date.like(f'{m_str}%')).all()
        m_rev = sum(p.amount for p in month_payments)
        revenue_data.append(m_rev)
        
    # Appointment Status breakdown for doughnut chart
    scheduled_count = Appointment.query.filter_by(status='Scheduled').count()
    confirmed_count = Appointment.query.filter_by(status='Confirmed').count()
    completed_count = Appointment.query.filter_by(status='Completed').count()
    cancelled_count = Appointment.query.filter_by(status='Cancelled').count()
    in_treatment_count = Appointment.query.filter_by(status='In Treatment').count()
    
    settings = ClinicSetting.get_settings()
    
    return render_template(
        'dashboard.html',
        today_appointments_count=today_appointments_count,
        total_patients_count=total_patients_count,
        new_patients_count=new_patients_count,
        today_revenue=today_revenue,
        pending_payments_total=pending_payments_total,
        active_treatments_count=active_treatments_count,
        low_stock_count=low_stock_count,
        low_stock_items=low_stock_items[:5],
        today_appointments=today_appointments,
        recent_patients=recent_patients,
        upcoming_appointments=upcoming_appointments,
        month_labels=month_labels,
        revenue_data=revenue_data,
        appointment_stats={
            'Scheduled': scheduled_count,
            'Confirmed': confirmed_count,
            'Completed': completed_count,
            'Cancelled': cancelled_count,
            'In Treatment': in_treatment_count
        },
        settings=settings
    )
