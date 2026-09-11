// Global DentiFlow Application JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // =============================================
    // Mobile sidebar toggle with overlay
    // =============================================
    const toggleBtn = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.app-sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function closeSidebar() {
        if (sidebar) sidebar.classList.remove('show');
        if (overlay) overlay.classList.remove('show');
    }

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // =============================================
    // Dark Mode Toggle
    // =============================================
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        // Set initial icon based on current theme
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const icon = darkModeToggle.querySelector('i');
        if (currentTheme === 'dark' && icon) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }

        darkModeToggle.addEventListener('click', function () {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (isDark) {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('df-theme', 'light');
                if (icon) { icon.classList.remove('fa-sun'); icon.classList.add('fa-moon'); }
                DentiFlow.toast('Light mode enabled', 'info', 'Theme');
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('df-theme', 'dark');
                if (icon) { icon.classList.remove('fa-moon'); icon.classList.add('fa-sun'); }
                DentiFlow.toast('Dark mode enabled', 'info', 'Theme');
            }
        });
    }

    // Initialize Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Setup Dynamic Invoice Item Adder
    initInvoiceCalculations();
});


// =============================================
// TOAST NOTIFICATION SYSTEM
// Usage: DentiFlow.toast('Message text', 'success', 'Optional Title');
// Types: success, danger, warning, info
// =============================================
window.DentiFlow = window.DentiFlow || {};

DentiFlow.toast = function (message, type, title) {
    type = type || 'info';
    var container = document.getElementById('toast-container');
    if (!container) return;

    var iconMap = {
        success: 'fa-check-circle',
        danger:  'fa-circle-exclamation',
        warning: 'fa-triangle-exclamation',
        info:    'fa-circle-info'
    };
    var titleMap = {
        success: 'Success',
        danger:  'Error',
        warning: 'Warning',
        info:    'Info'
    };

    var toast = document.createElement('div');
    toast.className = 'df-toast toast-' + type;
    toast.innerHTML =
        '<i class="fas ' + (iconMap[type] || iconMap.info) + ' toast-icon"></i>' +
        '<div class="toast-body">' +
            '<div class="toast-title">' + (title || titleMap[type] || 'Notification') + '</div>' +
            '<div class="toast-msg">' + message + '</div>' +
        '</div>' +
        '<button class="toast-close" aria-label="Close">&times;</button>' +
        '<div class="toast-progress"></div>';

    container.appendChild(toast);

    // Close handler
    var closeBtn = toast.querySelector('.toast-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            dismissToast(toast);
        });
    }

    // Auto-dismiss after 4 seconds
    setTimeout(function () {
        dismissToast(toast);
    }, 4000);

    function dismissToast(el) {
        if (el._dismissed) return;
        el._dismissed = true;
        el.style.animation = 'toastSlideOut 0.35s forwards';
        setTimeout(function () { el.remove(); }, 400);
    }
};

// =============================================
// Convert Flask flash messages to toasts
// =============================================
document.addEventListener('DOMContentLoaded', function () {
    // After a small delay, convert existing alert boxes into toasts
    setTimeout(function () {
        var alertBoxes = document.querySelectorAll('.alert-dismissible');
        alertBoxes.forEach(function (alertEl) {
            var category = 'info';
            if (alertEl.classList.contains('alert-success')) category = 'success';
            else if (alertEl.classList.contains('alert-danger')) category = 'danger';
            else if (alertEl.classList.contains('alert-warning')) category = 'warning';

            var text = '';
            // Get the text content from the nested div
            var innerDivs = alertEl.querySelectorAll('.d-flex div');
            if (innerDivs.length > 0) {
                text = innerDivs[innerDivs.length - 1].textContent.trim();
            } else {
                text = alertEl.textContent.trim();
            }

            if (text) {
                DentiFlow.toast(text, category);
            }
        });
    }, 200);
});


