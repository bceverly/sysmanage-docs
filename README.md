# SysManage Documentation Site

This repository contains the GitHub Pages documentation website for SysManage at [sysmanage.org](https://sysmanage.org).

## Overview

The SysManage documentation site provides comprehensive guides, tutorials, and reference materials for both the SysManage server and agent components. The site is built with static HTML/CSS/JavaScript and hosted on GitHub Pages.

## Structure

```
/
├── index.html              # Homepage
├── CNAME                   # Custom domain configuration
├── _config.yml             # Jekyll configuration
├── docs/                   # Documentation sections
│   ├── index.html          # Documentation landing page
│   ├── server/             # Server documentation
│   ├── agent/              # Agent documentation
│   ├── api/                # API reference
│   ├── security/           # Security documentation
│   ├── getting-started/    # Quick start guides
│   └── administration/     # Admin guides
├── assets/                 # Static assets
│   ├── css/style.css       # Main stylesheet
│   ├── js/main.js          # JavaScript functionality
│   └── images/             # Images and graphics
└── README.md               # This file
```

## Documentation Sections

### Server Documentation (`/docs/server/`)
- Installation and setup guides
- Configuration options
- Deployment strategies
- Feature overviews
- Troubleshooting guides

### Agent Documentation (`/docs/agent/`)
- Cross-platform installation
- Configuration and auto-discovery
- Privileged execution setup
- Platform-specific guides
- Security and mTLS setup

### API Reference (`/docs/api/`)
- REST API documentation
- WebSocket API reference
- Authentication guides
- Integration examples

### Security (`/docs/security/`)
- Security features overview
- mTLS configuration
- Security best practices
- Vulnerability reporting

### Getting Started (`/docs/getting-started/`)
- Quick start guides
- First deployment tutorials
- Basic management tasks

### Administration (`/docs/administration/`)
- User management
- Host administration
- Monitoring and alerts
- Backup and maintenance

## Local Development

To work on the documentation site locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bceverly/sysmanage-docs.git
   cd sysmanage-docs
   ```

2. **Serve locally with Jekyll (optional):**
   ```bash
   # Install Jekyll (if not already installed)
   gem install bundler jekyll

   # Create Gemfile if needed
   bundle init
   bundle add jekyll

   # Serve the site
   bundle exec jekyll serve
   ```

3. **Or serve with Python (simple HTTP server):**
   ```bash
   # Python 3
   python -m http.server 8000

   # Python 2
   python -m SimpleHTTPServer 8000
   ```

4. **View the site at:** `http://localhost:8000`

## Contributing

When contributing to the documentation:

1. **Content Updates**: Update the relevant HTML files in the appropriate sections
2. **Styling**: Modify `assets/css/style.css` for visual changes
3. **JavaScript**: Update `assets/js/main.js` for interactive features
4. **New Sections**: Add new directories under `docs/` and update navigation

## Deployment

The site is automatically deployed to GitHub Pages when changes are pushed to the main branch. The custom domain `sysmanage.org` is configured via the `CNAME` file.

### GitHub Pages Settings

- **Source**: Deploy from `main` branch
- **Custom domain**: `sysmanage.org`
- **Enforce HTTPS**: Enabled

### DNS Configuration

The domain should be configured with:
- **A records** pointing to GitHub Pages IPs
- **CNAME record** for `www` subdomain
- See the main documentation for complete DNS setup

## Features

- **Responsive Design**: Mobile-friendly layout
- **Modern UI**: Clean, professional appearance
- **Search Functionality**: Basic search capabilities
- **Smooth Navigation**: Animated scrolling and transitions
- **External Link Indicators**: Visual cues for external links
- **Copy Code Blocks**: One-click code copying
- **Scroll to Top**: Easy navigation for long pages

## License

This documentation site is part of the SysManage project and is licensed under the GNU Affero General Public License v3.0.

## Links

- **Main Project**: [SysManage Server](https://github.com/bceverly/sysmanage)
- **Agent Project**: [SysManage Agent](https://github.com/bceverly/sysmanage-agent)
- **Live Site**: [sysmanage.org](https://sysmanage.org)
- **Issues**: [GitHub Issues](https://github.com/bceverly/sysmanage-docs/issues)