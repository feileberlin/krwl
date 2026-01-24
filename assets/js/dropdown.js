/**
 * CustomDropdown Module
 * 
 * Reusable dropdown component for filter bar interactions.
 * 
 * KISS: Single responsibility - dropdown UI component
 */

class CustomDropdown {
    // Static registry to track all dropdown instances
    static instances = [];
    
    constructor(triggerEl, items, currentValue, onSelect) {
        this.triggerEl = triggerEl;
        this.itemsProvider = typeof items === 'function' ? items : null;
        this.currentValueProvider = typeof currentValue === 'function' ? currentValue : null;
        this.items = this.itemsProvider ? this.itemsProvider() : items;
        this.currentValue = this.currentValueProvider ? this.currentValueProvider() : currentValue;
        this.onSelect = onSelect;
        this.dropdownEl = null;
        this.isOpen = false;
        
        // Register this instance
        CustomDropdown.instances.push(this);
        
        this.setupTrigger();
    }
    
    setupTrigger() {
        this.triggerEl.addEventListener('click', (e) => {
            e.stopPropagation();
            if (this.isOpen) {
                this.close();
            } else {
                // Close all other dropdowns (one-click switch)
                CustomDropdown.closeAll();
                this.open();
            }
        });
    }
    
    static closeAll() {
        // Close all dropdown instances properly
        CustomDropdown.instances.forEach(instance => {
            if (instance.isOpen) {
                instance.close();
            }
        });
    }
    
    open() {
        this.isOpen = true;
        this.triggerEl.classList.add('editing');
        this.refreshData();
        
        this.dropdownEl = this.createDropdownElement();
        this.positionDropdown();
    }
    
    createDropdownElement() {
        const dropdown = document.createElement('div');
        dropdown.className = 'filter-bar-dropdown';
        
        this.items.forEach(item => {
            const itemEl = this.createItemElement(item);
            dropdown.appendChild(itemEl);
        });
        
        document.body.appendChild(dropdown);
        return dropdown;
    }
    
    createItemElement(item) {
        const itemEl = document.createElement('div');
        itemEl.className = 'filter-bar-dropdown-item';
        
        if (item.value === this.currentValue) {
            itemEl.classList.add('selected');
        }
        
        // Handle disabled items
        if (item.disabled) {
            itemEl.classList.add('disabled');
            itemEl.style.textDecoration = 'line-through';
            itemEl.style.color = '#888';
            itemEl.style.cursor = 'not-allowed';
            itemEl.style.opacity = '0.6';
        }
        
        itemEl.textContent = item.label;
        
        // Only add click listener if not disabled
        if (!item.disabled) {
            itemEl.addEventListener('click', (e) => {
                e.stopPropagation();
                this.onSelect(item.value);
                this.currentValue = this.currentValueProvider
                    ? this.currentValueProvider()
                    : item.value;
                this.close();
            });
        }
        
        return itemEl;
    }

    refreshData() {
        if (this.itemsProvider) {
            const items = this.itemsProvider();
            if (!Array.isArray(items)) {
                console.warn('[Dropdown] Items provider did not return an array');
                if (!Array.isArray(this.items)) {
                    this.items = [];
                }
            } else {
                this.items = items;
            }
        }
        if (this.currentValueProvider) {
            this.currentValue = this.currentValueProvider();
        }
    }
    
    positionDropdown() {
        const rect = this.triggerEl.getBoundingClientRect();
        this.dropdownEl.style.left = `${rect.left}px`;
        this.dropdownEl.style.top = `${rect.bottom + 5}px`;
        
        // Adjust if off-screen
        setTimeout(() => {
            this.adjustPosition(rect);
        }, 0);
    }
    
    adjustPosition(triggerRect) {
        const dropRect = this.dropdownEl.getBoundingClientRect();
        
        // Adjust horizontal position if off-screen
        if (dropRect.right > window.innerWidth) {
            this.dropdownEl.style.left = `${window.innerWidth - dropRect.width - 10}px`;
        }
        
        // Adjust vertical position if off-screen
        if (dropRect.bottom > window.innerHeight) {
            this.dropdownEl.style.top = `${triggerRect.top - dropRect.height - 5}px`;
        }
    }
    
    close() {
        this.isOpen = false;
        this.triggerEl.classList.remove('editing');
        
        if (this.dropdownEl) {
            this.dropdownEl.remove();
            this.dropdownEl = null;
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CustomDropdown;
}
