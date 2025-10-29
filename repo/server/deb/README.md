# SysManage Server APT Repository

This directory contains a Debian APT repository for distributing SysManage Server packages.

## Repository Structure

The repository uses **version-based organization** for clean management of multiple package versions:

```
apt/
├── dists/
│   └── stable/
│       ├── Release                          # Repository metadata
│       └── main/
│           └── binary-amd64/
│               ├── Packages                  # Package index (auto-generated)
│               └── Packages.gz              # Compressed package index (auto-generated)
└── pool/
    └── main/
        ├── 0.9.0-1/                         # Version-specific directory
        │   └── sysmanage-server_0.9.0-1_all.deb
        ├── 0.10.0-1/                        # Next version
        │   └── sysmanage-server_0.10.0-1_all.deb
        └── ...                               # Additional versions
```

## Adding the Repository (For Users)

Users can add this repository to their system with:

```bash
# Add the repository
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/repo/server/deb/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage-server.list

# Update package lists
sudo apt update

# Install sysmanage-server
sudo apt install sysmanage-server

# Or install a specific version
sudo apt install sysmanage-server=0.9.0-1
```

**Note**: The `[trusted=yes]` option is used because we're not signing packages with GPG for the initial release. For production use, you should set up GPG signing.

## Accessing via GitHub Pages

This repository is served via GitHub Pages at:
- **Base URL**: `https://bceverly.github.io/sysmanage-docs/repo/server/deb/apt`
- **Repository URL**: `https://bceverly.github.io/sysmanage-docs/repo/server/deb/apt stable main`

## Package Information

- **Package Name**: `sysmanage-server`
- **Description**: Centralized management server for SysManage infrastructure
- **Architecture**: all (Python-based, architecture independent)
- **Required OS**: Ubuntu 20.04+, Debian 11+

## Dependencies

The SysManage Server package automatically installs:
- Python 3.9+
- PostgreSQL 12+
- nginx
- Various Python packages (installed via pip in virtual environment)

## Configuration

After installation:

```bash
# Edit configuration
sudo nano /etc/sysmanage/sysmanage.yaml

# Enable and start service
sudo systemctl enable sysmanage-server
sudo systemctl start sysmanage-server

# Check status
sudo systemctl status sysmanage-server
```

## Documentation

- **Main Documentation**: https://sysmanage.org/docs
- **Server Setup Guide**: https://sysmanage.org/docs/server/installation
- **Configuration Reference**: https://sysmanage.org/docs/server/configuration

## Support

- **Issues**: https://github.com/bceverly/sysmanage/issues
- **Discussions**: https://github.com/bceverly/sysmanage/discussions
