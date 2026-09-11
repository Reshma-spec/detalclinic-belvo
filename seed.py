import os
from datetime import datetime, date, timedelta
from app import create_app
from models import (
    db, User, ClinicSetting, Specialty, Doctor, Patient, Appointment,
    ClinicalRecord, Prescription, PrescriptionItem, DentalToothCondition,
    TreatmentPlan, Invoice, InvoiceItem, Payment, InventoryItem, PatientTimeline
)

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing and rebuilding database with rich healthcare demo data...")
        db.drop_all()
        db.create_all()

        # 1. Clinic Settings
        clinic = ClinicSetting(
            clinic_name="DentiFlow Dental Care & Implant Center",
            tagline="Precision Dentistry & Gentle Compassionate Care",
            phone="+1 (555) 382-9000",
            emergency_phone="+1 (555) 911-DENT",
            email="contact@dentiflowcare.com",
            address="450 Lexington Avenue, Suite 1200, New York, NY 10017",
            about_clinic="DentiFlow is a state-of-the-art multi-specialty dental organization committed to providing world-class oral healthcare with warmth and precision.",
            currency_symbol="$",
            tax_rate=5.0,
            working_hours="Mon - Sat: 8:30 AM - 7:00 PM",
            invoice_footer_note="Thank you for trusting DentiFlow with your smile! For emergencies, please call our 24/7 helpline."
        )
        db.session.add(clinic)

        # 2. Dental Specialties
        specialties_data = [
            ("General Dentistry", "general_dentistry", "Comprehensive oral exams, cleanings, and preventive care.", "fa-tooth"),
            ("Cosmetic Dentistry", "cosmetic_dentistry", "Teeth whitening, veneers, and smile makeovers.", "fa-wand-magic-sparkles"),
            ("Endodontics", "endodontics", "Root canal therapy and dental pulp treatment.", "fa-notes-medical"),
            ("Implantology", "implantology", "Dental implants and permanent tooth replacement.", "fa-wrench"),
            ("Oral Surgery", "oral_surgery", "Tooth extractions, wisdom tooth surgery, and bone grafting.", "fa-scalpel"),
            ("Orthodontics", "orthodontics", "Braces, aligners, and bite correction.", "fa-teeth-open"),
            ("Pedodontics", "pedodontics", "Specialized pediatric dental care for kids and teens.", "fa-child"),
            ("Periodontics", "periodontics", "Gum disease treatment and deep periodontal scaling.", "fa-shield-halved"),
            ("Prosthodontics", "prosthodontics", "Crowns, bridges, and complete dentures.", "fa-crown")
        ]

        specialty_objs = {}
        for name, code, desc, icon in specialties_data:
            spec = Specialty(name=name, code=code, description=desc, icon=icon, is_active=True)
            db.session.add(spec)
            specialty_objs[code] = spec
        db.session.flush()

        # 3. User Accounts (Admin, Doctors, Receptionist, Patient)
        admin_user = User(
            username="admin",
            email="admin@dentiflow.com",
            full_name="Dr. Alexander Wright",
            role="admin",
            phone="+1 (555) 100-0001"
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)

        doc1_user = User(
            username="dr.smith",
            email="dr.smith@dentiflow.com",
            full_name="Dr. Sarah Smith",
            role="doctor",
            phone="+1 (555) 100-0002"
        )
        doc1_user.set_password("doctor123")
        db.session.add(doc1_user)

        doc2_user = User(
            username="dr.chen",
            email="dr.chen@dentiflow.com",
            full_name="Dr. Michael Chen",
            role="doctor",
            phone="+1 (555) 100-0003"
        )
        doc2_user.set_password("doctor123")
        db.session.add(doc2_user)

        recept_user = User(
            username="receptionist",
            email="reception@dentiflow.com",
            full_name="Emily Johnson",
            role="receptionist",
            phone="+1 (555) 100-0004"
        )
        recept_user.set_password("recept123")
        db.session.add(recept_user)

        patient_user = User(
            username="patient1",
            email="john.doe@example.com",
            full_name="John Doe",
            role="patient",
            phone="+1 (555) 234-5678"
        )
        patient_user.set_password("patient123")
        db.session.add(patient_user)
        db.session.flush()

        # 4. Doctors
        doc1 = Doctor(
            user_id=doc1_user.id,
            specialty_id=specialty_objs['general_dentistry'].id,
            name="Sarah Smith",
            specialization="General & Cosmetic Dentistry",
            qualification="BDS, MDS (Cosmetic)",
            years_experience=12,
            bio="Dr. Sarah Smith specializes in aesthetic smile transformations and gentle preventive dentistry with 12+ years of clinical excellence.",
            license_number="DDS-NY-49201",
            phone="+1 (555) 100-0002",
            email="dr.smith@dentiflow.com",
            consultation_fee=75.0,
            working_days="Mon, Tue, Wed, Thu, Fri",
            working_hours_start="09:00",
            working_hours_end="17:00",
            color_code="#0284c7"
        )

        doc2 = Doctor(
            user_id=doc2_user.id,
            specialty_id=specialty_objs['endodontics'].id,
            name="Michael Chen",
            specialization="Endodontics & Implantology",
            qualification="BDS, MDS (Endodontics)",
            years_experience=15,
            bio="Dr. Michael Chen is a renowned root canal specialist and implantologist dedicated to painless tooth preservation techniques.",
            license_number="DDS-NY-38104",
            phone="+1 (555) 100-0003",
            email="dr.chen@dentiflow.com",
            consultation_fee=90.0,
            working_days="Mon, Wed, Thu, Sat",
            working_hours_start="10:00",
            working_hours_end="18:00",
            color_code="#0d9488"
        )
        db.session.add_all([doc1, doc2])
        db.session.flush()

        # 5. Patients
        p1 = Patient(
            user_id=patient_user.id,
            patient_code="PAT-2026-0001",
            full_name="John Doe",
            age=34,
            gender="Male",
            phone="+1 (555) 234-5678",
            email="john.doe@example.com",
            dob="1992-05-14",
            address="742 Evergreen Terrace, Springfield",
            blood_group="O+",
            emergency_contact="Mary Doe (Wife) - +1 (555) 234-5679",
            medical_history="Mild hypertension. No surgical history.",
            allergies="Penicillin",
            current_medications="Lisinopril 5mg daily"
        )
        p2 = Patient(
            patient_code="PAT-2026-0002",
            full_name="Jane Miller",
            age=28,
            gender="Female",
            phone="+1 (555) 876-5432",
            email="jane.m@example.com",
            dob="1998-11-20",
            address="123 Maple Street, Apt 4B, Brooklyn, NY",
            blood_group="A+",
            emergency_contact="Robert Miller (Father) - +1 (555) 876-0000",
            medical_history="Asthma",
            allergies="Latex",
            current_medications="Albuterol inhaler"
        )
        db.session.add_all([p1, p2])
        db.session.flush()

        # 6. Initialize Adult 32 Teeth as Healthy for both patients
        for p in [p1, p2]:
            for tooth_num in range(1, 33):
                cond_val = 'Healthy'
                if p == p1 and tooth_num == 14:
                    cond_val = 'Caries'
                elif p == p1 and tooth_num == 19:
                    cond_val = 'Root Canal'
                elif p == p2 and tooth_num == 3:
                    cond_val = 'Crown'

                tc = DentalToothCondition(
                    patient_id=p.id,
                    tooth_number=tooth_num,
                    condition=cond_val,
                    surface='Whole',
                    notes='Initial oral evaluation'
                )
                db.session.add(tc)

        # 7. Patient Timelines
        tl1 = PatientTimeline(
            patient_id=p1.id,
            event_type="registration",
            title="Patient Account Registered",
            description="John Doe registered via DentiFlow online portal",
            badge_color="success",
            icon="fa-user-plus",
            created_by="John Doe"
        )
        tl2 = PatientTimeline(
            patient_id=p1.id,
            event_type="appointment",
            title="Initial Consultation Scheduled",
            description="Booked with Dr. Sarah Smith for general dental exam",
            badge_color="info",
            icon="fa-calendar-check",
            created_by="John Doe"
        )
        db.session.add_all([tl1, tl2])

        # 8. Appointments
        today_str = date.today().strftime('%Y-%m-%d')
        apt1 = Appointment(
            token_number=101,
            patient_id=p1.id,
            doctor_id=doc1.id,
            appointment_date=today_str,
            appointment_time="10:00",
            appointment_type="Consultation",
            status="Checked In",
            reason="Tooth sensitivity in upper left molar",
            notes="Patient arrived 10 min early."
        )
        apt2 = Appointment(
            token_number=102,
            patient_id=p2.id,
            doctor_id=doc2.id,
            appointment_date=today_str,
            appointment_time="11:30",
            appointment_type="Procedure",
            status="Scheduled",
            reason="Root canal follow-up examination",
            notes="Requires X-Ray review."
        )
        db.session.add_all([apt1, apt2])
        db.session.flush()

        # 9. Clinical Records & Prescriptions
        rec1 = ClinicalRecord(
            patient_id=p1.id,
            doctor_id=doc1.id,
            appointment_id=apt1.id,
            visit_date=today_str,
            chief_complaint="Tooth sensitivity in upper left molar (#14)",
            examination="Deep occlusal caries on tooth #14. Cold test positive.",
            diagnosis="Irreversible Pulpitis #14",
            procedure_performed="Direct pulp capping & temporary composite restoration.",
            prescriptions="Amoxicillin 500mg, Ibuprofen 400mg as needed.",
            clinical_notes="Recommended Root Canal Treatment & Crown."
        )
        db.session.add(rec1)
        db.session.flush()

        rx1 = Prescription(
            rx_number="RX-2026-0001",
            patient_id=p1.id,
            doctor_id=doc1.id,
            clinical_record_id=rec1.id,
            prescription_date=today_str,
            diagnosis="Irreversible Pulpitis #14",
            notes="Take medications after meals. Complete full antibiotic course."
        )
        db.session.add(rx1)
        db.session.flush()

        item1 = PrescriptionItem(
            prescription_id=rx1.id,
            medicine_name="Amoxicillin",
            dosage="500mg",
            frequency="1-0-1 (Twice Daily)",
            duration="5 Days",
            instructions="Take after breakfast & dinner"
        )
        item2 = PrescriptionItem(
            prescription_id=rx1.id,
            medicine_name="Ibuprofen",
            dosage="400mg",
            frequency="1-1-1 (As Needed)",
            duration="3 Days",
            instructions="For pain relief"
        )
        db.session.add_all([item1, item2])

        # 10. Invoices & Payments
        inv1 = Invoice(
            invoice_number="INV-2026-0001",
            patient_id=p1.id,
            doctor_id=doc1.id,
            invoice_date=today_str,
            subtotal=225.0,
            discount_type="fixed",
            discount_value=25.0,
            tax_percent=5.0,
            tax_amount=10.0,
            total_amount=210.0,
            paid_amount=150.0,
            balance_amount=60.0,
            payment_status="Partial",
            notes="Initial consultation & temporary restoration."
        )
        db.session.add(inv1)
        db.session.flush()

        inv_item1 = InvoiceItem(
            invoice_id=inv1.id,
            description="Comprehensive Oral Examination & Consultation",
            quantity=1,
            unit_price=75.0,
            total=75.0
        )
        inv_item2 = InvoiceItem(
            invoice_id=inv1.id,
            description="Composite Restoration (Tooth #14)",
            tooth_number="14",
            quantity=1,
            unit_price=150.0,
            total=150.0
        )
        db.session.add_all([inv_item1, inv_item2])

        pay1 = Payment(
            invoice_id=inv1.id,
            patient_id=p1.id,
            payment_date=today_str,
            amount=150.0,
            payment_method="Credit Card",
            reference_number="TXN-9948201",
            notes="Partial payment made at reception"
        )
        db.session.add(pay1)

        # 11. Inventory Items
        inventory_data = [
            ("Composite Resin A2", "Dental Materials", 45, 10, "Tubes", 35.0, "3M Dental", "Cabinet 2A"),
            ("Local Anesthetic (Lidocaine 2%)", "Pharmaceuticals", 120, 25, "Cartridges", 1.5, "Septodont", "Fridge 1"),
            ("ProTaper Gold Niti Files", "Endodontic Supplies", 8, 15, "Packs", 48.0, "Dentsply Sirona", "Drawer 4"),
            ("Sterile Dental Gloves (Medium)", "PPE & Hygiene", 350, 50, "Pairs", 0.4, "Ansell", "Supply Closet"),
            ("Dental Impression Material (Alginate)", "Impression Supplies", 18, 5, "Bags", 16.5, "Zhermack", "Shelf 3B")
        ]

        for name, cat, qty, min_qty, unit, price, supplier, loc in inventory_data:
            inv_item = InventoryItem(
                item_name=name, category=cat, quantity=qty, min_stock_level=min_qty,
                unit=unit, purchase_price=price, supplier_name=supplier, notes=f"Location: {loc}"
            )
            db.session.add(inv_item)

        db.session.commit()
        print("Database seeded successfully with specialties, doctors, patients, timeline, prescriptions, appointments, invoices, and inventory!")

if __name__ == '__main__':
    seed_database()
