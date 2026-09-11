import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dentiflow-local-dev-secret-key-2026'

    # SQLite database configuration in database/ directory inside project root
    db_dir = os.path.join(basedir, 'database')
    os.makedirs(db_dir, exist_ok=True)
    
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        if not _db_url.startswith('sqlite:///') and not _db_url.startswith('postgresql://') and not _db_url.startswith('mysql://'):
            _db_url = 'sqlite:///' + _db_url
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(db_dir, 'dentiflow.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Clinic defaults
    CLINIC_NAME = os.environ.get('CLINIC_NAME', 'DentiFlow Dental Care & Implant Center')
    CLINIC_CURRENCY = os.environ.get('CLINIC_CURRENCY', '$')
    CLINIC_TAX_RATE = float(os.environ.get('CLINIC_TAX_RATE', 5.0))

