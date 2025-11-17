// SysManage Documentation Site - Internationalization System

class I18n {
    constructor() {
        this.languages = {
            'en': { name: 'English', rtl: false },
            'es': { name: 'Español', rtl: false },
            'fr': { name: 'Français', rtl: false },
            'de': { name: 'Deutsch', rtl: false },
            'it': { name: 'Italiano', rtl: false },
            'pt': { name: 'Português', rtl: false },
            'nl': { name: 'Nederlands', rtl: false },
            'ja': { name: '日本語', rtl: false },
            'zh_CN': { name: '简体中文', rtl: false },
            'zh_TW': { name: '繁體中文', rtl: false },
            'ko': { name: '한국어', rtl: false },
            'ru': { name: 'Русский', rtl: false },
            'ar': { name: 'العربية', rtl: true },
            'hi': { name: 'हिन्दी', rtl: false }
        };

        this.currentLanguage = this.detectLanguage();
        this.translations = {};
        this.loadedLanguages = new Set();
        // Don't call init() in constructor - it will be called after DOM is ready
    }

    detectLanguage() {
        // Check localStorage first
        const saved = localStorage.getItem('sysmanage-docs-language');
        if (saved && this.languages[saved]) {
            return saved;
        }

        // Check browser language
        const browserLang = navigator.language || navigator.userLanguage;
        const langCode = browserLang.toLowerCase();

        // Direct match
        if (this.languages[langCode]) {
            return langCode;
        }

        // Handle variants (e.g., en-US -> en)
        const primaryLang = langCode.split('-')[0];
        if (this.languages[primaryLang]) {
            return primaryLang;
        }

        // Handle Chinese variants
        if (langCode.includes('zh')) {
            if (langCode.includes('tw') || langCode.includes('hk') || langCode.includes('mo')) {
                return 'zh_TW';
            }
            return 'zh_CN';
        }

        // Default to English
        return 'en';
    }

    async init() {
        await this.loadLanguage(this.currentLanguage);
        this.createLanguageSwitcher();
        this.applyLanguage();
        this.updateDirection();
    }

    async loadLanguage(langCode) {
        if (this.loadedLanguages.has(langCode)) {
            return;
        }

        try {
            // Determine the correct path based on current location
            let basePath = '';
            const path = window.location.pathname;

            // Count directory depth from root
            if (path.includes('/docs/')) {
                // If we're in a subdirectory of docs (like /docs/architecture/), need to go back more
                const pathParts = path.split('/');
                const docsIndex = pathParts.indexOf('docs');
                if (docsIndex >= 0) {
                    const depthFromDocs = pathParts.length - docsIndex - 2; // -2 for 'docs' and filename
                    basePath = '../'.repeat(depthFromDocs + 1); // +1 to get out of docs directory
                }
            }

            const response = await fetch(`${basePath}assets/locales/${langCode}.json`);
            if (response.ok) {
                const translations = await response.json();
                this.translations[langCode] = translations;
                this.loadedLanguages.add(langCode);
            } else {
                console.warn(`Failed to load translations for ${langCode}`);
                // Fallback to English if not already loaded
                if (langCode !== 'en' && !this.loadedLanguages.has('en')) {
                    await this.loadLanguage('en');
                }
            }
        } catch (error) {
            console.error(`Error loading language ${langCode}:`, error);
        }
    }

    createLanguageSwitcher() {
        const headers = document.querySelectorAll('.site-header .nav-menu');

        headers.forEach(header => {
            // Remove existing language switcher
            const existing = header.querySelector('.language-switcher');
            if (existing) {
                existing.remove();
            }

            const switcher = document.createElement('div');
            switcher.className = 'language-switcher';

            const currentLang = this.languages[this.currentLanguage];
            const button = document.createElement('button');
            button.className = 'language-button';
            button.innerHTML = `<span class="language-icon">🌐</span><span>${currentLang.name}</span>`;

            const dropdown = document.createElement('div');
            dropdown.className = 'language-dropdown';

            Object.entries(this.languages).forEach(([code, lang]) => {
                const option = document.createElement('a');
                option.href = '#';
                option.className = 'language-option';
                if (code === this.currentLanguage) {
                    option.classList.add('active');
                }

                option.innerHTML = `
                    <span class="language-name">${lang.name}</span>
                    <span class="language-code">${code}</span>
                `;

                option.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.changeLanguage(code);
                    dropdown.classList.remove('show');
                    button.classList.remove('open');
                });

                dropdown.appendChild(option);
            });

            button.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('show');
                button.classList.toggle('open');
            });

            switcher.appendChild(button);
            switcher.appendChild(dropdown);
            header.appendChild(switcher);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            document.querySelectorAll('.language-dropdown').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
            document.querySelectorAll('.language-button').forEach(button => {
                button.classList.remove('open');
            });
        });
    }

    async changeLanguage(langCode) {
        if (langCode === this.currentLanguage) return;

        await this.loadLanguage(langCode);
        this.currentLanguage = langCode;
        localStorage.setItem('sysmanage-docs-language', langCode);

        this.applyLanguage();
        this.updateDirection();
        this.updateLanguageSwitcher();
    }

    updateLanguageSwitcher() {
        const buttons = document.querySelectorAll('.language-button');
        const currentLang = this.languages[this.currentLanguage];

        buttons.forEach(button => {
            button.innerHTML = `<span class="language-icon">🌐</span><span>${currentLang.name}</span>`;
        });

        // Update active state in dropdowns
        document.querySelectorAll('.language-option').forEach(option => {
            option.classList.remove('active');
            const code = option.querySelector('.language-code').textContent;
            if (code === this.currentLanguage) {
                option.classList.add('active');
            }
        });
    }

    updateDirection() {
        const isRTL = this.languages[this.currentLanguage].rtl;
        document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
        document.documentElement.setAttribute('lang', this.currentLanguage);
    }

    applyLanguage() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);

            if (element.hasAttribute('data-i18n-attr')) {
                const attr = element.getAttribute('data-i18n-attr');
                element.setAttribute(attr, translation);
            } else if (element.hasAttribute('data-i18n-html')) {
                // Use innerHTML for content that contains HTML tags
                element.innerHTML = translation;
            } else {
                element.textContent = translation;
            }
        });

        // Update placeholders
        const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
        placeholderElements.forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = this.t(key);
            element.setAttribute('placeholder', translation);
        });

        // Update document title
        const titleKey = document.documentElement.getAttribute('data-i18n-title');
        if (titleKey) {
            document.title = this.t(titleKey);
        }
    }

    t(key, params = {}) {
        const langTranslations = this.translations[this.currentLanguage] || {};
        const fallbackTranslations = this.translations['en'] || {};

        let translation = this.getNestedValue(langTranslations, key) ||
                         this.getNestedValue(fallbackTranslations, key) ||
                         key;

        // Replace parameters
        Object.entries(params).forEach(([param, value]) => {
            translation = translation.replace(`{{${param}}}`, value);
        });

        return translation;
    }

    getNestedValue(obj, path) {
        return path.split('.').reduce((current, key) => {
            return current && current[key];
        }, obj);
    }

    // Helper method for dynamic content
    translate(key, params = {}) {
        return this.t(key, params);
    }
}

// Initialize i18n system when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', async () => {
        window.i18n = new I18n();
        await window.i18n.init();
    });
} else {
    // DOM is already loaded
    window.i18n = new I18n();
    window.i18n.init();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = I18n;
}