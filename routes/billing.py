from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required
from models import db, Invoice, InvoiceItem, Payment, Patient, Doctor, TreatmentPlan, ClinicSetting

billing_bp = Blueprint('billing', __name__)

def generate_invoice_number():
    year = datetime.now().year
    count = Invoice.query.count() + 1
    return f"INV-{year}-{count:04d}"

@billing_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', '').strip()
    search_query = request.args.get('search', '').strip()
    doctor_filter = request.args.get('doctor_id', '').strip()
    
    query = Invoice.query.join(Patient)
    
    if status_filter:
        query = query.filter(Invoice.payment_status == status_filter)
    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            (Invoice.invoice_number.ilike(search_like)) |
            (Patient.full_name.ilike(search_like)) |
            (Patient.patient_code.ilike(search_like))
        )
    if doctor_filter and doctor_filter.isdigit():
        query = query.filter(Invoice.doctor_id == int(doctor_filter))
        
    invoices = query.order_by(Invoice.invoice_date.desc(), Invoice.id.desc()).all()
    patients = Patient.query.order_by(Patient.full_name.asc()).all()
    doctors = Doctor.query.filter_by(is_active=True).all()
    treatments = TreatmentPlan.query.all()
    settings = ClinicSetting.get_settings()
    
    total_billed = sum(inv.total_amount for inv in invoices)
    total_received = sum(inv.paid_amount for inv in invoices)
    total_outstanding = sum(inv.balance_amount for inv in invoices)
    
    return render_template(
        'billing.html',
        invoices=invoices,
        patients=patients,
        doctors=doctors,
        treatments=treatments,
        status_filter=status_filter,
        search_query=search_query,
        doctor_filter=doctor_filter,
        total_billed=total_billed,
        total_received=total_received,
        total_outstanding=total_outstanding,
        today_str=date.today().strftime('%Y-%m-%d'),
        settings=settings
    )

@billing_bp.route('/add', methods=['POST'])
@login_required
def add():
    patient_id = request.form.get('patient_id')
    invoice_date = request.form.get('invoice_date', date.today().strftime('%Y-%m-%d')).strip()
    
    if not patient_id or not invoice_date:
        flash('Patient and Invoice Date are required.', 'danger')
        return redirect(url_for('billing.index'))
        
    doctor_id = request.form.get('doctor_id')
    doctor_id = int(doctor_id) if doctor_id and doctor_id.isdigit() else None
    
    treatment_id = request.form.get('treatment_id')
    treatment_id = int(treatment_id) if treatment_id and treatment_id.isdigit() else None
    
    settings = ClinicSetting.get_settings()
    tax_percent = float(request.form.get('tax_percent', settings.tax_rate))
    discount_type = request.form.get('discount_type', 'fixed')
    discount_value = float(request.form.get('discount_value', 0.0) or 0.0)
    
    invoice = Invoice(
        invoice_number=generate_invoice_number(),
        patient_id=int(patient_id),
        doctor_id=doctor_id,
        treatment_id=treatment_id,
        invoice_date=invoice_date,
        due_date=request.form.get('due_date', '').strip() or None,
        discount_type=discount_type,
        discount_value=discount_value,
        tax_percent=tax_percent,
        notes=request.form.get('notes', '').strip() or None
    )
    db.session.add(invoice)
    db.session.flush() # get invoice.id
    
    # Process line items
    descriptions = request.form.getlist('item_description[]')
    tooth_numbers = request.form.getlist('item_tooth[]')
    quantities = request.form.getlist('item_quantity[]')
    prices = request.form.getlist('item_price[]')
    
    for i in range(len(descriptions)):
        desc = descriptions[i].strip()
        if not desc:
            continue
        tooth = tooth_numbers[i].strip() if i < len(tooth_numbers) else ''
        qty = int(quantities[i]) if i < len(quantities) and quantities[i].isdigit() else 1
        price = float(prices[i]) if i < len(prices) and prices[i] else 0.0
        
        item = InvoiceItem(
            invoice_id=invoice.id,
            description=desc,
            tooth_number=tooth or None,
            quantity=qty,
            unit_price=price,
            total=round(qty * price, 2)
        )
        db.session.add(item)
        
    invoice.recalculate()
    
    # Check if initial payment made during creation
    initial_payment = request.form.get('initial_payment', '0')
    try:
        initial_pay_val = float(initial_payment)
    except ValueError:
        initial_pay_val = 0.0
        
    if initial_pay_val > 0:
        pay_amount = min(initial_pay_val, invoice.total_amount)
        payment = Payment(
            invoice_id=invoice.id,
            patient_id=invoice.patient_id,
            payment_date=invoice_date,
            amount=pay_amount,
            payment_method=request.form.get('payment_method', 'Cash'),
            reference_number=request.form.get('payment_ref', '').strip() or None,
            notes='Initial payment at time of invoice creation'
        )
        db.session.add(payment)
        invoice.recalculate()
        
    db.session.commit()
    flash(f'Invoice {invoice.invoice_number} created successfully!', 'success')
    return redirect(url_for('billing.detail', invoice_id=invoice.id))

@billing_bp.route('/<int:invoice_id>')
@login_required
def detail(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('billing.index'))
    invoice.recalculate()
    settings = ClinicSetting.get_settings()
    return render_template('invoice_detail.html', invoice=invoice, settings=settings)

@billing_bp.route('/<int:invoice_id>/pay', methods=['POST'])
@login_required
def record_payment(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('billing.index'))
        
    amount_str = request.form.get('amount', '0')
    try:
        amount = float(amount_str)
    except ValueError:
        amount = 0.0
        
    if amount <= 0:
        flash('Payment amount must be greater than zero.', 'danger')
        return redirect(url_for('billing.detail', invoice_id=invoice.id))
        
    if amount > invoice.balance_amount:
        amount = invoice.balance_amount
        
    payment = Payment(
        invoice_id=invoice.id,
        patient_id=invoice.patient_id,
        payment_date=request.form.get('payment_date', date.today().strftime('%Y-%m-%d')).strip(),
        amount=amount,
        payment_method=request.form.get('payment_method', 'Cash'),
        reference_number=request.form.get('reference_number', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None
    )
    db.session.add(payment)
    invoice.recalculate()
    db.session.commit()
    
    flash(f'Payment of {settings_currency()}{amount:.2f} recorded for Invoice {invoice.invoice_number}!', 'success')
    return redirect(url_for('billing.detail', invoice_id=invoice.id))

@billing_bp.route('/<int:invoice_id>/delete', methods=['POST'])
@login_required
def delete(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        flash('Invoice not found.', 'danger')
        return redirect(url_for('billing.index'))
    num = invoice.invoice_number
    db.session.delete(invoice)
    db.session.commit()
    flash(f'Invoice {num} deleted.', 'info')
    return redirect(url_for('billing.index'))

def settings_currency():
    s = ClinicSetting.get_settings()
    return s.currency_symbol if s else '$'
