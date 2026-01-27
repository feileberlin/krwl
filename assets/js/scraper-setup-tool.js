/**
 * Scraper Setup Tool - Visual Drag'n'Drop Configuration
 * 
 * This module provides a visual interface for configuring event scrapers.
 * Users drag DATA SNIPPETS from a webpage preview and drop them onto 
 * schema fields to create the mapping that connects the scraper.
 * 
 * Workflow:
 * 1. User enters a URL to analyze
 * 2. Tool fetches and displays data snippets from the page
 * 3. User drags snippets to schema field drop zones
 * 4. Tool captures the CSS selector for each mapping
 * 5. Configuration is exported for GitHub CI integration
 * 
 * Features:
 * - Visual drag-and-drop data snippet mapping
 * - Live preview of extracted data values
 * - Automatic CSS selector detection
 * - CI configuration export for GitHub Actions
 */

class ScraperSetupTool {
    constructor(config) {
        this.config = config || window.APP_CONFIG || {};
        
        // Schema fields for event mapping (the data scheme)
        this.schemaFields = {
            title: {
                type: 'text',
                required: true,
                description: 'Event title/name',
                icon: 'heading',
                example: 'Summer Music Festival'
            },
            description: {
                type: 'text',
                required: false,
                description: 'Event description',
                icon: 'file-text',
                example: 'Join us for a day of live music...'
            },
            location_name: {
                type: 'text',
                required: true,
                description: 'Venue/location name',
                icon: 'map-pin',
                example: 'City Park Amphitheater'
            },
            location_address: {
                type: 'text',
                required: false,
                description: 'Full address',
                icon: 'home',
                example: 'Main Street 123, 95028 Hof'
            },
            start_date: {
                type: 'datetime',
                required: true,
                description: 'Start date/time',
                icon: 'calendar',
                example: '15.06.2025 19:00'
            },
            end_date: {
                type: 'datetime',
                required: false,
                description: 'End date/time',
                icon: 'calendar-check',
                example: '15.06.2025 23:00'
            },
            url: {
                type: 'link',
                required: false,
                description: 'Event detail URL',
                icon: 'link',
                example: 'https://example.com/event/123'
            },
            image: {
                type: 'image',
                required: false,
                description: 'Event image/poster',
                icon: 'image',
                example: 'event-poster.jpg'
            },
            category: {
                type: 'text',
                required: false,
                description: 'Event category',
                icon: 'tag',
                example: 'Music, Concert'
            },
            price: {
                type: 'text',
                required: false,
                description: 'Price information',
                icon: 'credit-card',
                example: '15€ / Free entry'
            }
        };
        
        // Current state
        this.currentUrl = null;
        this.analysis = null;
        this.fieldMappings = {};
        this.selectedContainer = null;
        
        // DOM elements (will be set during init)
        this.elements = {};
        
        this.init();
    }
    
