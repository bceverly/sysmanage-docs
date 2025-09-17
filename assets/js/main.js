// SysManage Documentation Site JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');

    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add active class to current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (currentPath === linkPath ||
            (currentPath.startsWith('/docs/') && linkPath.includes('/docs/'))) {
            link.classList.add('active');
        }
    });

    // Mobile menu toggle (if needed for future mobile navigation)
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');

    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('open');
        });
    }

    // Add animation to feature cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe feature cards and documentation cards
    const animatedElements = document.querySelectorAll('.feature-card, .docs-card, .docs-section-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // Add search functionality (basic implementation)
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const searchableElements = document.querySelectorAll('.docs-card, .feature-card');

            searchableElements.forEach(element => {
                const text = element.textContent.toLowerCase();
                if (text.includes(searchTerm) || searchTerm === '') {
                    element.style.display = '';
                } else {
                    element.style.display = 'none';
                }
            });
        });
    }

    // Copy code blocks functionality with universal copy icon
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const pre = block.parentElement;
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.innerHTML = '⧉'; // Universal copy icon (overlapping squares)
        button.title = 'Copy to clipboard';
        button.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent).then(() => {
                button.innerHTML = '✓';
                button.title = 'Copied!';
                setTimeout(() => {
                    button.innerHTML = '⧉';
                    button.title = 'Copy to clipboard';
                }, 2000);
            });
        });
        pre.style.position = 'relative';
        pre.appendChild(button);
    });

    // Theme toggle (for future dark mode support)
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme',
                document.body.classList.contains('dark-theme') ? 'dark' : 'light'
            );
        });

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }

    // Add external link indicators
    const externalLinks = document.querySelectorAll('a[href^="http"]:not([href*="sysmanage.org"])');
    externalLinks.forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
        // Add external link icon
        const icon = document.createElement('span');
        icon.innerHTML = ' ↗';
        icon.style.fontSize = '0.8em';
        icon.style.opacity = '0.7';
        link.appendChild(icon);
    });

    // Scroll to top functionality
    const scrollToTopButton = document.createElement('button');
    scrollToTopButton.innerHTML = '↑';
    scrollToTopButton.className = 'scroll-to-top';
    scrollToTopButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #3498db;
        color: white;
        border: none;
        font-size: 20px;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s;
        z-index: 1000;
    `;

    document.body.appendChild(scrollToTopButton);

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollToTopButton.style.opacity = '1';
        } else {
            scrollToTopButton.style.opacity = '0';
        }
    });

    scrollToTopButton.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Platform tab navigation with smooth scrolling
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            const tabContainer = this.closest('.platform-tabs, .db-setup-tabs, .service-tabs');

            if (tabContainer) {
                // Remove active class from all buttons and panes in this container
                tabContainer.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                tabContainer.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

                // Add active class to clicked button and corresponding pane
                this.classList.add('active');
                const targetPane = tabContainer.querySelector(`#${tabId}`);
                if (targetPane) {
                    targetPane.classList.add('active');
                }

                // Smooth scroll to the platform section
                const platformSection = tabContainer.closest('.docs-section');
                if (platformSection) {
                    platformSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    // Add click handlers for any other platform navigation elements
    document.querySelectorAll('.platform-nav, .platform-button').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-target') || this.getAttribute('href')?.substring(1);
            if (targetId) {
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });

    console.log('SysManage Documentation Site initialized');
});