# SysManage Server - Windows MSI Packages

Official Windows MSI installer packages for SysManage Server.

## System Requirements

- **Operating System**: Windows 10 (1809+) or Windows Server 2019+
- **Architecture**: x64 or ARM64
- **Prerequisites**: Administrator privileges (for installation)
- **Database**: PostgreSQL 12+ (recommended) or SQLite
- **Python**: 3.12 (automatically installed by the MSI if not present)
- **Visual C++ Redistributable**: Automatically installed by the MSI if not present

## Installation

### Download

Download the MSI package for your architecture from the latest release:

- **x64 (64-bit Intel/AMD)**: `sysmanage-{VERSION}-windows-x64.msi`
- **ARM64 (64-bit ARM)**: `sysmanage-{VERSION}-windows-arm64.msi`

SHA256 checksum files are provided for verification.

### Install

#### Option 1: Graphical Installation

1. Double-click the downloaded MSI file
2. Follow the installation wizard
3. The installer will automatically:
   - Check for and install Python 3.12 if needed
   - Install Visual C++ Redistributable if needed
   - Extract application files to `C:\Program Files\SysManage Server`
   - Create a Python virtual environment
   - Install all dependencies
   - Create a Windows Service named "SysManageServer"
   - Start the service

#### Option 2: Command Line (Silent)

```powershell
# Run as Administrator
msiexec /i sysmanage-{VERSION}-windows-x64.msi /quiet /qn /norestart
```

### Configuration

After installation, configure the server:

1. Edit the configuration file:
   ```powershell
   notepad "C:\ProgramData\SysManage\sysmanage.yaml"
   ```

2. Update the database connection string and other settings

3. Restart the service:
   ```powershell
   Restart-Service SysManageServer
   ```

### Service Management

The installer creates a Windows Service named "SysManageServer" that runs automatically.

**Start the service:**
```powershell
Start-Service SysManageServer
```

**Stop the service:**
```powershell
Stop-Service SysManageServer
```

**Check service status:**
```powershell
Get-Service SysManageServer
```

**View service logs:**
```powershell
Get-Content "C:\ProgramData\SysManage\logs\sysmanage-service.log" -Tail 50
```

## File Locations

- **Application**: `C:\Program Files\SysManage Server\`
- **Configuration**: `C:\ProgramData\SysManage\sysmanage.yaml`
- **Logs**: `C:\ProgramData\SysManage\logs\`
- **Database** (if using SQLite): `C:\ProgramData\SysManage\db\`
- **Virtual Environment**: `C:\Program Files\SysManage Server\.venv\`

## Upgrade

To upgrade an existing installation:

1. Download the new MSI package
2. Run the installer (it will automatically uninstall the old version first)
3. The configuration file and data will be preserved

```powershell
msiexec /i sysmanage-{NEW_VERSION}-windows-x64.msi
```

## Uninstall

### Option 1: Control Panel

1. Open "Settings" > "Apps" > "Apps & features"
2. Find "SysManage Server" in the list
3. Click "Uninstall"

### Option 2: Command Line

```powershell
# Run as Administrator
msiexec /x sysmanage-{VERSION}-windows-x64.msi
```

The uninstaller will:
- Stop and remove the Windows Service
- Remove application files from `C:\Program Files\SysManage Server`
- Preserve configuration and data in `C:\ProgramData\SysManage` (manual deletion required)

## Troubleshooting

### Service won't start

1. Check the service logs:
   ```powershell
   Get-Content "C:\ProgramData\SysManage\logs\sysmanage-service.log"
   ```

2. Verify Python installation:
   ```powershell
   & "C:\Program Files\SysManage Server\.venv\Scripts\python.exe" --version
   ```

3. Check configuration file syntax:
   ```powershell
   notepad "C:\ProgramData\SysManage\sysmanage.yaml"
   ```

### Database connection errors

Ensure PostgreSQL is installed and running, and that the connection string in `sysmanage.yaml` is correct:

```yaml
database:
  url: "postgresql://sysmanage:password@localhost/sysmanage"
```

### Port conflicts

If port 8080 is already in use, edit the configuration:

```yaml
server:
  host: "0.0.0.0"
  port: 8080  # Change to another port
```

Then restart the service.

### Firewall

If you need to access SysManage from other machines, create a firewall rule:

```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "SysManage Server" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

## Architecture Notes

### x64 (Intel/AMD)
- Standard 64-bit Windows on Intel or AMD processors
- Most common architecture for Windows servers and workstations

### ARM64
- Windows on ARM devices (Surface Pro X, etc.)
- Uses ARM64 version of NSSM and Python 3.12

## Package Contents

Each MSI includes:
- Backend application (Python/FastAPI)
- Frontend application (pre-built static files)
- Database migration scripts (Alembic)
- NSSM (Non-Sucking Service Manager) for Windows Service creation
- Configuration example file
- Post-install scripts for setup automation
- Software Bill of Materials (SBOM) files

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/bceverly/sysmanage
- Documentation: https://sysmanage.org

## Security

The MSI packages are unsigned by default. When running the installer, Windows may show an "Unknown Publisher" warning. This is expected for unsigned packages.

For production deployments, it's recommended to verify the SHA256 checksum:

```powershell
certutil -hashfile sysmanage-{VERSION}-windows-x64.msi SHA256
```

Compare the output with the `.sha256` file provided with the release.

## License

SysManage Server is licensed under the terms specified in the project repository.
