// Interactive Adult Dental Chart (32 Teeth) Module

class DentalChartManager {
    constructor(patientId, initialData = {}) {
        this.patientId = patientId;
        this.chartData = initialData; // Map of toothNumber -> condition dict
        this.selectedTooth = null;
        this.init();
    }

    init() {
        this.renderTeethStyles();
        this.bindEvents();
    }

    renderTeethStyles() {
        const cards = document.querySelectorAll('.tooth-card');
        cards.forEach(card => {
            const toothNum = parseInt(card.dataset.toothNumber);
            const data = this.chartData[toothNum];
            if (data && data.condition) {
                this.applyConditionClass(card, data.condition);
                const badge = card.querySelector('.tooth-status-indicator');
                if (badge) badge.innerText = data.condition;
            }
        });
    }

    applyConditionClass(element, condition) {
        element.classList.remove(
            'tooth-healthy', 'tooth-caries', 'tooth-filled', 
            'tooth-missing', 'tooth-crown', 'tooth-root-canal', 
            'tooth-extraction-required', 'tooth-implant', 'tooth-other'
        );
        const slug = condition.toLowerCase().replace(/\s+/g, '-');
        element.classList.add(`tooth-${slug}`);
    }

    bindEvents() {
        const cards = document.querySelectorAll('.tooth-card');
        cards.forEach(card => {
            card.addEventListener('click', (e) => {
                cards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
                const toothNum = parseInt(card.dataset.toothNumber);
                this.selectTooth(toothNum, card.dataset.fdiNumber, card.dataset.toothName);
            });
        });

        // Modal / Form state sync
        const updateBtn = document.getElementById('saveToothQuickBtn');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => this.saveSelectedTooth());
        }
    }

    selectTooth(toothNumber, fdiNumber, toothName) {
        this.selectedTooth = toothNumber;
        const data = this.chartData[toothNumber] || {
            tooth_number: toothNumber,
            condition: 'Healthy',
            surface: 'Whole',
            notes: ''
        };

        const targetHeader = document.getElementById('selectedToothTitle');
        if (targetHeader) {
            targetHeader.innerText = `Tooth #${toothNumber} (FDI: ${fdiNumber || ''}) - ${toothName || 'Adult Tooth'}`;
        }

        const toothInput = document.getElementById('chartModalToothNum');
        if (toothInput) toothInput.value = toothNumber;

        const condSelect = document.getElementById('chartModalCondition');
        if (condSelect) condSelect.value = data.condition || 'Healthy';

        const surfSelect = document.getElementById('chartModalSurface');
        if (surfSelect) surfSelect.value = data.surface || 'Whole';

        const notesInput = document.getElementById('chartModalNotes');
        if (notesInput) notesInput.value = data.notes || '';

        // Show editor pane or trigger modal
        const editorPane = document.getElementById('toothEditorPane');
        if (editorPane) {
            editorPane.style.display = 'block';
            editorPane.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    async saveSelectedTooth() {
        if (!this.selectedTooth) return;

        const condition = document.getElementById('chartModalCondition').value;
        const surface = document.getElementById('chartModalSurface').value;
        const notes = document.getElementById('chartModalNotes').value;

        const payload = {
            tooth_number: this.selectedTooth,
            condition: condition,
            surface: surface,
            notes: notes
        };

        try {
            const resp = await fetch(`/chart/api/${this.patientId}/update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            const result = await resp.json();
            if (result.success) {
                this.chartData[this.selectedTooth] = result.tooth;
                this.renderTeethStyles();
                
                // Show brief success alert
                const alertBox = document.getElementById('chartSaveAlert');
                if (alertBox) {
                    alertBox.style.display = 'block';
                    setTimeout(() => { alertBox.style.display = 'none'; }, 3000);
                }
            } else {
                alert('Error saving tooth condition: ' + (result.error || 'Unknown error'));
            }
        } catch (err) {
            console.error('Save error:', err);
            // Fallback to submitting standard form if API is unavailable
            const fallbackForm = document.getElementById('toothFallbackForm');
            if (fallbackForm) fallbackForm.submit();
        }
    }
}
