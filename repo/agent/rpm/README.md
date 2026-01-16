# SysManage Agent RPM Repository

YUM/DNF repository for Red Hat-based Linux distributions.

## Repository Structure

```
rpm/
├── el8/                    # RHEL 8, CentOS 8, Rocky 8, AlmaLinux 8, Oracle Linux 8
│   └── x86_64/
│       ├── *.rpm
│       └── repodata/
├── el9/                    # RHEL 9, CentOS Stream 9, Rocky 9, AlmaLinux 9, Oracle Linux 9
│   └── x86_64/
│       ├── *.rpm
│       └── repodata/
├── fedora/
│   └── 39/                 # Fedora 39+
│       └── x86_64/
│           ├── *.rpm
│           └── repodata/
├── opensuse-leap/          # openSUSE Leap 15.x
│   └── 15/
│       └── x86_64/
│           ├── *.rpm
│           └── repodata/
├── opensuse-tumbleweed/    # openSUSE Tumbleweed
│   └── x86_64/
│       ├── *.rpm
│       └── repodata/
└── sles/                   # SUSE Linux Enterprise Server 15
    └── 15/
        └── x86_64/
            ├── *.rpm
            └── repodata/
```

## Supported Platforms

- **RHEL 9 / CentOS Stream 9 / Rocky 9 / AlmaLinux 9 / Oracle Linux 9** - Python 3.9+ (2022+)
- **RHEL 8 / CentOS 8 / Rocky 8 / AlmaLinux 8 / Oracle Linux 8** - Python 3.11 via AppStream (2019+)
- **Fedora 38+** - Python 3.11+ (2023+)
- **openSUSE Leap 15.x** - Python 3.11 (2021+)
- **openSUSE Tumbleweed** - Python 3.11+ (Rolling)
- **SUSE Linux Enterprise Server 15** - Python 3.11 (2018+)

## User Installation

### EL9 (RHEL 9, Rocky 9, AlmaLinux 9, Oracle Linux 9, CentOS Stream 9)

```bash
sudo tee /etc/yum.repos.d/sysmanage.repo << EOF
[sysmanage]
name=SysManage Agent Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/rpm/el9/x86_64
enabled=1
gpgcheck=0
EOF

sudo dnf install sysmanage-agent
```

### EL8 (RHEL 8, Rocky 8, AlmaLinux 8, Oracle Linux 8)

```bash
# Install Python 3.11 first
sudo dnf module install python311

sudo tee /etc/yum.repos.d/sysmanage.repo << EOF
[sysmanage]
name=SysManage Agent Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/rpm/el8/x86_64
enabled=1
gpgcheck=0
EOF

sudo dnf install sysmanage-agent
```

### Fedora 38+

```bash
sudo tee /etc/yum.repos.d/sysmanage.repo << EOF
[sysmanage]
name=SysManage Agent Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/rpm/fedora/39/x86_64
enabled=1
gpgcheck=0
EOF

sudo dnf install sysmanage-agent
```

### openSUSE Leap 15.x

```bash
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/rpm/opensuse-leap/15/x86_64 sysmanage
sudo zypper refresh
sudo zypper install sysmanage-agent
```

### openSUSE Tumbleweed

```bash
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/rpm/opensuse-tumbleweed/x86_64 sysmanage
sudo zypper refresh
sudo zypper install sysmanage-agent
```

### SUSE Linux Enterprise Server 15

```bash
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/rpm/sles/15/x86_64 sysmanage
sudo zypper refresh
sudo zypper install sysmanage-agent
```

## Repository Maintainer Guide

### Prerequisites

```bash
sudo dnf install createrepo_c
```

### Adding a Package to the Repository

Use the `update-repo.sh` script:

```bash
# Add a package to EL9 repository
./update-repo.sh /path/to/sysmanage-agent-X.Y.Z.el9.x86_64.rpm el9

# Add a package to EL8 repository
./update-repo.sh /path/to/sysmanage-agent-X.Y.Z.el8.x86_64.rpm el8

# Add a package to Fedora repository
./update-repo.sh /path/to/sysmanage-agent-X.Y.Z.fc39.x86_64.rpm fedora/39

# Add a package to openSUSE Leap repository
./update-repo.sh /path/to/sysmanage-agent-X.Y.Z.x86_64.rpm opensuse-leap

# Add a package to openSUSE Tumbleweed repository
./update-repo.sh /path/to/sysmanage-agent-X.Y.Z.x86_64.rpm opensuse-tumbleweed

# Add a package to SLES repository
./update-repo.sh /path/to/sysmanage-agent-X.Y.Z.x86_64.rpm sles
```

### Manual Process

```bash
# Example for EL9
cd repo/rpm/el9/x86_64

# Copy the RPM
cp /path/to/sysmanage-agent-*.rpm .

# Generate repository metadata
createrepo_c .

# Commit and push
git add .
git commit -m "Add sysmanage-agent version X.Y.Z for EL9"
git push
```

### Updating an Existing Package

```bash
# Remove old version
rm el9/x86_64/sysmanage-agent-OLD_VERSION.rpm

# Add new version
./update-repo.sh /path/to/sysmanage-agent-NEW_VERSION.rpm el9
```

## Automated Updates

The RPM repository is automatically updated by GitHub Actions when a new release is tagged in the `sysmanage-agent` repository.

Workflow: `.github/workflows/build-centos-rpm.yml`

## GPG Signing (Future)

Currently, packages are not GPG-signed (`gpgcheck=0`). For production deployments, consider adding GPG signing:

1. Generate a GPG key for package signing
2. Sign the RPM: `rpm --addsign sysmanage-agent-*.rpm`
3. Export public key: `gpg --export -a 'SysManage' > RPM-GPG-KEY-sysmanage`
4. Add to repository root
5. Update repository configuration to enable `gpgcheck=1` and add `gpgkey` URL

## Testing

```bash
# Verify repository metadata
curl https://bceverly.github.io/sysmanage-docs/repo/rpm/el9/x86_64/repodata/repomd.xml

# Test installation on a VM or container
docker run -it rockylinux:9 bash
# Inside container, add repo and install package
```

## Troubleshooting

**Repository not found (404)**:
- Ensure GitHub Pages is enabled for the `sysmanage-docs` repository
- Wait 2-5 minutes after pushing for GitHub Pages to update
- Verify the path in your browser

**Package not found**:
- Check that `repodata/` exists and contains `repomd.xml`
- Run `dnf clean all && dnf makecache` to refresh metadata
- Verify the `baseurl` in `/etc/yum.repos.d/sysmanage.repo`
