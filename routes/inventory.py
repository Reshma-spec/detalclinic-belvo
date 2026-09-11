from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from models import db, InventoryItem, ClinicSetting

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip() # 'low', 'expired'
    
    query = InventoryItem.query
    
    if search_query:
        search_like = f"%{search_query}%"
        query = query.filter(
            (InventoryItem.item_name.ilike(search_like)) |
            (InventoryItem.supplier_name.ilike(search_like))
        )
        
    if category_filter:
        query = query.filter(InventoryItem.category == category_filter)
        
    items = query.order_by(InventoryItem.item_name.asc()).all()
    
    if status_filter == 'low':
        items = [i for i in items if i.is_low_stock]
    elif status_filter == 'expired':
        items = [i for i in items if i.is_expired_or_near]
        
    categories = ['Consumables', 'Instruments', 'Materials', 'Pharmaceuticals', 'PPE', 'Equipment', 'Disposables']
    settings = ClinicSetting.get_settings()
    
    total_items = InventoryItem.query.count()
    low_stock_count = len([i for i in InventoryItem.query.all() if i.is_low_stock])
    total_val = sum(i.quantity * i.purchase_price for i in InventoryItem.query.all())
    
    return render_template(
        'inventory.html',
        items=items,
        categories=categories,
        search_query=search_query,
        category_filter=category_filter,
        status_filter=status_filter,
        total_items=total_items,
        low_stock_count=low_stock_count,
        total_val=total_val,
        today_str=date.today().strftime('%Y-%m-%d'),
        settings=settings
    )

@inventory_bp.route('/add', methods=['POST'])
@login_required
def add():
    item_name = request.form.get('item_name', '').strip()
    if not item_name:
        flash('Item name is required.', 'danger')
        return redirect(url_for('inventory.index'))
        
    try:
        qty = max(0, int(request.form.get('quantity', 0)))
        min_stock = max(0, int(request.form.get('min_stock_level', 10)))
        price = max(0.0, float(request.form.get('purchase_price', 0.0) or 0.0))
    except ValueError:
        qty = 0
        min_stock = 10
        price = 0.0
        
    item = InventoryItem(
        item_name=item_name,
        category=request.form.get('category', 'Consumables'),
        quantity=qty,
        unit=request.form.get('unit', 'Pcs').strip(),
        min_stock_level=min_stock,
        purchase_price=price,
        supplier_name=request.form.get('supplier_name', '').strip() or None,
        supplier_contact=request.form.get('supplier_contact', '').strip() or None,
        expiry_date=request.form.get('expiry_date', '').strip() or None,
        last_restocked=date.today().strftime('%Y-%m-%d'),
        notes=request.form.get('notes', '').strip() or None
    )
    db.session.add(item)
    db.session.commit()
    
    flash(f'Item "{item.item_name}" added to inventory.', 'success')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/<int:item_id>/adjust', methods=['POST'])
@login_required
def adjust_stock(item_id):
    item = db.session.get(InventoryItem, item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('inventory.index'))
        
    action = request.form.get('action') # 'in' or 'out'
    try:
        amount = int(request.form.get('amount', 0))
    except ValueError:
        amount = 0
        
    if amount <= 0:
        flash('Adjustment quantity must be positive.', 'danger')
        return redirect(url_for('inventory.index'))
        
    if action == 'in':
        item.quantity += amount
        item.last_restocked = date.today().strftime('%Y-%m-%d')
        flash(f'Restocked +{amount} {item.unit} for {item.item_name}. New Quantity: {item.quantity}', 'success')
    elif action == 'out':
        if amount > item.quantity:
            flash(f'Cannot deduct {amount} {item.unit}; current stock is only {item.quantity}.', 'danger')
            return redirect(url_for('inventory.index'))
        item.quantity -= amount
        flash(f'Deducted -{amount} {item.unit} from {item.item_name}. Remaining: {item.quantity}', 'info')
        
    db.session.commit()
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/<int:item_id>/edit', methods=['POST'])
@login_required
def edit(item_id):
    item = db.session.get(InventoryItem, item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('inventory.index'))
        
    item.item_name = request.form.get('item_name', item.item_name).strip()
    item.category = request.form.get('category', item.category)
    item.unit = request.form.get('unit', item.unit).strip()
    try:
        item.quantity = max(0, int(request.form.get('quantity', item.quantity)))
        item.min_stock_level = max(0, int(request.form.get('min_stock_level', item.min_stock_level)))
        item.purchase_price = max(0.0, float(request.form.get('purchase_price', item.purchase_price)))
    except ValueError:
        pass
        
    item.supplier_name = request.form.get('supplier_name', '').strip() or None
    item.supplier_contact = request.form.get('supplier_contact', '').strip() or None
    item.expiry_date = request.form.get('expiry_date', '').strip() or None
    item.notes = request.form.get('notes', '').strip() or None
    
    db.session.commit()
    flash(f'Item "{item.item_name}" updated.', 'success')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/<int:item_id>/delete', methods=['POST'])
@login_required
def delete(item_id):
    item = db.session.get(InventoryItem, item_id)
    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('inventory.index'))
    name = item.item_name
    db.session.delete(item)
    db.session.commit()
    flash(f'Item "{name}" deleted from inventory.', 'info')
    return redirect(url_for('inventory.index'))
