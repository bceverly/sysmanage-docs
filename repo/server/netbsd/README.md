# SysManage Server NetBSD Packages

This directory contains NetBSD .tgz packages for SysManage Server.

## Repository Structure

```
netbsd/
└── VERSION/
    ├── sysmanage-VERSION-netbsd.tgz
    └── sysmanage-VERSION-netbsd.tgz.sha256
```

## System Requirements

- **OS**: NetBSD 9.0 or later
- **Architecture**: x86_64 (amd64)
- **Python**: 3.12 or later
- **Required**: PostgreSQL 16+, nginx
- **Disk Space**: 500 MB
- **Memory**: 2 GB minimum, 4 GB recommended

## Installation

### Download and Install

```bash
# Download the latest version
VERSION="0.9.0"  # Replace with desired version
ftp https://bceverly.github.io/sysmanage-docs/repo/server/netbsd/${VERSION}/sysmanage-${VERSION}-netbsd.tgz

# Verify checksum
ftp https://bceverly.github.io/sysmanage-docs/repo/server/netbsd/${VERSION}/sysmanage-${VERSION}-netbsd.tgz.sha256
sha256 -c sysmanage-${VERSION}-netbsd.tgz.sha256 sysmanage-${VERSION}-netbsd.tgz

# Install (requires root)
su -
pkg_add sysmanage-${VERSION}-netbsd.tgz
```

### Post-Installation Setup

The package automatically installs files to `/usr/pkg/lib/sysmanage` and includes PostgreSQL 16 and nginx as dependencies.

#### 1. Initialize PostgreSQL

```bash
# Initialize PostgreSQL database cluster (if not already done)
su -
/etc/rc.d/pgsql initdb

# Enable PostgreSQL to start at boot
echo "pgsql=YES" >> /etc/rc.conf

# Start PostgreSQL
/etc/rc.d/pgsql start
```

#### 2. Create Database and User

```bash
# Create SysManage database user (as root)
su - pgsql -c "createuser -P sysmanage"
# You'll be prompted to enter a password

# Create SysManage database
su - pgsql -c "createdb -O sysmanage sysmanage"
```

#### 3. Configure SysManage

```bash
# Copy example configuration
cp /usr/pkg/etc/sysmanage/sysmanage.yaml.example /usr/pkg/etc/sysmanage.yaml

# Edit configuration
vi /usr/pkg/etc/sysmanage.yaml
```

Update the database connection string:
```yaml
database:
  url: postgresql://sysmanage:your-password@localhost/sysmanage
```

#### 4. Install Python Dependencies and Run Migrations

```bash
# Navigate to installation directory
cd /usr/pkg/lib/sysmanage

# Create Python virtual environment
python3.12 -m venv .venv

# Install dependencies
.venv/bin/pip install -r requirements.txt

# Run database migrations
.venv/bin/python -m alembic upgrade head
```

#### 5. Configure nginx (Optional)

```bash
# Copy nginx configuration
cp /usr/pkg/share/examples/sysmanage/sysmanage-nginx.conf /usr/pkg/etc/nginx/sites-enabled/

# Enable nginx to start at boot
echo "nginx=YES" >> /etc/rc.conf

# Test nginx configuration
nginx -t

# Start nginx
/etc/rc.d/nginx start
```

#### 6. Start the Service

```bash
# Copy rc.d script
cp /usr/pkg/share/examples/rc.d/sysmanage /etc/rc.d/
chmod +x /etc/rc.d/sysmanage

# Enable service to start at boot
echo "sysmanage=YES" >> /etc/rc.conf

# Start the service
/etc/rc.d/sysmanage start

# Check status
/etc/rc.d/sysmanage status

# View logs
tail -f /var/log/sysmanage/server.log
tail -f /var/log/sysmanage/server-error.log
```

## Service Management

### Start/Stop/Restart

```bash
# Stop service
/etc/rc.d/sysmanage stop

# Start service
/etc/rc.d/sysmanage start

# Restart service
/etc/rc.d/sysmanage restart

# Check status
/etc/rc.d/sysmanage status
```

### View Service Status and Logs

```bash
# Check if service is running
ps aux | grep sysmanage

# View real-time logs
tail -f /var/log/sysmanage/server.log

# View error logs
tail -f /var/log/sysmanage/server-error.log
```

