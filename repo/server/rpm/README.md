# SysManage Server RPM Repository

This directory contains RPM repositories for distributing SysManage Server packages.

## Available Repositories

### CentOS/RHEL/Fedora/Rocky/AlmaLinux/Oracle Linux

```bash
sudo tee /etc/yum.repos.d/sysmanage-server.repo <<EOF
[sysmanage-server]
name=SysManage Server Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/server/rpm/centos/\$releasever/\$basearch
enabled=1
gpgcheck=0
EOF

sudo dnf install sysmanage-server
```

### OpenSUSE/SLES

```bash
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/server/rpm/opensuse sysmanage-server
sudo zypper refresh
sudo zypper install sysmanage-server
```

## Repository Structure

```
rpm/
├── centos/
│   └── VERSION/
│       ├── x86_64/
│       │   ├── sysmanage-server-VERSION.x86_64.rpm
│       │   └── repodata/
│       └── noarch/
│           ├── sysmanage-server-VERSION.noarch.rpm
│           └── repodata/
└── opensuse/
    └── VERSION/
        └── noarch/
            ├── sysmanage-server-VERSION.noarch.rpm
            └── repodata/
```

## Package Information

- **Package Name**: `sysmanage-server`
- **Description**: Centralized management server for SysManage infrastructure
- **Architecture**: noarch (Python-based, architecture independent)
- **Required OS**: CentOS 8+, RHEL 8+, Fedora 35+, Rocky Linux 8+, AlmaLinux 8+, Oracle Linux 8+, openSUSE Leap 15.3+

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

## Version-Specific Installation

```bash
# CentOS/RHEL/Fedora
sudo dnf install sysmanage-server-0.9.0-1

# OpenSUSE
sudo zypper install sysmanage-server=0.9.0-1
```

## Documentation

- **Main Documentation**: https://sysmanage.org/docs
- **Server Setup Guide**: https://sysmanage.org/docs/server/installation
- **Configuration Reference**: https://sysmanage.org/docs/server/configuration

## Support

- **Issues**: https://github.com/bceverly/sysmanage/issues
