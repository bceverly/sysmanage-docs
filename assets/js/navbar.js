// SysManage Documentation Site - Shared Navigation Component
// This script dynamically loads a common navigation bar across all documentation pages

(function() {
    'use strict';

    // Configuration for navigation structure
    const navConfig = {
        brand: {
            logoSrc: '/assets/images/sysmanage-logo.svg',
            logoAlt: 'SysManage',
            homeLink: '/'
        },
        links: [
            {
                href: '/#features',
                text: 'Features',
                i18n: 'nav.features'
            },
            {
                href: '/#getting-started',
                text: 'Getting Started',
                i18n: 'nav.getting_started'
            },
            {
                href: '/docs/',
                text: 'Documentation',
                i18n: 'nav.documentation',
                activePattern: /\/docs\//
            },
            {
                href: '/config-builder.html',
                text: 'Configuration Builder',
                i18n: 'nav.config_builder'
            },
            {
                href: 'https://github.com/bceverly/sysmanage',
                text: 'GitHub',
                i18n: 'nav.github',
                external: true
            }
        ]
    };

    // Calculate the relative path based on current document location
    function getRelativePath() {
        const path = window.location.pathname;
        const depth = (path.match(/\//g) || []).length - 1;

        // Root level
        if (depth <= 1) return '';

        // Build relative path (../ for each level deep)
        return '../'.repeat(depth - 1);
    }

    // Adjust paths based on current page depth
    function adjustPath(originalPath) {
        // Don't adjust absolute URLs
        if (originalPath.startsWith('http')) {
            return originalPath;
        }

        const relativePath = getRelativePath();

        // Handle anchor links - if we're in docs, point back to homepage for anchors
        if (originalPath.startsWith('#')) {
            if (window.location.pathname.includes('/docs/')) {
                return relativePath + originalPath;
            }
            return originalPath;
        }

        // If we're in docs, adjust paths accordingly
        if (window.location.pathname.includes('/docs/')) {
            // For root-relative paths starting with /
            if (originalPath.startsWith('/')) {
                return relativePath + originalPath.substring(1);
            }
        }

        return originalPath;
    }

    // Check if current page matches the link pattern
    function isActive(link) {
        const currentPath = window.location.pathname;

        if (link.activePattern) {
            return link.activePattern.test(currentPath);
        }

        // Exact match for non-pattern links
        return currentPath === link.href || currentPath === link.href.replace(/\/$/, '');
    }

    // Build the navigation HTML
    function buildNavigation() {
        const relativePath = getRelativePath();
        const currentPath = window.location.pathname;

        // Build nav links
        const navLinks = navConfig.links.map(link => {
            const href = adjustPath(link.href);
            const isExternal = link.external;
            const active = isActive(link) ? ' active' : '';
            const externalAttrs = isExternal ? ' target="_blank"' : '';

            return `<a href="${href}" class="nav-link${active}" data-i18n="${link.i18n}"${externalAttrs}>${link.text}</a>`;
        }).join('\n                    ');

        // Build complete navigation HTML
        const navHTML = `
    <header class="site-header">
        <nav class="navbar">
            <div class="container">
                <div class="nav-brand">
                    <a href="${adjustPath(navConfig.brand.homeLink)}">
                        <img src="${adjustPath(navConfig.brand.logoSrc)}" alt="${navConfig.brand.logoAlt}" class="logo">
                    </a>
                </div>
                <div class="nav-menu">
                    ${navLinks}
                </div>
            </div>
        </nav>
    </header>`;

        return navHTML;
    }

    // Insert navigation into the page
    function insertNavigation() {
        // Check if navigation already exists
        const existingHeader = document.querySelector('.site-header');
        if (existingHeader) {
            // Replace existing navigation
            existingHeader.outerHTML = buildNavigation();
        } else {
            // Insert at the beginning of body
            document.body.insertAdjacentHTML('afterbegin', buildNavigation());
        }
    }

    // Initialize navigation when DOM is ready
    function initNavigation() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', insertNavigation);
        } else {
            insertNavigation();
        }
    }

    // Export for use by other scripts if needed
    window.SysManageNav = {
        init: initNavigation,
        config: navConfig,
        adjustPath: adjustPath
    };

    // Auto-initialize
    initNavigation();

})();