## Upgrade

To upgrade to a new version:

```bash
# Download new version
ftp https://bceverly.github.io/sysmanage-docs/repo/server/netbsd/${NEW_VERSION}/sysmanage-${NEW_VERSION}-netbsd.tgz

# Verify checksum
ftp https://bceverly.github.io/sysmanage-docs/repo/server/netbsd/${NEW_VERSION}/sysmanage-${NEW_VERSION}-netbsd.tgz.sha256
sha256 -c sysmanage-${NEW_VERSION}-netbsd.tgz.sha256 sysmanage-${NEW_VERSION}-netbsd.tgz

# Stop service
/etc/rc.d/sysmanage stop

# Install new version (will overwrite existing installation)
su -
pkg_add -u sysmanage-${NEW_VERSION}-netbsd.tgz

# Run any new migrations
cd /usr/pkg/lib/sysmanage
.venv/bin/python -m alembic upgrade head

# Start service
/etc/rc.d/sysmanage start
```

## Uninstall

```bash
# Stop and disable service
/etc/rc.d/sysmanage stop
sed -i '/sysmanage=YES/d' /etc/rc.conf

# Remove package
su -
pkg_delete sysmanage

# Remove files and directories
rm -rf /usr/pkg/lib/sysmanage
rm -rf /usr/pkg/etc/sysmanage
rm -rf /usr/pkg/share/examples/sysmanage
rm -rf /var/lib/sysmanage
rm -rf /var/log/sysmanage
rm /etc/rc.d/sysmanage

# Remove nginx configuration (if you installed it)
rm /usr/pkg/etc/nginx/sites-enabled/sysmanage-nginx.conf
/etc/rc.d/nginx restart

# Optionally remove database
su - pgsql -c "dropdb sysmanage"
su - pgsql -c "dropuser sysmanage"
```

## Package Dependencies

The NetBSD package automatically declares dependencies on:

- **python312** - Python 3.12 interpreter
- **py312-pip** - Python package installer
- **postgresql16-server** - PostgreSQL 16 database server
- **nginx** - Web server for reverse proxy

These will be installed automatically by `pkg_add` if not already present.

## Troubleshooting

### Service won't start

```bash
# Check logs for errors
tail -50 /var/log/sysmanage/server-error.log

# Verify configuration
cat /usr/pkg/etc/sysmanage.yaml

# Check database connectivity
su - pgsql -c "psql -U sysmanage -d sysmanage -c 'SELECT 1'"

# Verify Python environment
cd /usr/pkg/lib/sysmanage
.venv/bin/python --version
.venv/bin/pip list
```

### Port conflicts

If port 8080 is already in use:

```bash
# Edit rc.d script to change port
vi /etc/rc.d/sysmanage

# Or edit the configuration
vi /usr/pkg/etc/sysmanage.yaml

# Then restart service
/etc/rc.d/sysmanage restart
```

### Python dependency issues

```bash
# Rebuild virtual environment
cd /usr/pkg/lib/sysmanage
rm -rf .venv
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Database connection issues

```bash
# Verify PostgreSQL is running
/etc/rc.d/pgsql status

# Check PostgreSQL logs
tail -50 /var/pgsql/data/pg_log/postgresql-*.log

# Test connection manually
su - pgsql -c "psql -l"

# Verify pg_hba.conf allows local connections
cat /var/pgsql/data/pg_hba.conf | grep -v '^#' | grep -v '^$'
```

### Permission issues

```bash
# Ensure proper ownership of files
cd /usr/pkg/lib/sysmanage
ls -la

# Fix permissions if needed
chown -R root:wheel /usr/pkg/lib/sysmanage
chmod -R 755 /usr/pkg/lib/sysmanage

# Ensure log directory is writable
chown -R sysmanage:sysmanage /var/log/sysmanage
chmod 755 /var/log/sysmanage
```

## Documentation

- **Main Documentation**: https://sysmanage.org/docs
- **Server Setup Guide**: https://sysmanage.org/docs/server/installation
- **Configuration Reference**: https://sysmanage.org/docs/server/configuration

## Support

- **Issues**: https://github.com/bceverly/sysmanage/issues
