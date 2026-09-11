import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Determine if running in production (Render.com)
    is_production = os.environ.get('RENDER') == 'true'
    
    # Handle SECRET_KEY with environment awareness
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        if is_production:
            # Production: MUST have SECRET_KEY from environment
            raise ValueError(
                "CRITICAL: SECRET_KEY environment variable is not set. "
                "Render.com must auto-generate this via render.yaml. "
                "Ensure 'generateValue: true' is set for SECRET_KEY in render.yaml."
            )
        else:
            # Development: Use temporary fallback
            SECRET_KEY = 'dev-key-change-in-production-2026'

    # Support Render persistent disk at /data, or local SQLite fallback
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url and not _db_url.startswith('sqlite:///'):
        # If it's a plain path like /data/dentiflow.db, convert to URI
        _db_url = 'sqlite:///' + _db_url
    SQLALCHEMY_DATABASE_URI = _db_url or 'sqlite:///' + os.path.join(basedir, 'database', 'dentiflow.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clinic defaults
    CLINIC_NAME = os.environ.get('CLINIC_NAME', 'DentiFlow Dental Care & Implant Center')
    CLINIC_CURRENCY = os.environ.get('CLINIC_CURRENCY', '$')
    CLINIC_TAX_RATE = float(os.environ.get('CLINIC_TAX_RATE', 5.0))