    init() {
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupUI());
        } else {
            this.setupUI();
        }
    }
    
    setupUI() {
        // Find the scraper setup container
        const container = document.getElementById('scraper-setup-tool');
        if (!container) {
            // Tool not present in current page
            return;
        }
        
        this.elements.container = container;
        this.elements.urlInput = container.querySelector('#scraper-url-input');
        this.elements.analyzeBtn = container.querySelector('#scraper-analyze-btn');
        this.elements.resultsPanel = container.querySelector('#scraper-results');
        this.elements.fieldsPanel = container.querySelector('#scraper-fields');
        this.elements.previewPanel = container.querySelector('#scraper-preview');
        this.elements.exportBtn = container.querySelector('#scraper-export-btn');
        this.elements.statusEl = container.querySelector('#scraper-status');
        
        // Bind events
        if (this.elements.analyzeBtn) {
            this.elements.analyzeBtn.addEventListener('click', () => this.analyzeUrl());
        }
        
        if (this.elements.urlInput) {
            this.elements.urlInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.analyzeUrl();
                }
            });
            
            // Enable drag-and-drop URL input
            this.elements.urlInput.addEventListener('dragover', (e) => {
                e.preventDefault();
                this.elements.urlInput.classList.add('drag-over');
            });
            
            this.elements.urlInput.addEventListener('dragleave', () => {
                this.elements.urlInput.classList.remove('drag-over');
            });
            
            this.elements.urlInput.addEventListener('drop', (e) => {
                e.preventDefault();
                this.elements.urlInput.classList.remove('drag-over');
                
                // Extract URL from dropped content
                const text = e.dataTransfer.getData('text/plain') || 
                            e.dataTransfer.getData('text/uri-list');
                if (text && this.isValidUrl(text.trim())) {
                    this.elements.urlInput.value = text.trim();
                    this.analyzeUrl();
                }
            });
        }
        
        if (this.elements.exportBtn) {
            this.elements.exportBtn.addEventListener('click', () => this.exportConfig());
        }
        
        // Set up field drop zones
        this.setupFieldDropZones();
    }
    
    setupFieldDropZones() {
        if (!this.elements.fieldsPanel) return;
        
        // Create field mapping UI - THE DATA SCHEME
        let fieldsHtml = `
            <div class="fields-panel-header">
                <h4><i data-lucide="database"></i> Event Data Scheme</h4>
                <p class="fields-hint">Drop data snippets here to connect the scraper</p>
            </div>
            <div class="scraper-fields-list">
        `;
        
        for (const [fieldName, fieldInfo] of Object.entries(this.schemaFields)) {
            const requiredBadge = fieldInfo.required ? 
                '<span class="field-required">Required</span>' : '';
            
            fieldsHtml += `
                <div class="scraper-field-item" 
                     data-field="${fieldName}">
                    <div class="field-header">
                        <i data-lucide="${fieldInfo.icon}" class="field-icon"></i>
                        <span class="field-name">${fieldName}</span>
                        ${requiredBadge}
                    </div>
                    <div class="field-description">${fieldInfo.description}</div>
                    <div class="field-example">Example: <em>${fieldInfo.example}</em></div>
                    <div class="field-drop-zone" 
                         data-field="${fieldName}"
                         tabindex="0"
                         role="button"
                         aria-label="Drop zone for ${fieldName}">
                        <span class="drop-hint">Drag data snippet here</span>
                        <input type="text" 
                               class="selector-input" 
                               placeholder="Or enter CSS selector"
                               data-field="${fieldName}">
                    </div>
                    <div class="field-preview" data-field="${fieldName}"></div>
                </div>
            `;
        }
        
        fieldsHtml += '</div>';
        this.elements.fieldsPanel.innerHTML = fieldsHtml;
        
        // Initialize Lucide icons if available
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Add event listeners to drop zones
        const dropZones = this.elements.fieldsPanel.querySelectorAll('.field-drop-zone');
        dropZones.forEach(zone => {
            zone.addEventListener('dragover', (e) => this.handleDragOver(e));
            zone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            zone.addEventListener('drop', (e) => this.handleDrop(e));
        });
        
        // Add event listeners to selector inputs
        const selectorInputs = this.elements.fieldsPanel.querySelectorAll('.selector-input');
        selectorInputs.forEach(input => {
            input.addEventListener('input', (e) => this.handleSelectorInput(e));
            input.addEventListener('blur', (e) => this.validateSelector(e));
        });
    }
    
    isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }
    
    async analyzeUrl() {
        const url = this.elements.urlInput?.value?.trim();
        
        if (!url) {
            this.showStatus('error', 'Please enter a URL to analyze');
            return;
        }
        
        if (!this.isValidUrl(url)) {
            this.showStatus('error', 'Please enter a valid URL (e.g., https://example.com/events)');
            return;
        }
        
        this.currentUrl = url;
        this.showStatus('loading', 'Analyzing URL structure...');
        
        try {
            // In a production environment, this would call a backend API
            // For now, we'll use a simulated analysis or fetch directly
            const analysis = await this.performAnalysis(url);
            
            if (analysis.success) {
                this.analysis = analysis;
                this.showStatus('success', `Analysis complete! Found ${analysis.detected_containers?.length || 0} potential event containers.`);
                this.displayResults(analysis);
            } else {
                this.showStatus('error', analysis.error || 'Analysis failed');
            }
        } catch (error) {
            console.error('URL analysis error:', error);
            this.showStatus('error', `Analysis failed: ${error.message}`);
        }
    }
    
    async performAnalysis(url) {
        // Try to use a proxy or backend API for analysis
        // For static sites without a backend, provide guidance
        
        // Check if we have a backend endpoint
        const apiEndpoint = this.config?.scraper_setup?.api_endpoint;
        
        if (apiEndpoint) {
            try {
                const response = await fetch(apiEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: url })
                });
                
                if (response.ok) {
                    return await response.json();
                }
            } catch (e) {
                console.warn('Backend API not available:', e);
            }
        }
        
        // Return a helpful message for static deployment
        return {
            success: true,
            url: url,
            message: 'Direct URL analysis requires a backend service.',
            guidance: [
                '1. Run the Python analysis tool locally:',
                '   python3 src/modules/scraper_setup_api.py --analyze ' + url,
                '',
                '2. Or use the CLI tool:',
                '   python3 src/modules/scraper_setup_tool.py --url ' + url,
                '',
                '3. You can also manually enter CSS selectors below.'
            ],
            detected_containers: [],
            suggestions: this.getDefaultSuggestions()
        };
    }
    
    getDefaultSuggestions() {
        // Return common selector suggestions
        const suggestions = {};
        
        for (const [fieldName, fieldInfo] of Object.entries(this.schemaFields)) {
            suggestions[fieldName] = [
                { selector: this.getDefaultSelector(fieldName), sample_value: '' }
            ];
        }
        
        return suggestions;
    }
    
    getDefaultSelector(fieldName) {
        const defaults = {
            title: '.event-title, h2, h3',
            description: '.event-description, p',
            location_name: '.location, .venue',
            location_address: '.address',
            start_date: '.date, time',
            end_date: '.end-date',
            url: 'a[href*="event"]',
            image: 'img',
            category: '.category, .type',
            price: '.price'
        };
        
        return defaults[fieldName] || '';
    }
    
    displayResults(analysis) {
        if (!this.elements.resultsPanel) return;
        
        let html = '<div class="analysis-results">';
        
        // Show guidance if available
        if (analysis.guidance) {
            html += `
                <div class="analysis-guidance">
                    <h4><i data-lucide="info"></i> Setup Instructions</h4>
                    <pre>${analysis.guidance.join('\n')}</pre>
                </div>
            `;
        }
        
        // Show draggable DATA SNIPPETS section
        html += `
            <div class="data-snippets-section">
                <h4><i data-lucide="grip-vertical"></i> Data Snippets</h4>
                <p class="snippets-instructions">
                    <strong>Drag data snippets below to the schema fields on the right.</strong>
                    Each snippet represents data that can be extracted from the page.
                </p>
                <div class="data-snippets-container" id="data-snippets-container">
        `;
        
        // Generate draggable data snippets from analysis
        if (analysis.sample_elements && analysis.sample_elements.length > 0) {
            for (const sample of analysis.sample_elements) {
                for (const [fieldName, fieldData] of Object.entries(sample.fields || {})) {
                    if (fieldData.value) {
                        html += this.createDraggableSnippet(fieldName, fieldData.selector, fieldData.value);
                    }
                }
            }
        } else if (analysis.suggestions) {
            // Create snippets from suggestions
            for (const [fieldName, suggestions] of Object.entries(analysis.suggestions)) {
                if (suggestions && suggestions.length > 0) {
                    for (const suggestion of suggestions.slice(0, 2)) {
                        const displayValue = suggestion.sample_value || `[${fieldName} data]`;
                        html += this.createDraggableSnippet(fieldName, suggestion.selector, displayValue);
                    }
                }
            }
        }
        
        html += `
                </div>
            </div>
        `;
        
        // Show detected containers (collapsible)
        if (analysis.detected_containers?.length > 0) {
            html += `
                <details class="analysis-containers">
                    <summary><i data-lucide="box"></i> Event Containers (${analysis.detected_containers.length} found)</summary>
                    <ul class="container-list">
            `;
            
            for (const container of analysis.detected_containers) {
                const confidence = Math.round(container.confidence * 100);
                html += `
                    <li class="container-item" 
                        data-selector="${container.selector}"
                        role="button"
                        tabindex="0">
                        <code>${container.selector}</code>
                        <span class="container-count">${container.count} found</span>
                        <span class="container-confidence" 
                              style="background: hsl(${confidence}, 70%, 50%)">
                            ${confidence}%
                        </span>
                    </li>
                `;
            }
            
            html += '</ul></details>';
        }
        
        html += '</div>';
        this.elements.resultsPanel.innerHTML = html;
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Set up drag events on snippets
        this.setupSnippetDragEvents();
        this.setupContainerListeners();
    }
    
    /**
     * Create a draggable data snippet element
     */
    createDraggableSnippet(fieldName, selector, value) {
        const truncatedValue = value.length > 80 ? value.substring(0, 77) + '...' : value;
        const fieldInfo = this.schemaFields[fieldName] || {};
        const icon = fieldInfo.icon || 'file';
        
        return `
            <div class="data-snippet" 
                 draggable="true"
                 data-field="${fieldName}"
                 data-selector="${this.escapeHtml(selector)}"
                 data-value="${this.escapeHtml(value)}"
                 title="Drag to ${fieldName} field">
                <div class="snippet-header">
                    <i data-lucide="${icon}" class="snippet-icon"></i>
                    <span class="snippet-field-hint">${fieldName}</span>
                </div>
                <div class="snippet-value">${this.escapeHtml(truncatedValue)}</div>
                <div class="snippet-selector"><code>${this.escapeHtml(selector)}</code></div>
                <div class="snippet-drag-hint">
                    <i data-lucide="move"></i> Drag to schema field
                </div>
            </div>
        `;
    }
    
    setupSnippetDragEvents() {
        const snippets = this.elements.resultsPanel.querySelectorAll('.data-snippet');
        
        snippets.forEach(snippet => {
            snippet.addEventListener('dragstart', (e) => {
                const fieldName = snippet.dataset.field;
                const selector = snippet.dataset.selector;
                const value = snippet.dataset.value;
                
                // Store all data for the drop
                e.dataTransfer.setData('text/plain', selector);
                e.dataTransfer.setData('application/x-field', fieldName);
                e.dataTransfer.setData('application/x-value', value);
                e.dataTransfer.effectAllowed = 'copy';
                
                snippet.classList.add('dragging');
                
                // Highlight matching drop zone
                const matchingZone = this.elements.fieldsPanel?.querySelector(
                    `.field-drop-zone[data-field="${fieldName}"]`
                );
                if (matchingZone) {
                    matchingZone.classList.add('drop-target-hint');
                }
            });
            
            snippet.addEventListener('dragend', () => {
                snippet.classList.remove('dragging');
                
                // Remove all hints
                const zones = this.elements.fieldsPanel?.querySelectorAll('.field-drop-zone');
                zones?.forEach(zone => zone.classList.remove('drop-target-hint'));
            });
        });
    }
    
    setupContainerListeners() {
        const containerItems = this.elements.resultsPanel.querySelectorAll('.container-item');
        
        containerItems.forEach(item => {
            item.addEventListener('click', () => {
                const selector = item.dataset.selector;
                this.selectContainer(selector);
                
                // Visual feedback
                containerItems.forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');
            });
            
            item.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    item.click();
                }
            });
        });
    }
    
    selectContainer(selector) {
        this.selectedContainer = selector;
        this.showStatus('info', `Selected container: ${selector}`);
    }
    
    applySelector(fieldName, selector, value = '') {
        // Update the field mapping
        this.fieldMappings[fieldName] = {
            selector: selector,
            extraction_method: this.getExtractionMethod(fieldName),
            sample_value: value
        };
        
        // Update the UI - show dropped value in drop zone
        const dropZone = this.elements.fieldsPanel.querySelector(
            `.field-drop-zone[data-field="${fieldName}"]`
        );
        const previewEl = this.elements.fieldsPanel.querySelector(
            `.field-preview[data-field="${fieldName}"]`
        );
        
        if (dropZone) {
            dropZone.classList.add('has-selector');
            
            // Replace content with dropped value display
            const displayValue = value ? 
                (value.length > 50 ? value.substring(0, 47) + '...' : value) : 
                selector;
            
            dropZone.innerHTML = `
                <div class="dropped-value">
                    <span class="value-text" title="${this.escapeHtml(value || selector)}">${this.escapeHtml(displayValue)}</span>
                    <button class="clear-btn" 
                            data-field="${fieldName}" 
                            title="Remove mapping"
                            aria-label="Remove ${fieldName} mapping">
                        <i data-lucide="x" style="width:14px;height:14px"></i>
                    </button>
                </div>
                <input type="hidden" 
                       class="selector-input" 
                       data-field="${fieldName}"
                       value="${this.escapeHtml(selector)}">
            `;
            
            // Add clear button listener
            const clearBtn = dropZone.querySelector('.clear-btn');
            if (clearBtn) {
                clearBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.clearFieldMapping(fieldName);
                });
            }
            
            // Initialize Lucide icon
            if (typeof lucide !== 'undefined') {
                lucide.createIcons();
            }
        }
        
        if (previewEl) {
            previewEl.innerHTML = `<code>${this.escapeHtml(selector)}</code> ✓`;
            previewEl.classList.add('has-value');
        }
        
        // Mark the snippet as used
        const usedSnippet = this.elements.resultsPanel?.querySelector(
            `.data-snippet[data-selector="${selector}"]`
        );
        if (usedSnippet) {
            usedSnippet.classList.add('used');
        }
        
        // Update preview panel
        this.updatePreview();
    }
    
    clearFieldMapping(fieldName) {
        // Remove from mappings
        delete this.fieldMappings[fieldName];
        
        // Reset drop zone UI
        const dropZone = this.elements.fieldsPanel.querySelector(
            `.field-drop-zone[data-field="${fieldName}"]`
        );
        const previewEl = this.elements.fieldsPanel.querySelector(
            `.field-preview[data-field="${fieldName}"]`
        );
        
        if (dropZone) {
            dropZone.classList.remove('has-selector');
            dropZone.innerHTML = `
                <span class="drop-hint">Drag data snippet here</span>
                <input type="text" 
                       class="selector-input" 
                       placeholder="Or enter CSS selector"
                       data-field="${fieldName}">
            `;
            
            // Re-add input listener
            const input = dropZone.querySelector('.selector-input');
            if (input) {
                input.addEventListener('input', (e) => this.handleSelectorInput(e));
                input.addEventListener('blur', (e) => this.validateSelector(e));
            }
        }
        
        if (previewEl) {
            previewEl.innerHTML = '';
            previewEl.classList.remove('has-value');
        }
        
        // Update preview panel
        this.updatePreview();
    }
    
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getExtractionMethod(fieldName) {
        const fieldInfo = this.schemaFields[fieldName];
        
        switch (fieldInfo?.type) {
            case 'link':
                return 'href';
            case 'image':
                return 'src';
            case 'datetime':
                return 'datetime';
            default:
                return 'text';
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
        e.currentTarget.classList.add('drag-over');
        
        // Add fallback class for older browsers that don't support :has()
        const fieldItem = e.currentTarget.closest('.scraper-field-item');
        if (fieldItem) fieldItem.classList.add('drag-active');
    }
    
    handleDragLeave(e) {
        e.currentTarget.classList.remove('drag-over');
        
        // Remove fallback class
        const fieldItem = e.currentTarget.closest('.scraper-field-item');
        if (fieldItem) fieldItem.classList.remove('drag-active');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-over');
        
        // Remove fallback class
        const fieldItem = e.currentTarget.closest('.scraper-field-item');
        if (fieldItem) fieldItem.classList.remove('drag-active');
        
        const fieldName = e.currentTarget.dataset.field;
        const selector = e.dataTransfer.getData('text/plain');
        const value = e.dataTransfer.getData('application/x-value') || '';
        
        if (selector) {
            this.applySelector(fieldName, selector, value);
            
            // Show success feedback
            this.showStatus('success', `Mapped "${selector}" to ${fieldName}`);
        }
    }
    
    handleSelectorInput(e) {
        const fieldName = e.target.dataset.field;
        const selector = e.target.value.trim();
        
        if (selector) {
            // Debounce the update
            clearTimeout(this._selectorInputTimeout);
            this._selectorInputTimeout = setTimeout(() => {
                this.applySelector(fieldName, selector);
            }, 500);
        }
    }
    
    validateSelector(e) {
        const fieldName = e.target.dataset.field;
        const selector = e.target.value.trim();
        
        if (selector) {
            try {
                // Test if selector is valid CSS syntax
                // Use a test element to avoid false positives on complex selectors
                const testDiv = document.createElement('div');
                testDiv.innerHTML = '<div class="test"></div>';
                testDiv.querySelector(selector);
                e.target.classList.remove('invalid');
            } catch (err) {
                // Check if it's a SyntaxError (invalid selector) vs other errors
                if (err instanceof DOMException || err instanceof SyntaxError) {
                    e.target.classList.add('invalid');
                } else {
                    // Other errors - assume selector is valid but couldn't be tested
                    e.target.classList.remove('invalid');
                }
            }
        } else {
            e.target.classList.remove('invalid');
        }
    }
    
    updatePreview() {
        if (!this.elements.previewPanel) return;
        
        const mappedFields = Object.entries(this.fieldMappings).filter(([_, v]) => v.selector);
        
        if (mappedFields.length === 0) {
            this.elements.previewPanel.innerHTML = `
                <p class="preview-empty">No fields mapped yet. 
                   Drag suggestions to field drop zones or enter selectors manually.</p>
            `;
            return;
        }
        
        let html = `
            <h4><i data-lucide="eye"></i> Configuration Preview</h4>
            <div class="preview-summary">
                <span class="mapped-count">${mappedFields.length}/${Object.keys(this.schemaFields).length} fields mapped</span>
            </div>
            <table class="preview-table">
                <thead>
                    <tr>
                        <th>Field</th>
                        <th>Selector</th>
                        <th>Extraction</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        for (const [fieldName, mapping] of mappedFields) {
            const fieldInfo = this.schemaFields[fieldName];
            const requiredClass = fieldInfo?.required ? 'required' : '';
            
            html += `
                <tr class="${requiredClass}">
                    <td><strong>${fieldName}</strong></td>
                    <td><code>${mapping.selector}</code></td>
                    <td>${mapping.extraction_method}</td>
                </tr>
            `;
        }
        
        html += '</tbody></table>';
        
        // Check for missing required fields
        const missingRequired = [];
        for (const [fieldName, fieldInfo] of Object.entries(this.schemaFields)) {
            if (fieldInfo.required && !this.fieldMappings[fieldName]?.selector) {
                missingRequired.push(fieldName);
            }
        }
        
        if (missingRequired.length > 0) {
            html += `
                <div class="preview-warning">
                    <i data-lucide="alert-triangle"></i>
                    Missing required fields: ${missingRequired.join(', ')}
                </div>
            `;
        }
        
        this.elements.previewPanel.innerHTML = html;
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
        
        // Enable export button if we have required fields
        if (this.elements.exportBtn) {
            this.elements.exportBtn.disabled = missingRequired.length > 0;
        }
    }
    
    async exportConfig() {
        // Validate required fields
        const missingRequired = [];
        for (const [fieldName, fieldInfo] of Object.entries(this.schemaFields)) {
            if (fieldInfo.required && !this.fieldMappings[fieldName]?.selector) {
                missingRequired.push(fieldName);
            }
        }
        
        if (missingRequired.length > 0) {
            this.showStatus('error', `Please map required fields: ${missingRequired.join(', ')}`);
            return;
        }
        
        // Generate source name from URL
        let sourceName = 'custom_source';
        if (this.currentUrl) {
            try {
                const urlObj = new URL(this.currentUrl);
                sourceName = urlObj.hostname.replace(/\./g, '_').replace(/^www_/, '');
            } catch (_) {
                // Use default name
            }
        }
        
        // Generate CI configuration
        const config = {
            version: '2.0',
            source: {
                name: sourceName,
                url: this.currentUrl || '',
                type: 'html',
                enabled: true
            },
            container: {
                selector: this.selectedContainer || '.event'
            },
            field_mappings: {},
            metadata: {
                created_at: new Date().toISOString(),
                created_by: 'scraper-setup-tool-web',
                version: '1.0'
            }
        };
        
        for (const [fieldName, mapping] of Object.entries(this.fieldMappings)) {
            if (mapping.selector) {
                config.field_mappings[fieldName] = {
                    selector: mapping.selector,
                    extraction: mapping.extraction_method,
                    required: this.schemaFields[fieldName]?.required || false
                };
            }
        }
        
        // Create downloadable file
        const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
        const downloadUrl = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${sourceName}_ci_config.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(downloadUrl);
        
        this.showStatus('success', `Configuration exported as ${sourceName}_ci_config.json`);
        
        // Show next steps
        this.showExportInstructions(sourceName, config);
    }
    
    showExportInstructions(sourceName, config) {
        if (!this.elements.previewPanel) return;
        
        const instructions = `
            <div class="export-instructions">
                <h4><i data-lucide="check-circle"></i> Configuration Exported!</h4>
                
                <div class="instruction-step">
                    <span class="step-number">1</span>
                    <div class="step-content">
                        <strong>Save the configuration file</strong>
                        <p>Add the downloaded file to your repository:</p>
                        <code>config/scraper_mappings/${sourceName}_ci_config.json</code>
                    </div>
                </div>
                
                <div class="instruction-step">
                    <span class="step-number">2</span>
                    <div class="step-content">
                        <strong>Add source to config.json</strong>
                        <p>Add this source to your scraping configuration:</p>
                        <pre>{
  "name": "${sourceName}",
  "url": "${config.source.url}",
  "type": "html",
  "mapping_file": "config/scraper_mappings/${sourceName}_ci_config.json",
  "enabled": true
}</pre>
                    </div>
                </div>
                
                <div class="instruction-step">
                    <span class="step-number">3</span>
                    <div class="step-content">
                        <strong>Commit and push</strong>
                        <p>The GitHub Actions workflow will automatically use your new scraper configuration!</p>
                    </div>
                </div>
                
                <div class="instruction-links">
                    <a href="https://github.com/feileberlin/krwl-hof/actions/workflows/manual-scrape.yml" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       class="instruction-link">
                        <i data-lucide="play"></i> Trigger Manual Scrape
                    </a>
                    <a href="https://github.com/feileberlin/krwl-hof/blob/main/config.json" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       class="instruction-link">
                        <i data-lucide="settings"></i> View config.json
                    </a>
                </div>
            </div>
        `;
        
        this.elements.previewPanel.innerHTML = instructions;
        
        // Initialize Lucide icons
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }
    
    showStatus(type, message) {
        if (!this.elements.statusEl) return;
        
        this.elements.statusEl.className = `scraper-status scraper-status--${type}`;
        this.elements.statusEl.textContent = message;
        this.elements.statusEl.style.display = 'block';
        
        // Auto-hide after delay (except for errors)
        if (type !== 'error') {
            setTimeout(() => {
                this.elements.statusEl.style.display = 'none';
            }, 5000);
        }
    }
    
    // Reset the tool
    reset() {
        this.currentUrl = null;
        this.analysis = null;
        this.fieldMappings = {};
        this.selectedContainer = null;
        
        if (this.elements.urlInput) {
            this.elements.urlInput.value = '';
        }
        
        if (this.elements.resultsPanel) {
            this.elements.resultsPanel.innerHTML = '';
        }
        
        this.setupFieldDropZones();
        this.updatePreview();
    }
}

// Export for use in app.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ScraperSetupTool;
}

// Auto-initialize if container exists
if (typeof window !== 'undefined') {
    window.ScraperSetupTool = ScraperSetupTool;
}
