from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request
from routes.auth import login_required
from models import db, Patient, Appointment, TreatmentPlan, Invoice, Payment, InventoryItem, ClinicSetting

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    report_type = request.args.get('type', 'financial') # financial, patients, appointments, treatments, inventory
    start_date = request.args.get('start_date', (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
    
    settings = ClinicSetting.get_settings()
    
    # Financial Analytics
    payments_in_range = Payment.query.filter(
        Payment.payment_date >= start_date,
        Payment.payment_date <= end_date
    ).order_by(Payment.payment_date.desc()).all()
    
    invoices_in_range = Invoice.query.filter(
        Invoice.invoice_date >= start_date,
        Invoice.invoice_date <= end_date
    ).all()
    
    period_revenue = sum(p.amount for p in payments_in_range)
    period_invoiced = sum(inv.total_amount for inv in invoices_in_range)
    outstanding_invoices = Invoice.query.filter(Invoice.balance_amount > 0).order_by(Invoice.balance_amount.desc()).all()
    total_outstanding_all = sum(inv.balance_amount for inv in outstanding_invoices)
    
    # Payment Method Breakdown
    methods = {}
    for p in payments_in_range:
        m = p.payment_method or 'Cash'
        methods[m] = methods.get(m, 0.0) + p.amount
        
    # Appointments in range
    appts_in_range = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).all()
    
    appt_status_counts = {}
    for a in appts_in_range:
        appt_status_counts[a.status] = appt_status_counts.get(a.status, 0) + 1
        
    # Treatments in range
    treatments = TreatmentPlan.query.all()
    treatment_status_counts = {}
    for t in treatments:
        treatment_status_counts[t.status] = treatment_status_counts.get(t.status, 0) + 1
        
    # Inventory
    inventory_items = InventoryItem.query.all()
    low_stock_list = [i for i in inventory_items if i.is_low_stock]
    total_inventory_val = sum(i.quantity * i.purchase_price for i in inventory_items)
    
    # Patients Registered
    all_patients = Patient.query.order_by(Patient.registration_date.desc()).all()
    
    return render_template(
        'reports.html',
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        period_revenue=period_revenue,
        period_invoiced=period_invoiced,
        total_outstanding_all=total_outstanding_all,
        payments_in_range=payments_in_range,
        outstanding_invoices=outstanding_invoices,
        payment_methods=methods,
        appts_in_range=appts_in_range,
        appt_status_counts=appt_status_counts,
        treatments=treatments,
        treatment_status_counts=treatment_status_counts,
        inventory_items=inventory_items,
        low_stock_list=low_stock_list,
        total_inventory_val=total_inventory_val,
        all_patients=all_patients,
        settings=settings
    )
