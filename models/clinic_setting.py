from models import db

class ClinicSetting(db.Model):
    __tablename__ = 'clinic_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(150), default='DentiFlow Dental Care')
    tagline = db.Column(db.String(200), default='Precision Dentistry & Gentle Care')
    phone = db.Column(db.String(50), default='+1 (555) 234-5678')
    emergency_phone = db.Column(db.String(50), default='+1 (555) 911-DENT')
    email = db.Column(db.String(100), default='contact@dentiflow.com')
    address = db.Column(db.Text, default='100 Healthcare Blvd, Suite 400, New York, NY 10001')
    about_clinic = db.Column(db.Text, default='DentiFlow is a state-of-the-art multi-specialty dental hospital committed to providing world-class oral healthcare with warmth and precision.')
    currency_symbol = db.Column(db.String(10), default='$')
    tax_rate = db.Column(db.Float, default=5.0)  # Percentage
    working_hours = db.Column(db.String(100), default='Mon - Sat: 9:00 AM - 7:00 PM')
    invoice_footer_note = db.Column(db.Text, default='Thank you for trusting DentiFlow with your smile! For emergencies, please call our 24/7 helpline.')

    @classmethod
    def get_settings(cls):
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings
