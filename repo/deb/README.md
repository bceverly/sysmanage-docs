# SysManage APT Repository

This directory contains Debian APT repositories for distributing SysManage packages.

## Available Repositories

### SysManage Agent
The agent runs on managed systems and communicates with the server.

- **Repository**: [agent/deb/](../agent/deb/)
- **Documentation**: [Agent APT Repository Guide](../agent/deb/README.md)

Add the agent repository:
```bash
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/repo/agent/deb/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage-agent.list
sudo apt update
sudo apt install sysmanage-agent
```

### SysManage Server
The server provides centralized management and web interface.

- **Repository**: [server/deb/](../server/deb/)
- **Documentation**: [Server APT Repository Guide](../server/deb/README.md)

Add the server repository:
```bash
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/repo/server/deb/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage-server.list
sudo apt update
sudo apt install sysmanage-server
```

## Repository Structure

Both repositories use version-based organization for clean management:

```
deb/
├── agent/
│   └── deb/
│       ├── apt/
│       │   ├── dists/stable/
│       │   └── pool/main/VERSION/
│       └── README.md
└── server/
    └── deb/
        ├── apt/
        │   ├── dists/stable/
        │   └── pool/main/VERSION/
        └── README.md
```

## Support

- **Documentation**: https://sysmanage.org/docs
- **Issues**: https://github.com/bceverly/sysmanage/issues
- **Agent Issues**: https://github.com/bceverly/sysmanage-agent/issues
