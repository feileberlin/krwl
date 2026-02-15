/**
 * I18n Module - Internationalization for KRWL> Events
 * 
 * KISS: Simple handrolled i18n solution (~200 lines, no dependencies)
 * - URL-based language detection (e.g., /en, /de/hof)
 * - Simple JSON translation files
 * - Template string interpolation ({{variable}})
 * - Fallback to English if translation missing
 * - LocalStorage language preference
 * 
 * URL Structure:
 * - / → default language + default region
 * - /en → English + default region
 * - /de/hof → German + Hof region
 * - /hof → default language + Hof region (backward compatible)
 */

class I18n {
    constructor(config) {
        this.config = config;
        this.currentLang = null;
        this.defaultLang = 'en';  // Fallback if config not loaded
        this.supportedLangs = ['de', 'en', 'cs'];
        this.translations = {};
        this.translationsLoaded = false;
    }
    
    /**
     * Initialize i18n system
     * 1. Detect language from URL or localStorage
     * 2. Load translation file
     * 3. Set document lang attribute
     * @returns {Promise<void>}
     */
    async init() {
        // Get supported languages from config
        this.supportedLangs = this.config?.supportedLanguages || ['de', 'en', 'cs'];
        this.defaultLang = this.config?.defaultLanguage || 'en';
        
        // Detect language from URL or localStorage
        this.currentLang = this.detectLanguage();
        
        // Load translations for detected language
        await this.loadTranslations(this.currentLang);
        
        // Set document language attribute (important for accessibility)
        document.documentElement.lang = this.currentLang;
        
        this.log('I18n initialized:', {
            currentLang: this.currentLang,
            supportedLangs: this.supportedLangs,
            translationsLoaded: this.translationsLoaded
        });
    }
    
    /**
     * Detect language from URL path or localStorage
     * URL format: /{lang}/{region} or /{lang} or /{region}
     * 
     * Examples:
     * - /en → English
     * - /de/hof → German
     * - /hof → default language (backward compatible)
     * - / → default language
     * 
     * @returns {string} Language code (e.g., 'en', 'de', 'cs')
     */
    detectLanguage() {
        // Parse URL path (remove leading/trailing slashes)
        const path = window.location.pathname.replace(/^\/|\/$/g, '');
        const segments = path.split('/').filter(s => s.length > 0);
        
        // Check if first segment is a language code
        if (segments.length > 0 && this.supportedLangs.includes(segments[0])) {
            // Store language preference
            this.setLanguagePreference(segments[0]);
            return segments[0];
        }
        
        // Check localStorage for saved preference
        const storedLang = this.getLanguagePreference();
        if (storedLang && this.supportedLangs.includes(storedLang)) {
            return storedLang;
        }
        
        // Check browser language (navigator.language or navigator.userLanguage)
        const browserLang = (navigator.language || navigator.userLanguage || '').split('-')[0];
        if (this.supportedLangs.includes(browserLang)) {
            return browserLang;
        }
        
        // Fallback to default language
        return this.defaultLang;
    }
    
    /**
     * Load translation file for specified language
     * @param {string} lang - Language code
     * @returns {Promise<void>}
     */
    async loadTranslations(lang) {
        try {
            // Check if translations are embedded in window.TRANSLATIONS (from backend)
            if (window.TRANSLATIONS && window.TRANSLATIONS[lang]) {
                this.translations = window.TRANSLATIONS[lang];
                this.translationsLoaded = true;
                this.log(`Translations loaded from window.TRANSLATIONS for: ${lang}`);
                return;
            }
            
            // Fallback: Load from separate JSON file
            const response = await fetch(`/assets/json/translations/${lang}.json`);
            if (!response.ok) {
                throw new Error(`Failed to load translations: ${response.status}`);
            }
            
            this.translations = await response.json();
            this.translationsLoaded = true;
            this.log(`Translations loaded from file: ${lang}.json`);
        } catch (error) {
            console.error(`Failed to load translations for ${lang}:`, error);
            
            // Fallback to English if not already English
            if (lang !== 'en') {
                console.warn(`Falling back to English translations`);
                await this.loadTranslations('en');
            } else {
                this.translationsLoaded = false;
            }
        }
    }
    
