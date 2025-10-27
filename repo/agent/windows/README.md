# SysManage Agent - Windows Package Repository

This repository hosts Windows installer packages (`.msi`) for the SysManage Agent.

## Quick Installation

Download and install the latest version:

### PowerShell (Windows 10/11)

```powershell
# Download the latest package (x64)
$VERSION = (Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/windows/latest.txt").Content.Trim()
$ARCH = "x64"  # or "arm64" for ARM64 Windows
Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/windows/packages/$VERSION/sysmanage-agent-$VERSION-windows-$ARCH.msi" -OutFile "sysmanage-agent-$VERSION-windows-$ARCH.msi"

# Install the package (requires Administrator)
Start-Process msiexec.exe -ArgumentList "/i sysmanage-agent-$VERSION-windows-$ARCH.msi /qn" -Wait -Verb RunAs

# Configure the agent
notepad C:\ProgramData\SysManage\sysmanage-agent.yaml

# Start the service
Start-Service SysManageAgent
```

## Requirements

- **Windows Version**: Windows 10 (1809) or later, Windows Server 2019 or later
- **Architecture**: x64 or ARM64
- **Python**: 3.9 or later (automatically installed if missing)
- **Visual C++ Redistributable**: 2015-2022 (automatically installed if missing)

## Available Architectures

- **x64**: For Intel/AMD 64-bit systems
- **ARM64**: For ARM64 Windows devices (Surface Pro X, etc.)

## Manual Download

Check the package index for available versions: https://bceverly.github.io/sysmanage-docs/repo/windows/index.json

## Verify Package Integrity

Each package includes a SHA256 checksum file:

```powershell
# Download package and checksum
$VERSION = "0.9.7.2"  # Replace with desired version
$ARCH = "x64"  # or "arm64"
Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/windows/packages/$VERSION/sysmanage-agent-$VERSION-windows-$ARCH.msi" -OutFile "sysmanage-agent-$VERSION-windows-$ARCH.msi"
Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/windows/packages/$VERSION/sysmanage-agent-$VERSION-windows-$ARCH.msi.sha256" -OutFile "sysmanage-agent-$VERSION-windows-$ARCH.msi.sha256"

# Verify checksum
$expectedHash = (Get-Content "sysmanage-agent-$VERSION-windows-$ARCH.msi.sha256").Split()[0]
$actualHash = (Get-FileHash "sysmanage-agent-$VERSION-windows-$ARCH.msi" -Algorithm SHA256).Hash.ToLower()
if ($expectedHash -eq $actualHash) { Write-Host "Checksum verified!" } else { Write-Host "Checksum mismatch!" }
```

## Service Management

The agent runs as a Windows Service using NSSM (Non-Sucking Service Manager) and starts automatically at boot.

### Check Service Status

```powershell
Get-Service SysManageAgent
```

### Start/Stop Service

```powershell
# Start
Start-Service SysManageAgent

# Stop
Stop-Service SysManageAgent

# Restart
Restart-Service SysManageAgent
```

### View Logs

```powershell
# View recent logs
Get-Content C:\ProgramData\SysManage\logs\agent.log -Tail 50

# View service logs
Get-Content C:\ProgramData\SysManage\logs\service-stdout.log -Tail 50
Get-Content C:\ProgramData\SysManage\logs\service-stderr.log -Tail 50
```

## Uninstallation

### Using Control Panel

1. Open **Settings** > **Apps** > **Apps & features**
2. Search for "SysManage Agent"
3. Click **Uninstall**

### Using PowerShell

```powershell
# Get the product code
$productCode = (Get-WmiObject -Class Win32_Product | Where-Object { $_.Name -eq "SysManage Agent" }).IdentifyingNumber

# Uninstall
Start-Process msiexec.exe -ArgumentList "/x $productCode /qn" -Wait -Verb RunAs
```

### Manual Cleanup (if needed)

```powershell
# Stop and remove service
Stop-Service SysManageAgent
sc.exe delete SysManageAgent

# Remove installed files
Remove-Item -Path "C:\Program Files\SysManage Agent" -Recurse -Force

# Remove configuration and data (optional)
Remove-Item -Path "C:\ProgramData\SysManage" -Recurse -Force
```

## Configuration

The agent configuration file is located at `C:\ProgramData\SysManage\sysmanage-agent.yaml`.

An example configuration is provided at `C:\ProgramData\SysManage\sysmanage-agent.yaml.example`.

Key configuration options:

- **server.hostname**: Hostname of your SysManage server
- **server.port**: Server port
- **server.use_https**: Use HTTPS for connections
- **database.path**: SQLite database location
- **logging.level**: Log verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Troubleshooting

### Service won't start

Check the service error log:
```powershell
Get-Content C:\ProgramData\SysManage\logs\service-stderr.log -Tail 50
```

### Installation fails

Check the installation log:
```powershell
Get-Content C:\ProgramData\SysManage\logs\install.log
Get-Content C:\ProgramData\SysManage\logs\install-transcript.log
```

### Python not found

The installer automatically installs Python 3.12 if not present. If issues occur:
```powershell
# Download Python manually from https://www.python.org/downloads/
# Or install using winget:
winget install Python.Python.3.12
```

### Permission issues

Ensure the service is running as SYSTEM:
```powershell
Get-Service SysManageAgent | Select-Object Name, Status, StartType, ServiceName
```

### Database errors

Check database directory permissions:
```powershell
icacls "C:\ProgramData\SysManage\db"
```

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/bceverly/sysmanage-agent/issues
- Documentation: https://bceverly.github.io/sysmanage-docs/

## Package Details

- **Installation Location**: `C:\Program Files\SysManage Agent`
- **Service Manager**: NSSM (Non-Sucking Service Manager)
- **Service Name**: `SysManageAgent`
- **Configuration**: `C:\ProgramData\SysManage\sysmanage-agent.yaml`
- **Database**: `C:\ProgramData\SysManage\db\agent.db`
- **Logs**: `C:\ProgramData\SysManage\logs\`

## Building from Source

See the [sysmanage-agent repository](https://github.com/bceverly/sysmanage-agent) for build instructions.
