from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import db, User

auth_bp = Blueprint('auth', __name__)

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return db.session.get(User, user_id)
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('role', 'receptionist')
            if user_role not in roles:
                flash('Access denied. You do not have permission for this section.', 'danger')
                return render_template('errors/403.html'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect_by_role(session.get('role'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('This account is disabled. Please contact the clinic administrator.', 'danger')
                return render_template('login.html')
                
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['full_name'] = user.full_name
            session['role'] = user.role
            
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('//'):
                return redirect(next_page)
            return redirect_by_role(user.role)
        else:
            flash('Invalid username/email or password.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect_by_role(session.get('role'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        age = request.form.get('age', '').strip()
        gender = request.form.get('gender', 'Other')
        
        if not full_name or not username or not email or not password or not phone:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')
            
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email is already registered.', 'warning')
            return render_template('register.html')
            
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role='patient',
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Auto-create linked Patient record
        from models import Patient, PatientTimeline
        p_code = f"PAT-{user.id:04d}"
        patient = Patient(
            user_id=user.id,
            patient_code=p_code,
            full_name=full_name,
            phone=phone,
            email=email,
            age=int(age) if age and age.isdigit() else None,
            gender=gender
        )
        db.session.add(patient)
        db.session.flush()
        
        # Log to patient timeline
        timeline = PatientTimeline(
            patient_id=patient.id,
            event_type='registration',
            title='Account Created',
            description='Patient registered online via DentiFlow portal',
            badge_color='success',
            icon='fa-user-plus',
            created_by=full_name
        )
        db.session.add(timeline)
        db.session.commit()
        
        # Auto-login
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['full_name'] = user.full_name
        session['role'] = user.role
        
        flash(f'Account created successfully! Welcome to DentiFlow, {full_name}.', 'success')
        return redirect(url_for('portal.dashboard'))
        
    return render_template('register.html')

def redirect_by_role(role):
    if role == 'patient':
        return redirect(url_for('portal.dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctors.dashboard'))
    else:
        return redirect(url_for('dashboard.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if 'user_id' in session:
        return redirect_by_role(session.get('role'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not email:
            flash('Please enter your registered email address.', 'danger')
            return render_template('forgot_password.html')

        user = User.query.filter_by(email=email).first()
        if user and user.is_active:
            from models import PasswordResetToken
            raw_token = PasswordResetToken.generate_token_for_user(user.id)
            reset_url = url_for('auth.reset_password', token=raw_token, _external=True)

            # Development Mode Email Logger / Safe display
            import os
            email_mode = os.environ.get('EMAIL_MODE', 'development')
            if email_mode == 'development':
                print("=" * 60)
                print(f"[DentiFlow Security Engine] Password Reset Link for {user.email}:")
                print(reset_url)
                print("=" * 60)
                flash(f'[DEV MODE] Password reset link generated: {reset_url}', 'info')

        # Generic response to prevent email enumeration attacks
        flash('If an account exists for this email address, a password reset link has been sent. Please check your inbox.', 'success')
        return render_template('forgot_password.html', email_sent=True)

    return render_template('forgot_password.html', email_sent=False)

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'user_id' in session:
        return redirect_by_role(session.get('role'))

    raw_token = request.args.get('token', '').strip() or request.form.get('token', '').strip()
    if not raw_token:
        flash('Invalid or missing password reset token.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    from models import PasswordResetToken
    token_entry = PasswordResetToken.verify_token(raw_token)
    if not token_entry:
        flash('This password reset link is invalid or has expired (valid for 30 minutes). Please request a new link.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('reset_password.html', token=raw_token)

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('reset_password.html', token=raw_token)

        user = db.session.get(User, token_entry.user_id)
        if not user or not user.is_active:
            flash('User account not found or disabled.', 'danger')
            return redirect(url_for('auth.login'))

        # Update password & invalidate token
        user.set_password(password)
        token_entry.used = True
        db.session.commit()

        flash('Password successfully changed. Please sign in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=raw_token)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('auth.login'))
