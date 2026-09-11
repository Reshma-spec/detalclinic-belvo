import os
from flask import Flask, render_template
from config import Config
from models import db, ClinicSetting, Patient, Doctor, User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize SQLAlchemy database
    db.init_app(app)

    # Register Route Blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.patients import patients_bp
    from routes.appointments import appointments_bp
    from routes.queue import queue_bp
    from routes.clinical import clinical_bp
    from routes.dental_chart import dental_chart_bp
    from routes.treatments import treatments_bp
    from routes.billing import billing_bp
    from routes.inventory import inventory_bp
    from routes.reports import reports_bp
    from routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp, url_prefix='/patients')
    app.register_blueprint(appointments_bp, url_prefix='/appointments')
    app.register_blueprint(queue_bp, url_prefix='/queue')
    app.register_blueprint(clinical_bp, url_prefix='/clinical')
    app.register_blueprint(dental_chart_bp, url_prefix='/chart')
    app.register_blueprint(treatments_bp, url_prefix='/treatments')
    app.register_blueprint(billing_bp, url_prefix='/billing')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    # Global Context Processor for Navbar Quick Actions & Settings
    @app.context_processor
    def inject_globals():
        try:
            settings = ClinicSetting.get_settings()
            all_patients_list = Patient.query.order_by(Patient.full_name.asc()).all()
            all_doctors_list = Doctor.query.filter_by(is_active=True).all()
        except Exception:
            settings = None
            all_patients_list = []
            all_doctors_list = []
        return {
            'settings': settings,
            'all_patients_list': all_patients_list,
            'all_doctors_list': all_doctors_list
        }

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Auto-create database tables on startup
    with app.app_context():
        db.create_all()
        # Ensure default settings row exists
        ClinicSetting.get_settings()
        # Auto-seed default admin on first run (if no users exist)
        if User.query.count() == 0:
            from werkzeug.security import generate_password_hash
            admin = User(
                username='admin',
                email='admin@dentiflow.com',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            admin.password_hash = generate_password_hash('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[DentiFlow] Default admin user created: admin / admin123")

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    is_production = os.environ.get('RENDER', False)
    print("=" * 60)
    print("  DentiFlow - Dental Clinic Owner Management System")
    if is_production:
        print(f"  Running on port {port} (production)")
    else:
        print(f"  Running locally on http://127.0.0.1:{port}")
        print("  Default Admin Login: admin / admin123")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=not is_production)
