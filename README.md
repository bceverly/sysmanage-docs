# SysManage Documentation

> **Modern Infrastructure Management Made Simple**

This repository contains the complete documentation for SysManage, an open-source infrastructure management platform that provides centralized monitoring, control, and automation for distributed systems.

![SysManage Dashboard](docs/screenshot.png)

[![GitHub Pages](https://img.shields.io/github/deployments/bceverly/sysmanage-docs/github-pages?label=docs)](https://bceverly.github.io/sysmanage-docs/)
[![Link Check](https://github.com/bceverly/sysmanage-docs/workflows/Link%20Check/badge.svg)](https://github.com/bceverly/sysmanage-docs/actions)
[![Accessibility](https://github.com/bceverly/sysmanage-docs/workflows/Accessibility%20Check/badge.svg)](https://github.com/bceverly/sysmanage-docs/actions)
[![License](https://img.shields.io/badge/license-AGPLv3-blue.svg)](LICENSE)

## 📚 Documentation

- **[Getting Started](docs/getting-started/)** - Quick start guide and tutorials
- **[Server Documentation](docs/server/)** - Installation, configuration, and deployment
- **[Agent Documentation](docs/agent/)** - Cross-platform agent setup and management
- **[API Reference](docs/api/)** - Complete REST API documentation
- **[Security](docs/security/)** - Authentication, mTLS, and best practices
- **[Architecture](docs/architecture/)** - System design and scaling strategies
- **[Administration](docs/administration/)** - Backup, maintenance, and troubleshooting

## 🚀 Quick Start

1. **Install SysManage Server**

   ```bash
   # Download and install the server
   curl -sSL https://install.sysmanage.org/server | bash
   ```

2. **Deploy Agents**

   ```bash
   # Install agent on managed hosts
   curl -sSL https://install.sysmanage.org/agent | bash
   ```

3. **Access Dashboard**
   - Open your web browser to `https://your-server:8443`
   - Complete the initial setup wizard
   - Start managing your infrastructure

## 🏗️ Building Documentation

This documentation site is built with:

- **HTML/CSS/JavaScript** - Static site generation
- **Internationalization** - Support for 14 languages
- **GitHub Pages** - Automated deployment
- **Accessibility Testing** - WCAG 2.1 AA compliance

### Local Development

```bash
# Clone the repository
git clone https://github.com/bceverly/sysmanage-docs.git
cd sysmanage-docs

# Install dependencies
npm install

# Start local server
npm run serve

# Generate screenshots (requires dependencies)
npm run screenshots
```

### Building and Testing

```bash
# Run all quality checks
make check

# Run individual checks
npm run lint        # Markdown linting
npm run spellcheck  # Spelling validation
npm run linkcheck   # Link validation
npm run a11y        # Accessibility testing
```

## 🌍 Internationalization

SysManage documentation is available in 14 languages:

- **English** (en) - Primary
- **Spanish** (es)
- **French** (fr)
- **German** (de)
- **Italian** (it)
- **Portuguese** (pt)
- **Dutch** (nl)
- **Russian** (ru)
- **Chinese Simplified** (zh_CN)
- **Chinese Traditional** (zh_TW)
- **Japanese** (ja)
- **Korean** (ko)
- **Hindi** (hi)
- **Arabic** (ar)

Translation files are located in `assets/locales/` and contributions are welcome!

## 📸 Screenshots

Automated screenshots are generated for:

- Dashboard views
- Configuration pages
- Setup wizards
- Mobile responsive layouts

See [SCREENSHOTS.md](SCREENSHOTS.md) for details on the screenshot generation process.

## 🤝 Contributing

We welcome contributions to improve SysManage documentation!

### Ways to Contribute

- **Report Issues** - Found a bug or outdated information?
- **Improve Content** - Fix typos, clarify instructions, add examples
- **Translate** - Help translate documentation to new languages
- **Add Screenshots** - Provide updated or new screenshots

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-improvement`)
3. Make your changes
4. Test locally (`make check`)
5. Commit your changes (`git commit -am 'Add amazing improvement'`)
6. Push to your branch (`git push origin feature/amazing-improvement`)
7. Open a Pull Request

### Style Guide

- Use clear, concise language
- Include code examples where helpful
- Test all instructions on supported platforms
- Follow accessibility guidelines
- Maintain consistent formatting

## 📦 Package Repositories

This repository also hosts package repositories for installing SysManage Agent on various platforms via GitHub Pages:

### DEB Repository (Ubuntu/Debian)

```bash
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/repo/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/sysmanage.list
sudo apt update && sudo apt install sysmanage-agent
```

**Supported Platforms:**

- Ubuntu 26.04 LTS (Resolute) and earlier LTS releases back to 22.04
- Debian 12 (Bookworm) and later

### RPM Repository (RHEL/CentOS/Fedora/Rocky/AlmaLinux/Oracle Linux)

RPM packages are available via [Fedora Copr](https://copr.fedorainfracloud.org/coprs/bceverly/sysmanage/) for both **x86_64** and **aarch64** architectures:

```bash
sudo dnf copr enable bceverly/sysmanage
sudo dnf install sysmanage        # Server
sudo dnf install sysmanage-agent  # Agent
```

**Supported targets (x86_64 and aarch64):**

- **EPEL 10 / CentOS Stream 10** - Python 3.12
- **EPEL 9 / RHEL 9 / Rocky 9 / AlmaLinux 9 / Oracle Linux 9 / CentOS Stream 9** - Python 3.9+
- **EPEL 8 / RHEL 8 / Rocky 8 / AlmaLinux 8 / Oracle Linux 8** - Python 3.11 via AppStream
- **Fedora 41, 42, 43** - Python 3.13+

### openSUSE/SLES (via Open Build Service)

- **openSUSE Leap 15.x** - Python 3.11
- **openSUSE Tumbleweed** - Python 3.11+
- **SUSE Linux Enterprise Server 15** - Python 3.11

### Other Platforms

- **Alpine Linux** 3.19, 3.20, 3.21 - APK packages
- **macOS** 11+ (Big Sur) - Universal `.pkg` installer (Intel and Apple Silicon)
- **Windows** 10+ / Server 2019+ - MSI installer (x64 and ARM64)
- **FreeBSD** 14.0+ - `.pkg` packages (x86_64)
- **OpenBSD** 7.7, 7.8 - Port tarballs and binary packages (x86_64)
- **NetBSD** 10.0+ - `.tgz` packages (x86_64)
- **Snap** - Available via `snap install sysmanage`
- **Flatpak** - Agent available via Flatpak (x86_64)

For more details, see:

- [DEB Repository Documentation](repo/deb/README.md)
- [RPM Repository Documentation](repo/rpm/README.md)
- [General Repository Documentation](repo/README.md)

## 📁 Repository Structure

```text
sysmanage-docs/
├── docs/                   # Documentation content
│   ├── getting-started/    # Getting started guides
│   ├── server/            # Server documentation
│   ├── agent/             # Agent documentation
│   ├── api/               # API reference
│   ├── security/          # Security guides
│   ├── architecture/      # System architecture
│   └── administration/    # Admin guides
├── repo/                  # Package repositories
│   ├── deb/              # Debian/Ubuntu APT repository
│   ├── rpm/              # Red Hat/Fedora YUM/DNF repository
│   │   ├── el8/          # RHEL 8, Rocky 8, AlmaLinux 8, Oracle Linux 8
│   │   ├── el9/          # RHEL 9, Rocky 9, AlmaLinux 9, Oracle Linux 9
│   │   ├── el10/         # RHEL 10, CentOS Stream 10
│   │   └── fedora/       # Fedora 41+
│   ├── agent/            # Agent-specific packages
│   └── server/           # Server-specific packages
├── assets/                # Static assets
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   ├── images/           # Images and icons
│   └── locales/          # Translation files
├── .github/              # GitHub workflows
├── scripts/              # Build and utility scripts
└── node_modules/         # Dependencies
```

## 🔗 Related Projects

- **[SysManage Server](https://github.com/bceverly/sysmanage)** - Core management server
- **[SysManage Agent](https://github.com/bceverly/sysmanage-agent)** - Lightweight monitoring agent
- **[SysManage CLI](https://github.com/bceverly/sysmanage-cli)** - Command-line interface (coming soon)

## 📜 License

This documentation is released under the [GNU Affero General Public License Version 3](LICENSE).

## 🆘 Support

- **Documentation Issues** - [GitHub Issues](https://github.com/bceverly/sysmanage-docs/issues)
- **General Support** - [GitHub Issues](https://github.com/bceverly/sysmanage/issues)
- **Security Issues** - [Security Reporting](docs/security/reporting.html)

---

Made with ❤️ by the SysManage team