// =============================================
// Dynamic Invoice Calculations
// =============================================
function initInvoiceCalculations() {
    const tableBody = document.getElementById('invoiceItemsBody');
    const addItemBtn = document.getElementById('addInvoiceItemBtn');
    
    if (!tableBody || !addItemBtn) return;

    function recalculateFormTotals() {
        let subtotal = 0;
        const rows = tableBody.querySelectorAll('tr.item-row');
        rows.forEach(function (row) {
            const qtyInput = row.querySelector('.item-qty');
            const priceInput = row.querySelector('.item-price');
            const totalCell = row.querySelector('.item-row-total');
            
            const qty = parseFloat(qtyInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            const rowTotal = Math.round(qty * price * 100) / 100;
            
            if (totalCell) totalCell.innerText = rowTotal.toFixed(2);
            subtotal += rowTotal;
        });

        const subtotalEl = document.getElementById('calcSubtotal');
        if (subtotalEl) subtotalEl.innerText = subtotal.toFixed(2);

        // Discount
        const discType = document.getElementById('discountType')?.value || 'fixed';
        const discVal = parseFloat(document.getElementById('discountValue')?.value) || 0;
        let discountAmt = 0;
        if (discType === 'percentage') {
            discountAmt = Math.round((subtotal * (discVal / 100)) * 100) / 100;
        } else {
            discountAmt = Math.min(subtotal, discVal);
        }
        const discAmtEl = document.getElementById('calcDiscountAmt');
        if (discAmtEl) discAmtEl.innerText = discountAmt.toFixed(2);

        // Tax
        const taxable = Math.max(0, subtotal - discountAmt);
        const taxRate = parseFloat(document.getElementById('taxPercent')?.value) || 0;
        const taxAmt = Math.round((taxable * (taxRate / 100)) * 100) / 100;
        const taxAmtEl = document.getElementById('calcTaxAmt');
        if (taxAmtEl) taxAmtEl.innerText = taxAmt.toFixed(2);

        // Grand Total
        const grandTotal = Math.round((taxable + taxAmt) * 100) / 100;
        const grandTotalEl = document.getElementById('calcGrandTotal');
        if (grandTotalEl) grandTotalEl.innerText = grandTotal.toFixed(2);
    }

    addItemBtn.addEventListener('click', function () {
        const row = document.createElement('tr');
        row.className = 'item-row';
        row.innerHTML = `
            <td>
                <input type="text" name="item_description[]" class="form-control form-control-sm" placeholder="Procedure / Item description" required>
            </td>
            <td>
                <input type="text" name="item_tooth[]" class="form-control form-control-sm" placeholder="e.g. 14, 15">
            </td>
            <td style="width: 90px;">
                <input type="number" name="item_quantity[]" class="form-control form-control-sm item-qty" value="1" min="1" required>
            </td>
            <td style="width: 130px;">
                <input type="number" name="item_price[]" class="form-control form-control-sm item-price" value="0.00" step="0.01" min="0" required>
            </td>
            <td style="width: 110px;" class="text-end fw-semibold item-row-total">0.00</td>
            <td style="width: 50px;" class="text-center">
                <button type="button" class="btn btn-outline-danger btn-sm remove-row-btn"><i class="fas fa-trash"></i></button>
            </td>
        `;
        tableBody.appendChild(row);
        bindRowEvents(row);
        recalculateFormTotals();
    });

    function bindRowEvents(row) {
        row.querySelectorAll('.item-qty, .item-price').forEach(input => {
            input.addEventListener('input', recalculateFormTotals);
        });
        const rmBtn = row.querySelector('.remove-row-btn');
        if (rmBtn) {
            rmBtn.addEventListener('click', function () {
                if (tableBody.querySelectorAll('tr.item-row').length > 1) {
                    row.remove();
                    recalculateFormTotals();
                } else {
                    DentiFlow.toast('An invoice must have at least one line item.', 'warning');
                }
            });
        }
    }

    // Bind existing rows
    tableBody.querySelectorAll('tr.item-row').forEach(bindRowEvents);

    // Bind discount & tax inputs
    ['discountType', 'discountValue', 'taxPercent'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', recalculateFormTotals);
    });

    recalculateFormTotals();
}

// Print trigger helper
function printCurrentPage() {
    window.print();
}
