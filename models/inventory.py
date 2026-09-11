from datetime import datetime
from models import db

class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), default='Consumables')
    quantity = db.Column(db.Integer, default=0, nullable=False)
    unit = db.Column(db.String(30), default='Pcs')
    min_stock_level = db.Column(db.Integer, default=10)
    purchase_price = db.Column(db.Float, default=0.0)
    supplier_name = db.Column(db.String(150), nullable=True)
    supplier_contact = db.Column(db.String(100), nullable=True)
    expiry_date = db.Column(db.String(10), nullable=True)
    last_restocked = db.Column(db.String(10), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def min_quantity(self):
        return self.min_stock_level

    @min_quantity.setter
    def min_quantity(self, value):
        self.min_stock_level = value

    @property
    def unit_cost(self):
        return self.purchase_price

    @unit_cost.setter
    def unit_cost(self, value):
        self.purchase_price = value

    @property
    def supplier(self):
        return self.supplier_name

    @supplier.setter
    def supplier(self, value):
        self.supplier_name = value

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_stock_level

    @property
    def is_expired_or_near(self):
        if not self.expiry_date:
            return False
        try:
            exp = datetime.strptime(self.expiry_date, '%Y-%m-%d').date()
            today = datetime.utcnow().date()
            return (exp - today).days <= 30
        except Exception:
            return False

    def __repr__(self):
        return f'<InventoryItem {self.item_name} Qty:{self.quantity} {self.unit}>'
