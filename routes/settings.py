from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required, role_required
from models import db, ClinicSetting, User, Doctor

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@login_required
@role_required('admin')
def index():
    settings = ClinicSetting.get_settings()
    users = User.query.order_by(User.role.asc(), User.full_name.asc()).all()
    doctors = Doctor.query.all()
    return render_template('settings.html', settings=settings, users=users, doctors=doctors)

@settings_bp.route('/clinic/update', methods=['POST'])
@login_required
@role_required('admin')
def update_clinic():
    settings = ClinicSetting.get_settings()
    settings.clinic_name = request.form.get('clinic_name', settings.clinic_name).strip()
    settings.tagline = request.form.get('tagline', settings.tagline).strip()
    settings.phone = request.form.get('phone', settings.phone).strip()
    settings.email = request.form.get('email', settings.email).strip()
    settings.address = request.form.get('address', settings.address).strip()
    settings.currency_symbol = request.form.get('currency_symbol', settings.currency_symbol).strip()
    try:
        settings.tax_rate = float(request.form.get('tax_rate', settings.tax_rate))
    except ValueError:
        pass
    settings.working_hours = request.form.get('working_hours', settings.working_hours).strip()
    settings.invoice_footer_note = request.form.get('invoice_footer_note', settings.invoice_footer_note).strip()
    
    db.session.commit()
    flash('Clinic settings saved successfully!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/user/add', methods=['POST'])
@login_required
@role_required('admin')
def add_user():
    username = request.form.get('username', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    full_name = request.form.get('full_name', '').strip()
    role = request.form.get('role', 'receptionist')
    
    if not username or not email or not password or not full_name:
        flash('All user fields are required.', 'danger')
        return redirect(url_for('settings.index'))
        
    existing = User.query.filter((User.username == username) | (User.email == email)).first()
    if existing:
        flash('A user with that username or email already exists.', 'danger')
        return redirect(url_for('settings.index'))
        
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        role=role,
        phone=request.form.get('phone', '').strip() or None
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    
    if role == 'doctor':
        doc = Doctor(
            user_id=user.id,
            name=full_name,
            specialization=request.form.get('specialization', 'General Dentistry'),
            license_number=request.form.get('license_number', '').strip() or None,
            phone=user.phone,
            email=email,
            consultation_fee=float(request.form.get('consultation_fee', 50.0) or 50.0),
            working_days='Mon, Tue, Wed, Thu, Fri, Sat'
        )
        db.session.add(doc)
        
    db.session.commit()
    flash(f'User {user.full_name} ({user.role}) added successfully!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('settings.index'))
        
    if user.username == 'admin':
        flash('Cannot disable the primary admin account.', 'danger')
        return redirect(url_for('settings.index'))
        
    user.is_active = not user.is_active
    db.session.commit()
    status_str = 'enabled' if user.is_active else 'disabled'
    flash(f'Account {user.username} has been {status_str}.', 'info')
    return redirect(url_for('settings.index'))
