from datetime import datetime
from models import db

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='SET NULL'), nullable=True)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatment_plans.id', ondelete='SET NULL'), nullable=True)
    
    invoice_date = db.Column(db.String(10), nullable=False)
    due_date = db.Column(db.String(10), nullable=True)
    
    subtotal = db.Column(db.Float, default=0.0)
    discount_type = db.Column(db.String(20), default='fixed')
    discount_value = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_percent = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)
    balance_amount = db.Column(db.Float, default=0.0)
    
    payment_status = db.Column(db.String(30), default='Pending')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='invoice', lazy='dynamic', cascade='all, delete-orphan', order_by='desc(Payment.payment_date)')

    def recalculate(self):
        self.subtotal = sum(item.total for item in self.items)
        if self.discount_type == 'percentage':
            self.discount_amount = round((self.subtotal * (float(self.discount_value or 0) / 100.0)), 2)
        else:
            self.discount_amount = min(self.subtotal, round(float(self.discount_value or 0), 2))
            
        taxable = max(0.0, self.subtotal - self.discount_amount)
        self.tax_amount = round(taxable * (float(self.tax_percent or 0) / 100.0), 2)
        self.total_amount = round(taxable + self.tax_amount, 2)
        
        total_paid = sum(payment.amount for payment in self.payments)
        self.paid_amount = round(total_paid, 2)
        self.balance_amount = max(0.0, round(self.total_amount - self.paid_amount, 2))
        
        if self.paid_amount >= self.total_amount and self.total_amount > 0:
            self.payment_status = 'Paid'
        elif self.paid_amount > 0:
            self.payment_status = 'Partially Paid'
        else:
            self.payment_status = 'Pending'

    def __repr__(self):
        return f'<Invoice {self.invoice_number} Total:{self.total_amount} Status:{self.payment_status}>'

class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    tooth_number = db.Column(db.String(20), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)

    def calculate_total(self):
        self.total = round((self.quantity or 1) * (self.unit_price or 0.0), 2)
        return self.total
