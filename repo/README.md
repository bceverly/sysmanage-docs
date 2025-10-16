# SysManage Agent Package Repositories

This directory contains package repositories for installing the SysManage Agent across different Linux distributions.

## Repository Structure

```
repo/
├── deb/          # Debian/Ubuntu APT repository
└── rpm/          # Red Hat/Fedora/openSUSE/SLES YUM/DNF/Zypper repository
```

## Supported Platforms

### Debian/Ubuntu (DEB Packages)

- **Ubuntu 24.04 LTS (Noble)** - Python 3.12
- **Ubuntu 22.04 LTS (Jammy)** - Python 3.10
- **Debian 12 (Bookworm)** - Python 3.11

### Red Hat/CentOS/Fedora (RPM Packages)

- **RHEL 9 / CentOS Stream 9** - Python 3.9+ (2022+)
- **Rocky Linux 9 / AlmaLinux 9** - Python 3.9+ (2022+)
- **RHEL 8 / CentOS 8** - Python 3.11 via AppStream (2019+)
- **Rocky Linux 8 / AlmaLinux 8** - Python 3.11 via AppStream (2020+)
- **Fedora 38+** - Python 3.11+ (2023+)

### openSUSE/SLES (RPM Packages)

- **openSUSE Leap 15.x** - Python 3.11 (2021+)
- **openSUSE Tumbleweed** - Python 3.11+ (Rolling)
- **SUSE Linux Enterprise Server 15** - Python 3.11 (2018+)

## Installation Instructions

### Ubuntu/Debian

```bash
# Add the repository
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/repo/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/sysmanage.list

# Update package list
sudo apt update

# Install sysmanage-agent
sudo apt install sysmanage-agent
```

### RHEL 9 / Rocky 9 / AlmaLinux 9 / CentOS Stream 9

```bash
# Add the repository
sudo tee /etc/yum.repos.d/sysmanage.repo << EOF
[sysmanage]
name=SysManage Agent Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/rpm/el9/x86_64
enabled=1
gpgcheck=0
EOF

# Install sysmanage-agent
sudo dnf install sysmanage-agent
```

### RHEL 8 / Rocky 8 / AlmaLinux 8

```bash
# Install Python 3.11 first (required)
sudo dnf module install python311

# Add the repository
sudo tee /etc/yum.repos.d/sysmanage.repo << EOF
[sysmanage]
name=SysManage Agent Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/rpm/el8/x86_64
enabled=1
gpgcheck=0
EOF

# Install sysmanage-agent
sudo dnf install sysmanage-agent
```

### Fedora 38+

```bash
# Add the repository
sudo tee /etc/yum.repos.d/sysmanage.repo << EOF
[sysmanage]
name=SysManage Agent Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/rpm/fedora/39/x86_64
enabled=1
gpgcheck=0
EOF

# Install sysmanage-agent
sudo dnf install sysmanage-agent
```

### openSUSE Leap 15.x

```bash
# Add the repository
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/rpm/opensuse-leap/15/x86_64 sysmanage
sudo zypper refresh

# Install sysmanage-agent
sudo zypper install sysmanage-agent
```

### openSUSE Tumbleweed

```bash
# Add the repository
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/rpm/opensuse-tumbleweed/x86_64 sysmanage
sudo zypper refresh

# Install sysmanage-agent
sudo zypper install sysmanage-agent
```

### SUSE Linux Enterprise Server 15

```bash
# Add the repository
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/rpm/sles/15/x86_64 sysmanage
sudo zypper refresh

# Install sysmanage-agent
sudo zypper install sysmanage-agent
```

## Post-Installation

After installation, configure the agent:

```bash
# Edit configuration
sudo nano /etc/sysmanage-agent.yaml

# Restart the service
sudo systemctl restart sysmanage-agent

# Check status
sudo systemctl status sysmanage-agent
```

## Direct Downloads

Alternatively, download packages directly from GitHub Releases:

https://github.com/bceverly/sysmanage-agent/releases

## Repository Maintainer Documentation

- DEB Repository: See [repo/deb/README.md](deb/README.md)
- RPM Repository: See [repo/rpm/README.md](rpm/README.md)
