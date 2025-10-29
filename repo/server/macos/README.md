# SysManage Server macOS Packages

This directory contains macOS .pkg installer packages for SysManage Server.

## Repository Structure

```
macos/
└── VERSION/
    ├── sysmanage-VERSION-macos.pkg
    └── sysmanage-VERSION-macos.pkg.sha256
```

## System Requirements

- **OS**: macOS 11 (Big Sur) or later
- **Architecture**: Intel (x86_64) and Apple Silicon (ARM64)
- **Python**: 3.9 or later (included with macOS)
- **Required**: PostgreSQL 12+, nginx
- **Disk Space**: 500 MB
- **Memory**: 2 GB minimum, 4 GB recommended

## Installation

### Download and Install

```bash
# Download the latest version
VERSION="0.9.0"  # Replace with desired version
curl -L -O https://bceverly.github.io/sysmanage-docs/repo/server/macos/${VERSION}/sysmanage-${VERSION}-macos.pkg

# Verify checksum
curl -L -O https://bceverly.github.io/sysmanage-docs/repo/server/macos/${VERSION}/sysmanage-${VERSION}-macos.pkg.sha256
shasum -a 256 -c sysmanage-${VERSION}-macos.pkg.sha256

# Install
sudo installer -pkg sysmanage-${VERSION}-macos.pkg -target /
```

### Post-Installation Setup

The installer automatically:
- Creates `/usr/local/lib/sysmanage` directory structure
- Installs Python virtual environment with dependencies
- Copies configuration examples to `/usr/local/etc/sysmanage`
- Creates LaunchDaemon plist for automatic startup
- Configures nginx if already installed

#### 1. Install Dependencies (if not already installed)

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@16
brew services start postgresql@16

# Create database
createdb sysmanage

# Install nginx
brew install nginx
```

#### 2. Configure SysManage

```bash
# Copy and edit configuration
sudo cp /etc/sysmanage.yaml.example /etc/sysmanage.yaml
sudo nano /etc/sysmanage.yaml
```

Update the database connection string:
```yaml
database:
  url: postgresql://user:password@localhost/sysmanage
```

#### 3. Run Database Migrations

```bash
cd /usr/local/lib/sysmanage
.venv/bin/python -m alembic upgrade head
```

#### 4. Configure nginx

```bash
# Copy nginx configuration
sudo cp /usr/local/etc/sysmanage/sysmanage-nginx.conf /usr/local/etc/nginx/servers/

# Restart nginx
brew services restart nginx
```

#### 5. Start the Service

```bash
# Load and start the LaunchDaemon
sudo launchctl load /Library/LaunchDaemons/com.sysmanage.server.plist

# Check status
sudo launchctl list | grep sysmanage

# View logs
tail -f /var/log/sysmanage/server.log
tail -f /var/log/sysmanage/server-error.log
```

## Service Management

### Start/Stop/Restart

```bash
# Stop service
sudo launchctl unload /Library/LaunchDaemons/com.sysmanage.server.plist

# Start service
sudo launchctl load /Library/LaunchDaemons/com.sysmanage.server.plist

# Restart service (unload and reload)
sudo launchctl unload /Library/LaunchDaemons/com.sysmanage.server.plist
sudo launchctl load /Library/LaunchDaemons/com.sysmanage.server.plist
```

### View Service Status

```bash
# Check if service is running
sudo launchctl list | grep com.sysmanage.server

# View real-time logs
tail -f /var/log/sysmanage/server.log
```

## Upgrade

To upgrade to a new version:

```bash
# Download new version
curl -L -O https://bceverly.github.io/sysmanage-docs/repo/server/macos/${NEW_VERSION}/sysmanage-${NEW_VERSION}-macos.pkg

# Stop service
sudo launchctl unload /Library/LaunchDaemons/com.sysmanage.server.plist

# Install new version (will overwrite existing installation)
sudo installer -pkg sysmanage-${NEW_VERSION}-macos.pkg -target /

# Run any new migrations
cd /usr/local/lib/sysmanage
.venv/bin/python -m alembic upgrade head

# Start service
sudo launchctl load /Library/LaunchDaemons/com.sysmanage.server.plist
```

## Uninstall

```bash
# Stop and unload service
sudo launchctl unload /Library/LaunchDaemons/com.sysmanage.server.plist

# Remove files
sudo rm -rf /usr/local/lib/sysmanage
sudo rm -rf /usr/local/etc/sysmanage
sudo rm -rf /usr/local/share/doc/sysmanage
sudo rm -rf /var/lib/sysmanage
sudo rm -rf /var/log/sysmanage
sudo rm /Library/LaunchDaemons/com.sysmanage.server.plist

# Remove nginx configuration
sudo rm /usr/local/etc/nginx/servers/sysmanage-nginx.conf
brew services restart nginx

# Optionally remove database
dropdb sysmanage
```

## Architecture Support

The macOS package supports both Intel and Apple Silicon:

- **Intel (x86_64)**: Runs natively on Intel Macs
- **Apple Silicon (ARM64)**: The installer automatically detects Apple Silicon and builds the Python virtual environment with ARM64 architecture

The package will automatically detect your Mac's architecture during installation and configure appropriately.

## Troubleshooting

### Service won't start

```bash
# Check logs for errors
tail -50 /var/log/sysmanage/server-error.log

# Verify configuration
cat /etc/sysmanage.yaml

# Check database connectivity
psql postgresql://user:password@localhost/sysmanage -c "SELECT 1"
```

### Port conflicts

If port 8080 is already in use:

```bash
# Edit LaunchDaemon plist
sudo nano /Library/LaunchDaemons/com.sysmanage.server.plist

# Change port in ProgramArguments section
# Then reload service
sudo launchctl unload /Library/LaunchDaemons/com.sysmanage.server.plist
sudo launchctl load /Library/LaunchDaemons/com.sysmanage.server.plist
```

### Python dependency issues

```bash
# Rebuild virtual environment
cd /usr/local/lib/sysmanage
rm -rf .venv

# For Intel Macs
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# For Apple Silicon
arch -arm64 python3 -m venv .venv
arch -arm64 .venv/bin/pip install -r requirements.txt
```

## Documentation

- **Main Documentation**: https://sysmanage.org/docs
- **Server Setup Guide**: https://sysmanage.org/docs/server/installation
- **Configuration Reference**: https://sysmanage.org/docs/server/configuration

## Support

- **Issues**: https://github.com/bceverly/sysmanage/issues
