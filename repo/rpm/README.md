# SysManage RPM Repository

This directory contains RPM repositories for distributing SysManage packages.

## Available Repositories

### SysManage Agent
The agent runs on managed systems and communicates with the server.

- **Repository**: [agent/rpm/](../agent/rpm/)
- **Documentation**: [Agent RPM Repository Guide](../agent/rpm/README.md)

Configure the agent repository:

**CentOS/RHEL/Fedora/Rocky/AlmaLinux:**
```bash
sudo tee /etc/yum.repos.d/sysmanage-agent.repo <<EOF
[sysmanage-agent]
name=SysManage Agent Repository
baseurl=https://bceverly.github.io/sysmanage-docs/repo/agent/rpm/centos/\$releasever/\$basearch
enabled=1
gpgcheck=0
EOF

sudo dnf install sysmanage-agent
```

**OpenSUSE/SLES:**
```bash
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/agent/rpm/opensuse sysmanage-agent
sudo zypper refresh
sudo zypper install sysmanage-agent
```

### SysManage Server
The server provides centralized management and web interface.

- **Repository**: [server/rpm/](../server/rpm/)
- **Documentation**: [Server RPM Repository Guide](../server/rpm/README.md)

Configure the server repository:

**CentOS/RHEL/Fedora/Rocky/AlmaLinux:**
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

**OpenSUSE/SLES:**
```bash
sudo zypper addrepo https://bceverly.github.io/sysmanage-docs/repo/server/rpm/opensuse sysmanage-server
sudo zypper refresh
sudo zypper install sysmanage-server
```

## Repository Structure

Both repositories use version-based organization:

```
rpm/
├── agent/
│   └── rpm/
│       ├── centos/
│       │   └── VERSION/
│       │       ├── x86_64/
│       │       └── noarch/
│       └── opensuse/
│           └── VERSION/
│               └── noarch/
└── server/
    └── rpm/
        ├── centos/
        │   └── VERSION/
        │       ├── x86_64/
        │       └── noarch/
        └── opensuse/
            └── VERSION/
                └── noarch/
```

## Support

- **Documentation**: https://sysmanage.org/docs
- **Issues**: https://github.com/bceverly/sysmanage/issues
- **Agent Issues**: https://github.com/bceverly/sysmanage-agent/issues
