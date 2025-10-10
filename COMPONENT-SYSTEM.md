# Component System Documentation

## Overview

The SysManage documentation site now uses a centralized component system for headers and footers. This eliminates code duplication and uses absolute paths from the site root, making maintenance much easier.

## How It Works

1. **Single Source of Truth**: All header/footer HTML is defined in `/assets/js/components.js`
2. **Absolute Paths**: Uses absolute paths from the site root (e.g., `/assets/images/logo.svg` or `/sysmanage-docs/assets/images/logo.svg` for GitHub Pages)
3. **Dynamic Injection**: Components are injected into pages at runtime via JavaScript
4. **i18n Compatible**: Works seamlessly with the existing internationalization system

## Usage

### Simple Auto-Injection (Recommended)

Add data attributes to your `<body>` tag:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>My Page</title>
    <link rel="stylesheet" href="/assets/css/style.css">
</head>
<body data-auto-header="documentation" data-auto-footer>
    <!-- Header and Footer injected automatically by components.js -->

    <main>
        <!-- Your page content here -->
    </main>

    <script src="/assets/js/components.js"></script>
    <script src="/assets/js/i18n.js"></script>
</body>
</html>
```

**Attributes:**
- `data-auto-header="active-link-name"` - Injects header with specified active nav link
  - Valid values: `features`, `getting-started`, `documentation`, `config-builder`
- `data-auto-footer` - Injects footer

### Manual Injection (Advanced)

If you need more control:

```javascript
// Inject header programmatically
window.components.injectHeader('documentation');

// Inject footer programmatically
window.components.injectFooter();
```

### Get Component HTML

To get the HTML without injecting:

```javascript
const headerHTML = window.components.getHeader('documentation');
const footerHTML = window.components.getFooter();
```

## File Structure

```
/assets/js/
  ├── components.js    # Component definitions (header, footer)
  ├── i18n.js         # Internationalization system
  ├── navbar.js       # Navbar interactions
  └── main.js         # Main site JavaScript
```

## Script Loading Order

**IMPORTANT**: Load scripts in this order:

```html
<script src="/assets/js/components.js"></script>  <!-- Load first -->
<script src="/assets/js/i18n.js"></script>        <!-- Load second -->
<script src="/assets/js/navbar.js"></script>
<script src="/assets/js/main.js"></script>
```

Why? Components must be injected into the DOM before i18n.js scans for elements to translate.

## Path Detection

The system automatically detects whether you're on:
- **GitHub Pages**: Uses `/sysmanage-docs/` prefix
- **Local/Custom Domain**: Uses `/` prefix

This is handled automatically in `components.js` via the `detectSiteRoot()` method.

## Migrating Existing Pages

### Before (with relative paths and duplicated HTML):

```html
<body>
    <header class="site-header">
        <nav class="navbar">
            <div class="container">
                <div class="nav-brand">
                    <a href="../../">
                        <img src="../../assets/images/sysmanage-logo.svg" alt="SysManage" class="logo">
                    </a>
                </div>
                <!-- ... 30 more lines ... -->
            </div>
        </nav>
    </header>

    <main>Content</main>

    <footer class="site-footer">
        <!-- ... 50 more lines ... -->
    </footer>

    <script src="../../assets/js/i18n.js"></script>
</body>
```

### After (with component system):

```html
<body data-auto-header="documentation" data-auto-footer>
    <!-- Header and Footer injected automatically -->

    <main>Content</main>

    <script src="/assets/js/components.js"></script>
    <script src="/assets/js/i18n.js"></script>
</body>
```

**Benefits:**
- Reduced HTML by ~80 lines per page
- No more relative path calculations (`../../` vs `../`)
- Single point of maintenance for header/footer
- Automatic path detection for different environments

## Adding New Components

To add a new component to the system:

1. Open `/assets/js/components.js`
2. Add a new method to the `Components` class:

```javascript
getMyComponent() {
    const root = this.siteRoot;
    return `
        <div class="my-component">
            <a href="${root}some-page.html">Link</a>
        </div>
    `;
}
```

3. Optionally add injection methods:

```javascript
injectMyComponent() {
    const html = this.getMyComponent();
    // Insert into DOM where needed
}
```

## Troubleshooting

### Components don't appear
- Check that `components.js` is loaded **before** content is visible
- Verify the `data-auto-header` and `data-auto-footer` attributes are on the `<body>` tag
- Check browser console for JavaScript errors

### Paths are wrong
- Verify you're using absolute paths (starting with `/`) not relative (`../`)
- Check the `detectSiteRoot()` logic if you're on a custom domain

### Translations don't work
- Ensure `components.js` loads **before** `i18n.js`
- Components must be in the DOM before i18n scans for `data-i18n` attributes

## Example Pages

See these pages for working examples:
- `/docs/index.html` - Documentation landing page
- `/docs/architecture/performance-testing.html` - Nested page example
