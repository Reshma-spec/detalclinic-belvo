import os
from datetime import datetime, date, timedelta
from app import create_app
from models import (
    db, User, ClinicSetting, Doctor, Patient, Appointment,
    ClinicalRecord, DentalToothCondition, TreatmentPlan,
    Invoice, InvoiceItem, Payment, InventoryItem
)

def seed_database():
    app = create_app()
    with app.app_context():
        print("Clearing and rebuilding database with realistic demo data...")
        db.drop_all()
        db.create_all()

        # 1. Clinic Settings
        clinic = ClinicSetting(
            clinic_name="DentiFlow Dental Care & Implant Center",
            tagline="Precision Dentistry & Gentle Compassionate Care",
            phone="+1 (555) 382-9000",
            email="contact@dentiflowcare.com",
            address="450 Lexington Avenue, Suite 1200, New York, NY 10017",
            currency_symbol="$",
            tax_rate=5.0,
            working_hours="Mon - Sat: 8:30 AM - 7:00 PM",
            invoice_footer_note="Thank you for trusting DentiFlow with your smile! Please follow post-op guidelines."
        )
        db.session.add(clinic)

        # 2. Users (Admin, Doctor, Receptionist)
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

        reception_user = User(
            username="reception",
            email="reception@dentiflow.com",
            full_name="Emily Davis",
            role="receptionist",
            phone="+1 (555) 100-0004"
        )
        reception_user.set_password("reception123")
        db.session.add(reception_user)
        db.session.flush()

        # 3. Doctor Profiles
        doc_owner = Doctor(
            user_id=admin_user.id,
            name="Alexander Wright",
            specialization="Implantology & Oral Surgery",
            license_number="DDS-NY-44821",
            phone=admin_user.phone,
            email=admin_user.email,
            consultation_fee=100.0,
            color_code="#0284c7"
        )
        db.session.add(doc_owner)

        doc_smith = Doctor(
            user_id=doc1_user.id,
            name="Sarah Smith",
            specialization="Endodontics & Restorative",
            license_number="DDS-NY-55912",
            phone=doc1_user.phone,
            email=doc1_user.email,
            consultation_fee=80.0,
            color_code="#0f766e"
        )
        db.session.add(doc_smith)

        doc_chen = Doctor(
            user_id=doc2_user.id,
            name="Michael Chen",
            specialization="Orthodontics & Pediatric",
            license_number="DDS-NY-66034",
            phone=doc2_user.phone,
            email=doc2_user.email,
            consultation_fee=75.0,
            color_code="#8b5cf6"
        )
        db.session.add(doc_chen)
        db.session.flush()

        # 4. Patients
        patients_data = [
            {
                "code": "PAT-2026-0001", "name": "Eleanor Vance", "age": 29, "gender": "Female",
                "phone": "+1 (555) 234-1101", "email": "eleanor.vance@gmail.com", "dob": "1997-04-12",
                "blood": "O+", "allergies": "Penicillin", "meds": "None",
                "history": "Occasional dental anxiety. Regular checkups.",
                "notes": "Prefers morning appointments."
            },
            {
                "code": "PAT-2026-0002", "name": "James Henderson", "age": 45, "gender": "Male",
                "phone": "+1 (555) 234-1102", "email": "j.henderson@corporate.com", "dob": "1981-08-23",
                "blood": "A+", "allergies": "None", "meds": "Amlodipine 5mg",
                "history": "Controlled hypertension.",
                "notes": "Undergoing full arch implant restoration."
            },
            {
                "code": "PAT-2026-0003", "name": "Sophia Martinez", "age": 22, "gender": "Female",
                "phone": "+1 (555) 234-1103", "email": "sophia.m@university.edu", "dob": "2004-11-05",
                "blood": "B+", "allergies": "Latex", "meds": "None",
                "history": "Wisdom teeth pain.",
                "notes": "Non-latex gloves required."
            },
            {
                "code": "PAT-2026-0004", "name": "Robert Miller", "age": 58, "gender": "Male",
                "phone": "+1 (555) 234-1104", "email": "rmiller58@outlook.com", "dob": "1968-02-14",
                "blood": "AB+", "allergies": "None", "meds": "Metformin 500mg",
                "history": "Type 2 Diabetes (HbA1c 6.4).",
                "notes": "Periodontal maintenance protocol every 3 months."
            },
            {
                "code": "PAT-2026-0005", "name": "Chloe Bennett", "age": 16, "gender": "Female",
                "phone": "+1 (555) 234-1105", "email": "c.bennett.parent@gmail.com", "dob": "2010-06-30",
                "blood": "O-", "allergies": "None", "meds": "None",
                "history": "Orthodontic alignment.",
                "notes": "Braces follow-up scheduled monthly."
            },
            {
                "code": "PAT-2026-0006", "name": "David Wilson", "age": 36, "gender": "Male",
                "phone": "+1 (555) 234-1106", "email": "david.w@tech.io", "dob": "1990-09-18",
                "blood": "A-", "allergies": "Sulfa drugs", "meds": "None",
                "history": "Mild bruxism.",
                "notes": "Night guard fabricated."
            }
        ]

        created_patients = []
        for p in patients_data:
            pat = Patient(
                patient_code=p["code"],
                full_name=p["name"],
                age=p["age"],
                gender=p["gender"],
                phone=p["phone"],
                email=p["email"],
                dob=p["dob"],
                address="New York, NY",
                blood_group=p["blood"],
                emergency_contact="Spouse/Family: +1 (555) 999-0000",
                allergies=p["allergies"],
                current_medications=p["meds"],
                medical_history=p["history"],
                notes=p["notes"]
            )
            db.session.add(pat)
            created_patients.append(pat)
        db.session.flush()

        # 5. Dental Chart Conditions initialization for all patients
        for pat in created_patients:
            for t_num in range(1, 33):
                cond_val = "Healthy"
                surf = "Whole"
                note = ""

                # Add realistic sample conditions for patients
                if pat.patient_code == "PAT-2026-0001":
                    if t_num == 3: cond_val = "Filled"; surf = "Occlusal"; note = "Composite class I"
                    elif t_num == 14: cond_val = "Caries"; surf = "Mesial"; note = "Incipient decay"
                    elif t_num == 19: cond_val = "Crown"; surf = "Whole"; note = "Zirconia crown"
                elif pat.patient_code == "PAT-2026-0002":
                    if t_num == 30: cond_val = "Implant"; surf = "Whole"; note = "Straumann 4.1mm"
                    elif t_num == 18: cond_val = "Missing"; surf = "Whole"; note = "Extracted 2024"
                    elif t_num == 19: cond_val = "Root Canal"; surf = "Whole"; note = "Completed RCT"
                elif pat.patient_code == "PAT-2026-0003":
                    if t_num in [1, 16, 17, 32]: cond_val = "Extraction Required"; note = "Impacted 3rd Molar"

                tooth_entry = DentalToothCondition(
                    patient_id=pat.id,
                    tooth_number=t_num,
                    condition=cond_val,
                    surface=surf,
                    notes=note
                )
                db.session.add(tooth_entry)

        # 6. Appointments
        today_str = date.today().strftime('%Y-%m-%d')
        yesterday_str = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        tomorrow_str = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')

        appointments_sample = [
            (created_patients[0].id, doc_smith.id, today_str, "09:00", "Consultation", "Scheduled", 1, "Routine checkup and cleaning"),
            (created_patients[1].id, doc_owner.id, today_str, "10:30", "Root Canal Treatment", "In Treatment", 2, "RCT stage 2 lower molar"),
            (created_patients[2].id, doc_owner.id, today_str, "11:45", "Tooth Extraction", "Waiting", 3, "Surgical extraction #32"),
            (created_patients[3].id, doc_smith.id, today_str, "14:00", "Scaling & Cleaning", "Scheduled", 4, "Periodontal maintenance"),
            (created_patients[4].id, doc_chen.id, tomorrow_str, "10:00", "Orthodontics", "Confirmed", 1, "Wire adjustment upper arch"),
            (created_patients[5].id, doc_smith.id, yesterday_str, "15:00", "Dental Filling", "Completed", 1, "Composite restoration #14")
        ]

        for p_id, d_id, a_date, a_time, a_type, st, token, reas in appointments_sample:
            appt = Appointment(
                patient_id=p_id,
                doctor_id=d_id,
                appointment_date=a_date,
                appointment_time=a_time,
                duration_minutes=30,
                appointment_type=a_type,
                reason=reas,
                status=st,
                token_number=token
            )
            db.session.add(appt)

        # 7. Clinical Records
        clin_rec1 = ClinicalRecord(
            patient_id=created_patients[0].id,
            doctor_id=doc_smith.id,
            visit_date=yesterday_str,
            chief_complaint="Sensitivity to cold foods on upper right teeth",
            examination="Cavity detected on tooth #14 mesial surface. Normal response to pulp vitality.",
            diagnosis="Class II Dental Caries #14",
            procedure_performed="Complete caries excavation, etch & bond, composite shade A2 placed.",
            prescriptions="Ibuprofen 400mg - 1 tablet PRN after food",
            clinical_notes="Patient tolerated procedure well. Advised flossing.",
            follow_up_date=tomorrow_str
        )
        db.session.add(clin_rec1)

        # 8. Treatment Plans
        tp1 = TreatmentPlan(
            patient_id=created_patients[0].id,
            doctor_id=doc_smith.id,
            treatment_name="Composite Restoration & Polishing",
            tooth_number="14",
            estimated_cost=150.0,
            status="Completed",
            start_date=yesterday_str,
            expected_completion=today_str,
            notes="Completed with high gloss polish."
        )
        db.session.add(tp1)

        tp2 = TreatmentPlan(
            patient_id=created_patients[1].id,
            doctor_id=doc_owner.id,
            treatment_name="Molar Root Canal & Porcelain Crown",
            tooth_number="19",
            estimated_cost=750.0,
            status="In Progress",
            start_date=today_str,
            expected_completion=tomorrow_str,
            notes="Stage 1 completed. Crown prep pending."
        )
        db.session.add(tp2)

        # 9. Invoices & Payments
        inv1 = Invoice(
            invoice_number="INV-2026-0001",
            patient_id=created_patients[0].id,
            doctor_id=doc_smith.id,
            treatment_id=1,
            invoice_date=yesterday_str,
            subtotal=150.0,
            discount_type="fixed",
            discount_value=0.0,
            tax_percent=5.0,
            notes="Paid in full via Card"
        )
        db.session.add(inv1)
        db.session.flush()

        item1 = InvoiceItem(invoice_id=inv1.id, description="Composite Restoration Tooth #14", tooth_number="14", quantity=1, unit_price=150.0, total=150.0)
        db.session.add(item1)
        inv1.recalculate()

        pay1 = Payment(invoice_id=inv1.id, patient_id=created_patients[0].id, payment_date=yesterday_str, amount=inv1.total_amount, payment_method="Credit Card", reference_number="TXN-991204")
        db.session.add(pay1)
        inv1.recalculate()

        inv2 = Invoice(
            invoice_number="INV-2026-0002",
            patient_id=created_patients[1].id,
            doctor_id=doc_owner.id,
            treatment_id=2,
            invoice_date=today_str,
            subtotal=750.0,
            discount_type="percentage",
            discount_value=10.0,
            tax_percent=5.0,
            notes="Partial advance paid for RCT & Crown"
        )
        db.session.add(inv2)
        db.session.flush()

        item2_a = InvoiceItem(invoice_id=inv2.id, description="Molar Endodontic Therapy (RCT) #19", tooth_number="19", quantity=1, unit_price=450.0, total=450.0)
        item2_b = InvoiceItem(invoice_id=inv2.id, description="Zirconia Crown Restoration #19", tooth_number="19", quantity=1, unit_price=300.0, total=300.0)
        db.session.add(item2_a)
        db.session.add(item2_b)
        inv2.recalculate()

        pay2 = Payment(invoice_id=inv2.id, patient_id=created_patients[1].id, payment_date=today_str, amount=350.0, payment_method="Cash", reference_number="REC-0012")
        db.session.add(pay2)
        inv2.recalculate()

        # 10. Inventory Items
        inventory_data = [
            ("Composite Resin Syringes (A2/A3)", "Materials", 18, "Pack", 10, 35.0, "3M Dental", "2027-12-31"),
            ("Dental Anesthetic Cartridges (2% Lidocaine)", "Pharmaceuticals", 45, "Box", 15, 48.0, "Septodont", "2027-08-30"),
            ("Disposable Examination Gloves (M)", "PPE", 8, "Box", 12, 11.50, "Medline", "2028-05-31"),  # Low stock
            ("Surgical Face Masks Level 3", "PPE", 5, "Box", 10, 8.0, "Halyard", "2028-01-31"),          # Low stock
            ("Endodontic K-Files Assorted 25mm", "Instruments", 24, "Pack", 8, 18.0, "Dentsply", "2029-12-31"),
            ("Alginate Impression Material", "Materials", 14, "Bag", 5, 22.0, "Kerr Dental", "2027-03-15"),
            ("Dental Micro-applicator Brushes", "Disposables", 50, "Box", 15, 6.50, "Microbrush", "2029-01-01"),
            ("Zirconia Crown Blanks", "Materials", 12, "Pcs", 5, 65.0, "Ivoclar", "2030-01-01"),
            ("Suture Needles 4-0 Silk", "Consumables", 6, "Box", 10, 24.0, "Ethicon", "2027-01-15"),      # Low stock
            ("Prophy Paste Mint (Coarse)", "Consumables", 16, "Jar", 5, 14.0, "Premier Dental", "2027-10-31"),
            ("Dental Bibs Disposable (Pack of 500)", "Disposables", 9, "Box", 4, 29.0, "Crosstex", "2029-06-30"),
            ("Dental X-Ray Sensor Barrier Sleeves", "Disposables", 30, "Box", 10, 16.0, "Patterson", "2028-11-30")
        ]

        for name, cat, qty, unit, min_s, price, supp, exp in inventory_data:
            item = InventoryItem(
                item_name=name,
                category=cat,
                quantity=qty,
                unit=unit,
                min_stock_level=min_s,
                purchase_price=price,
                supplier_name=supp,
                expiry_date=exp,
                last_restocked=today_str
            )
            db.session.add(item)

        db.session.commit()
        print("SEEDING COMPLETE!")
        print("Demo Accounts:")
        print(" - Admin / Owner: admin / admin123")
        print(" - Doctor:        dr.smith / doctor123")
        print(" - Receptionist:  reception / reception123")

if __name__ == '__main__':
    seed_database()
