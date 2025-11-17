// SysManage Documentation Site - Reusable Components
// This file contains HTML components that are dynamically injected into pages

class Components {
    constructor() {
        this.siteRoot = this.detectSiteRoot();
    }

    /**
     * Detect the site root based on current path
     * Returns the path prefix needed to reach the site root (e.g., '../', '../../', or '/')
     */
    detectSiteRoot() {
        const path = window.location.pathname;

        // If we're on GitHub Pages, use absolute paths from the repo root
        if (path.includes('/sysmanage-docs/')) {
            return '/sysmanage-docs/';
        }

        // For local development or custom domain, use root
        return '/';
    }

    /**
     * Get header/navbar component with absolute paths
     */
    getHeader(activeLink = 'documentation') {
        const root = this.siteRoot;

        return `
    <header class="site-header">
        <nav class="navbar">
            <div class="container">
                <div class="nav-brand">
                    <a href="${root}">
                        <img src="${root}assets/images/sysmanage-logo.svg" alt="SysManage" class="logo">
                    </a>
                </div>
                <div class="nav-menu">
                    <a href="${root}docs/" class="nav-link${activeLink === 'documentation' ? ' active' : ''}" data-i18n="nav.documentation" data-i18n-html>Documentation</a>
                    <a href="${root}config-builder.html" class="nav-link${activeLink === 'config-builder' ? ' active' : ''}" data-i18n="nav.config_builder" data-i18n-html>Configuration Builder</a>
                    <a href="https://github.com/bceverly/sysmanage" class="nav-link" target="_blank" data-i18n="nav.github_server" data-i18n-html>Server GitHub</a>
                    <a href="https://github.com/bceverly/sysmanage-agent" class="nav-link" target="_blank" data-i18n="nav.github_agent" data-i18n-html>Agent GitHub</a>
                </div>
            </div>
        </nav>
    </header>`;
    }

    /**
     * Get footer component with absolute paths
     */
    getFooter() {
        const root = this.siteRoot;

        return `
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>SysManage</h3>
                    <p data-i18n="footer.description" data-i18n-html>Modern system management platform for comprehensive infrastructure monitoring and automation.</p>
                </div>
                <div class="footer-section">
                    <h3 data-i18n="footer.documentation" data-i18n-html>Documentation</h3>
                    <ul>
                        <li><a href="${root}docs/server/" data-i18n="footer.server_docs" data-i18n-html>Server Docs</a></li>
                        <li><a href="${root}docs/agent/" data-i18n="footer.agent_docs" data-i18n-html>Agent Docs</a></li>
                        <li><a href="${root}docs/api/" data-i18n="footer.api_reference" data-i18n-html>API Reference</a></li>
                        <li><a href="${root}docs/security/" data-i18n="footer.security" data-i18n-html>Security</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3 data-i18n="footer.community" data-i18n-html>Community</h3>
                    <ul>
                        <li><a href="https://github.com/bceverly/sysmanage" target="_blank" data-i18n="footer.github_repo" data-i18n-html>GitHub Repository</a></li>
                        <li><a href="https://github.com/bceverly/sysmanage/issues" target="_blank" data-i18n="footer.issue_tracker" data-i18n-html>Issue Tracker</a></li>
                        <li><a href="https://github.com/bceverly/sysmanage/issues" target="_blank" data-i18n="footer.discussions" data-i18n-html>Discussions</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3 data-i18n="footer.license" data-i18n-html>License</h3>
                    <p data-i18n="footer.licensed_under" data-i18n-html>Licensed under AGPLv3</p>
                    <p><a href="https://github.com/bceverly/sysmanage/blob/main/LICENSE" target="_blank" data-i18n="footer.view_license" data-i18n-html>View License</a></p>
                </div>
            </div>
            <div class="footer-bottom">
                <p data-i18n="footer.copyright">&copy; 2024 SysManage. All rights reserved.</p>
            </div>
        </div>
    </footer>`;
    }

    /**
     * Inject header into the page
     * Should be called before <main> or at the start of <body>
     */
    injectHeader(activeLink = 'documentation') {
        const body = document.body;
        const headerHTML = this.getHeader(activeLink);

        // Insert header as first child of body
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = headerHTML;
        const header = tempDiv.firstElementChild;

        body.insertBefore(header, body.firstChild);
    }

    /**
     * Inject footer into the page
     * Should be called at the end of <body>
     */
    injectFooter() {
        const body = document.body;
        const footerHTML = this.getFooter();

        // Insert footer at the end of body
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = footerHTML;
        const footer = tempDiv.firstElementChild;

        body.appendChild(footer);
    }

    /**
     * Auto-inject components based on page markers
     *
     * Usage in HTML:
     * Add data-auto-header="active-link-name" to <body> tag to auto-inject header
     * Add data-auto-footer to <body> tag to auto-inject footer
     */
    autoInject() {
        const body = document.body;

        // Auto-inject header if requested
        if (body.hasAttribute('data-auto-header')) {
            const activeLink = body.getAttribute('data-auto-header') || 'documentation';
            this.injectHeader(activeLink);
        }

        // Auto-inject footer if requested
        if (body.hasAttribute('data-auto-footer')) {
            this.injectFooter();
        }
    }
}

// Initialize components system when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.components = new Components();
        window.components.autoInject();
    });
} else {
    window.components = new Components();
    window.components.autoInject();
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Components;
}