    /**
     * Get translated string by key path
     * Supports nested keys with dot notation: "filter_bar.event_count.singular"
     * Supports template interpolation: "Hello {{name}}" with {name: "World"}
     * 
     * @param {string} key - Translation key (dot-separated path)
     * @param {Object} params - Template variables for interpolation
     * @returns {string} Translated string or key if not found
     */
    t(key, params = {}) {
        if (!this.translationsLoaded) {
            console.warn('Translations not loaded yet');
            return key;
        }
        
        // Navigate nested object using dot notation
        const keys = key.split('.');
        let value = this.translations;
        
        for (const k of keys) {
            if (value && typeof value === 'object' && k in value) {
                value = value[k];
            } else {
                console.warn(`Translation key not found: ${key}`);
                return key;  // Return key if translation not found
            }
        }
        
        // Ensure we have a string
        if (typeof value !== 'string') {
            console.warn(`Translation value is not a string: ${key}`);
            return key;
        }
        
        // Interpolate template variables
        return this.interpolate(value, params);
    }
    
    /**
     * Interpolate template variables in string
     * Replaces {{variable}} with params.variable
     * 
     * @param {string} template - Template string with {{variables}}
     * @param {Object} params - Variable values
     * @returns {string} Interpolated string
     */
    interpolate(template, params) {
        return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return params[key] !== undefined ? params[key] : match;
        });
    }
    
    /**
     * Get current language code
     * @returns {string} Current language code
     */
    getCurrentLanguage() {
        return this.currentLang;
    }
    
    /**
     * Get all supported languages
     * @returns {Array<string>} Array of language codes
     */
    getSupportedLanguages() {
        return this.supportedLangs;
    }
    
    /**
     * Get translated event field with transparency metadata
     * Used for displaying event content in the current language
     * 
     * @param {Object} event - Event object with translations
     * @param {string} field - Field name (title, description, location_name)
     * @param {string} lang - Target language code (default: current language)
     * @returns {Object} { text, isTranslated, metadata, fallback }
     */
    getTranslatedField(event, field, lang = null) {
        const targetLang = lang || this.currentLang;
        
        // If no translations object, return original
        if (!event.translations) {
            return {
                text: this._getOriginalFieldValue(event, field),
                isTranslated: false,
                metadata: null,
                fallback: false
            };
        }
        
        const sourceLang = event.translations.source_language || this.defaultLang;
        
        // If current language matches source language, return original
        if (targetLang === sourceLang) {
            return {
                text: this._getOriginalFieldValue(event, field),
                isTranslated: false,
                metadata: null,
                fallback: false
            };
        }
        
        // Check if translation exists
        const translation = event.translations.fields?.[field]?.[targetLang];
        if (translation && translation.text) {
            return {
                text: translation.text,
                isTranslated: true,
                metadata: translation,
                fallback: false
            };
        }
        
        // Fallback to original language
        return {
            text: this._getOriginalFieldValue(event, field),
            isTranslated: false,
            metadata: null,
            fallback: true
        };
    }
    
    /**
     * Get original field value from event
     * @private
     */
    _getOriginalFieldValue(event, field) {
        if (field === 'location_name') {
            return event.location?.name || '';
        }
        return event[field] || '';
    }
    
    /**
     * Create AI translation indicator HTML
     * Returns footnote symbol (†) with ARIA label and tooltip
     * 
     * @param {Object} metadata - Translation metadata
     * @returns {string} HTML for footnote indicator or empty string
     */
    createTranslationIndicator(metadata) {
        if (!metadata || metadata.method !== 'ai') {
            return '';
        }
        
        const service = metadata.service || 'AI';
        const date = metadata.generated_at ? new Date(metadata.generated_at).toLocaleDateString() : 'Unknown';
        const verified = metadata.verified ? 'Verified' : 'Not verified';
        const sourceLang = this._getLanguageName(metadata.source_language || 'unknown');
        
        const tooltip = `AI Translation\nFrom: ${sourceLang}\nService: ${service}\nDate: ${date}\nStatus: ${verified}`;
        
        return `<sup class="ai-translation-indicator" 
                     role="img"
                     aria-label="AI-translated from ${sourceLang}"
                     title="${tooltip}">†</sup>`;
    }
    
    /**
     * Get human-readable language name
     * @private
     */
    _getLanguageName(code) {
        const names = {
            'de': 'German',
            'en': 'English',
            'cs': 'Czech'
        };
        return names[code] || code.toUpperCase();
    }
    
    /**
     * Create translation disclosure footer
     * Shows "AI-translated" notice with "View Original" button
     * 
     * @param {Object} event - Event with translations
     * @returns {string} HTML for translation footer or empty string
     */
    createTranslationFooter(event) {
        if (!event.translations || !event.translations.source_language) {
            return '';
        }
        
        const sourceLang = event.translations.source_language;
        const currentLang = this.currentLang;
        
        // Don't show footer if viewing original language
        if (sourceLang === currentLang) {
            return '';
        }
        
        // Check if current view has any translations
        const hasTranslations = event.translations.fields && 
            Object.values(event.translations.fields).some(field => 
                field[currentLang] && field[currentLang].method === 'ai'
            );
        
        if (!hasTranslations) {
            return '';
        }
        
        const langNames = {
            'de': 'German',
            'en': 'English',
            'cs': 'Czech'
        };
        const sourceLangName = langNames[sourceLang] || sourceLang.toUpperCase();
        
        return `
            <div class="translation-footer">
                <i data-lucide="info" aria-hidden="true"></i>
                <span class="translation-notice">
                    AI-translated from ${sourceLangName}. 
                    <button class="view-original-btn" 
                            data-event-id="${event.id}"
                            data-source-lang="${sourceLang}"
                            onclick="window.app.i18n.switchLanguage('${sourceLang}')">
                        View original
                    </button>
                </span>
            </div>
        `.trim();
    }
    
    /**
     * Get language metadata (name, native name)
     * @param {string} lang - Language code
     * @returns {Object} Language metadata
     */
    getLanguageMetadata(lang) {
        // Try to get from loaded translations
        if (this.translations && this.translations._language) {
            return this.translations._language;
        }
        
        // Fallback metadata
        const metadata = {
            de: { code: 'de', name: 'German', native_name: 'Deutsch' },
            en: { code: 'en', name: 'English', native_name: 'English' },
            cs: { code: 'cs', name: 'Czech', native_name: 'Čeština' }
        };
        
        return metadata[lang] || { code: lang, name: lang, native_name: lang };
    }
    
    /**
     * Switch to different language
     * Updates URL and reloads page
     * 
     * @param {string} lang - Language code to switch to
     */
    switchLanguage(lang) {
        if (!this.supportedLangs.includes(lang)) {
            console.error(`Unsupported language: ${lang}`);
            return;
        }
        
        // Save preference
        this.setLanguagePreference(lang);
        
        // Build new URL with language
        const path = window.location.pathname.replace(/^\/|\/$/g, '');
        const segments = path.split('/').filter(s => s.length > 0);
        
        // Remove current language from path if present
        if (segments.length > 0 && this.supportedLangs.includes(segments[0])) {
            segments.shift();
        }
        
        // Add new language to beginning
        const newPath = `/${lang}${segments.length > 0 ? '/' + segments.join('/') : ''}`;
        
        // Navigate to new URL (full page reload)
        window.location.href = newPath;
    }
    
    /**
     * Get language preference from localStorage
     * @returns {string|null} Stored language code or null
     */
    getLanguagePreference() {
        try {
            return localStorage.getItem('krwl_language');
        } catch (e) {
            return null;
        }
    }
    
    /**
     * Save language preference to localStorage
     * @param {string} lang - Language code
     */
    setLanguagePreference(lang) {
        try {
            localStorage.setItem('krwl_language', lang);
        } catch (e) {
            console.warn('Failed to save language preference:', e);
        }
    }
    
    /**
     * Get region from URL (for multi-region support)
     * URL format: /{lang}/{region} or /{region}
     * 
     * @returns {string|null} Region code or null
     */
    getRegionFromUrl() {
        const path = window.location.pathname.replace(/^\/|\/$/g, '');
        const segments = path.split('/').filter(s => s.length > 0);
        
        // If first segment is language, second is region
        if (segments.length > 1 && this.supportedLangs.includes(segments[0])) {
            return segments[1];
        }
        
        // If first segment is not language, it's region
        if (segments.length > 0 && !this.supportedLangs.includes(segments[0])) {
            return segments[0];
        }
        
        return null;
    }
    
    /**
     * Log helper (only if debug enabled)
     */
    log(message, ...args) {
        if (this.config && this.config.debug) {
            console.log('[I18n]', message, ...args);
        }
    }
}

// Make I18n available globally
window.I18n = I18n;
