import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # CRITICAL: Must be generated/provided via environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY environment variable is not set. "
            "For production on Render, this must be generated. "
            "For local development, set it in .env file."
        )

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
