from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.clinic_setting import ClinicSetting
from models.doctor import Doctor
from models.patient import Patient
from models.appointment import Appointment
from models.clinical_record import ClinicalRecord
from models.dental_chart import DentalToothCondition
from models.treatment import TreatmentPlan
from models.invoice import Invoice, InvoiceItem
from models.payment import Payment
from models.inventory import InventoryItem
