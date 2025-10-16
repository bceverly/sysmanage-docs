# SysManage Agent - macOS Package Repository

This repository hosts macOS installer packages (`.pkg`) for the SysManage Agent.

## Quick Installation

Download and install the latest version:

```bash
# Download the latest package
VERSION=$(curl -s https://bceverly.github.io/sysmanage-docs/repo/mac/latest.txt)
curl -O https://bceverly.github.io/sysmanage-docs/repo/mac/packages/$VERSION/sysmanage-agent-$VERSION-macos.pkg

# Install the package
sudo installer -pkg sysmanage-agent-$VERSION-macos.pkg -target /

# Configure the agent
sudo nano /etc/sysmanage-agent.yaml

# Start the service
sudo launchctl start com.sysmanage.agent
```

## Requirements

- **macOS Version**: 11.0 (Big Sur) or later
- **Architecture**: Apple Silicon (ARM64) or Intel (x86_64)
- **Python**: 3.9 or later (system Python is used)

## Manual Download

Browse available versions at: https://bceverly.github.io/sysmanage-docs/repo/mac/packages/

Or check the package index: https://bceverly.github.io/sysmanage-docs/repo/mac/index.json

## Verify Package Integrity

Each package includes a SHA256 checksum file:

```bash
# Download package and checksum
curl -O https://bceverly.github.io/sysmanage-docs/repo/mac/packages/$VERSION/sysmanage-agent-$VERSION-macos.pkg
curl -O https://bceverly.github.io/sysmanage-docs/repo/mac/packages/$VERSION/sysmanage-agent-$VERSION-macos.pkg.sha256

# Verify checksum
shasum -a 256 -c sysmanage-agent-$VERSION-macos.pkg.sha256
```

## Service Management

The agent runs as a LaunchDaemon and starts automatically at boot.

### Check Service Status

```bash
sudo launchctl print system/com.sysmanage.agent
```

### Start/Stop Service

```bash
# Start
sudo launchctl start com.sysmanage.agent

# Stop
sudo launchctl stop com.sysmanage.agent
```

### View Logs

```bash
# Standard output
tail -f /var/log/sysmanage-agent.log

# Error output
tail -f /var/log/sysmanage-agent-error.log
```

## Uninstallation

```bash
# Stop and unload the service
sudo launchctl unload /Library/LaunchDaemons/com.sysmanage.agent.plist

# Remove installed files
sudo rm -rf /opt/sysmanage-agent
sudo rm /Library/LaunchDaemons/com.sysmanage.agent.plist
sudo rm /etc/sysmanage-agent.yaml
sudo rm /etc/sysmanage-agent.yaml.example

# Remove data and logs (optional)
sudo rm -rf /var/lib/sysmanage-agent
sudo rm -rf /var/log/sysmanage-agent*.log
```

## Configuration

The agent configuration file is located at `/etc/sysmanage-agent.yaml`.

An example configuration is provided at `/etc/sysmanage-agent.yaml.example`.

Key configuration options:

- **server.url**: WebSocket URL of your SysManage server
- **server.token**: Authentication token
- **database.path**: SQLite database location
- **logging.level**: Log verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Troubleshooting

### Service won't start

Check the error log:
```bash
sudo tail -50 /var/log/sysmanage-agent-error.log
```

### Permission issues

Ensure proper ownership:
```bash
sudo chown -R root:wheel /opt/sysmanage-agent
sudo chmod 755 /opt/sysmanage-agent
```

### Database errors

Check database directory permissions:
```bash
sudo mkdir -p /var/lib/sysmanage-agent
sudo chmod 755 /var/lib/sysmanage-agent
```

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/bceverly/sysmanage-agent/issues
- Documentation: https://bceverly.github.io/sysmanage-docs/

## Package Details

- **Installation Location**: `/opt/sysmanage-agent`
- **Service File**: `/Library/LaunchDaemons/com.sysmanage.agent.plist`
- **Configuration**: `/etc/sysmanage-agent.yaml`
- **Database**: `/var/lib/sysmanage-agent/agent.db`
- **Logs**: `/var/log/sysmanage-agent.log` and `/var/log/sysmanage-agent-error.log`

## Building from Source

See the [sysmanage-agent repository](https://github.com/bceverly/sysmanage-agent) for build instructions.
