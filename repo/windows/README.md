# SysManage Windows Repository

This directory contains Windows MSI installer packages for SysManage.

## Available Packages

### SysManage Agent
The agent runs on managed Windows systems and communicates with the server.

- **Repository**: [agent/windows/](../agent/windows/)
- **Documentation**: [Agent Windows Repository Guide](../agent/windows/README.md)
- **Architectures**: x64, ARM64

Download and install:
```powershell
# Download latest installer
Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/agent/windows/packages/sysmanage-agent-latest-x64.msi" -OutFile "sysmanage-agent.msi"

# Install
msiexec /i sysmanage-agent.msi /qn

# Or use the interactive installer
Start-Process sysmanage-agent.msi
```

### SysManage Server (Coming Soon)
The server provides centralized management and web interface.

- **Status**: Planned for future release
- **Platform**: Windows Server 2019+
- **Architecture**: x64

## Repository Structure

```
windows/
├── agent/
│   └── windows/
│       ├── packages/
│       │   ├── VERSION/
│       │   │   ├── sysmanage-agent-VERSION-x64.msi
│       │   │   ├── sysmanage-agent-VERSION-arm64.msi
│       │   │   └── checksums.txt
│       │   └── latest/ (symlinks)
│       ├── index.json
│       └── README.md
└── server/ (planned)
```

## Installation Methods

### Method 1: Direct Download
Download the MSI installer directly from the repository and run it.

### Method 2: PowerShell Script
```powershell
# Download and install in one command
$url = "https://bceverly.github.io/sysmanage-docs/repo/agent/windows/packages/sysmanage-agent-latest-x64.msi"
$output = "$env:TEMP\sysmanage-agent.msi"
Invoke-WebRequest -Uri $url -OutFile $output
Start-Process msiexec.exe -ArgumentList "/i `"$output`" /qn" -Wait
Remove-Item $output
```

### Method 3: Chocolatey (Future)
Package submission to Chocolatey is planned for easier installation.

## Verification

All packages include SHA256 checksums for verification:

```powershell
# Download checksum file
$checksumUrl = "https://bceverly.github.io/sysmanage-docs/repo/agent/windows/packages/VERSION/checksums.txt"
$checksumFile = "checksums.txt"
Invoke-WebRequest -Uri $checksumUrl -OutFile $checksumFile

# Verify downloaded MSI
$actualHash = (Get-FileHash sysmanage-agent.msi -Algorithm SHA256).Hash
$expectedHash = (Get-Content checksums.txt | Select-String "sysmanage-agent.*x64.msi" | ForEach-Object { ($_ -split '\s+')[0] })
if ($actualHash -eq $expectedHash) {
    Write-Host "✓ Checksum verified"
} else {
    Write-Host "✗ Checksum mismatch!"
}
```

## Code Signing

All Windows installers are digitally signed using:
- **Certificate Authority**: SignPath Foundation
- **Certificate Type**: EV Code Signing
- **Signing Service**: SignPath.io

You can verify the signature by:
1. Right-clicking the .msi file
2. Selecting "Properties"
3. Navigating to the "Digital Signatures" tab

## Support

- **Documentation**: https://sysmanage.org/docs
- **Issues**: https://github.com/bceverly/sysmanage/issues
- **Agent Issues**: https://github.com/bceverly/sysmanage-agent/issues

## System Requirements

### Agent
- **OS**: Windows 10, Windows 11, Windows Server 2016+
- **Architecture**: x64 or ARM64
- **.NET**: Framework 4.8 or .NET 6+ (included in installer)
- **Disk Space**: 50 MB
- **Memory**: 256 MB

### Server (When Available)
- **OS**: Windows Server 2019+
- **Architecture**: x64
- **Database**: PostgreSQL 12+ (separate installation)
- **Web Server**: IIS 10+ or nginx
- **Disk Space**: 500 MB
- **Memory**: 2 GB
