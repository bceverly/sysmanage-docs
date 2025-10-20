# Download Page Requirements for SignPath

## Overview

SignPath Foundation requires that signed software be available for public download with clear signing information displayed. This document outlines how SysManage Agent meets these requirements.

## Current Download Locations

### Primary Download Pages

1. **GitHub Releases** (Primary)
   - URL: https://github.com/bceverly/sysmanage-agent/releases
   - Purpose: Official release distribution
   - Format: MSI installers for x64 and ARM64

2. **Documentation Site** (Secondary)
   - URL: https://bceverly.github.io/sysmanage-docs/repo/windows/
   - Purpose: Package repository with installation instructions
   - Format: Direct links to MSI files with checksums

3. **Agent Installation Guide** (Tertiary)
   - URL: https://bceverly.github.io/sysmanage-docs/docs/agent/installation.html
   - Purpose: Comprehensive installation documentation
   - Format: Instructions with download links

## SignPath Requirements Compliance

### ✅ Requirement 1: Public Download Page

**Status**: COMPLIANT

The SysManage Agent has multiple public download pages:
- GitHub Releases (primary distribution channel)
- GitHub Pages repository (secondary with README)
- Documentation site (installation guide)

All pages are:
- Publicly accessible (no login required)
- Free to download
- Include installation instructions
- Provide SHA256 checksums for verification

### 📝 Requirement 2: Signing Information Display

**Status**: PENDING (After SignPath Approval)

Once SignPath approves the application and issues a certificate, the following information must be added to all download pages:

#### Required Signing Information

```markdown
## Code Signing Information

This software is digitally signed to verify its authenticity and integrity.

**Certificate Details:**
- **Issuer**: SignPath Foundation
- **Subject**: SysManage
- **Valid From**: [Issue Date]
- **Valid Until**: [Expiration Date]
- **Signature Algorithm**: SHA256 with RSA
- **Timestamp Authority**: SignPath Foundation

**Verification Steps:**
1. Right-click the downloaded MSI file
2. Select "Properties"
3. Navigate to the "Digital Signatures" tab
4. Select the signature and click "Details"
5. Verify the certificate matches the information above
```

## Implementation Plan

### Phase 1: GitHub Releases (Automated)

**File**: `.github/workflows/build-and-release.yml`

Add to release notes template:

```yaml
## 🔒 Code Signing

This release is digitally signed with a certificate from SignPath Foundation.

**Certificate Information:**
- Issuer: SignPath Foundation
- Subject: SysManage
- Algorithm: SHA256 with RSA

**Verification:**
```powershell
# Verify the digital signature
Get-AuthenticodeSignature sysmanage-agent-$VERSION-windows-x64.msi | Select-Object Status, SignerCertificate
```

**Expected Output:**
- Status: Valid
- Signer: CN=SysManage
```

### Phase 2: Documentation Site

**File**: `C:\Users\bceverly\dev\sysmanage-docs\repo\windows\README.md`

Add new section after "Quick Installation":

```markdown
## 🔒 Code Signing & Verification

All SysManage Agent MSI packages are digitally signed with a certificate from SignPath Foundation to ensure authenticity and integrity.

### Certificate Details

- **Certificate Authority**: SignPath Foundation
- **Certificate Subject**: SysManage
- **Algorithm**: SHA256 with RSA
- **Timestamp Server**: SignPath Foundation

### Verify Digital Signature (GUI)

1. Download the MSI installer
2. Right-click the file and select **Properties**
3. Go to the **Digital Signatures** tab
4. Select the signature and click **Details**
5. Verify:
   - Issuer: SignPath Foundation
   - Subject: SysManage
   - Status: "This digital signature is OK"

### Verify Digital Signature (PowerShell)

```powershell
# Download and verify signature
$VERSION = (Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/windows/latest.txt").Content.Trim()
$ARCH = "x64"
Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/windows/packages/$VERSION/sysmanage-agent-$VERSION-windows-$ARCH.msi" -OutFile "sysmanage-agent-$VERSION-windows-$ARCH.msi"

# Check signature
$sig = Get-AuthenticodeSignature "sysmanage-agent-$VERSION-windows-$ARCH.msi"
Write-Host "Signature Status: $($sig.Status)"
Write-Host "Signer: $($sig.SignerCertificate.Subject)"
Write-Host "Issuer: $($sig.SignerCertificate.Issuer)"

# Expected output:
# Signature Status: Valid
# Signer: CN=SysManage
# Issuer: CN=SignPath Foundation
```

### Verify SHA256 Checksum

In addition to signature verification, always verify the SHA256 checksum:

```powershell
# Download checksum file
Invoke-WebRequest -Uri "https://bceverly.github.io/sysmanage-docs/repo/windows/packages/$VERSION/sysmanage-agent-$VERSION-windows-$ARCH.msi.sha256" -OutFile "sysmanage-agent-$VERSION-windows-$ARCH.msi.sha256"

# Verify
$expectedHash = (Get-Content "sysmanage-agent-$VERSION-windows-$ARCH.msi.sha256").Split()[0]
$actualHash = (Get-FileHash "sysmanage-agent-$VERSION-windows-$ARCH.msi" -Algorithm SHA256).Hash.ToLower()

if ($expectedHash -eq $actualHash) {
    Write-Host "✓ Checksum verified!" -ForegroundColor Green
} else {
    Write-Host "✗ Checksum mismatch! Do not install." -ForegroundColor Red
}
```

### Security Best Practices

1. **Always verify signatures** before installing
2. **Check checksums** in addition to signatures
3. **Download only from official sources**:
   - GitHub Releases: https://github.com/bceverly/sysmanage-agent/releases
   - GitHub Pages: https://bceverly.github.io/sysmanage-docs/repo/windows/
4. **Report suspicious packages** to security@sysmanage.example.com
```

### Phase 3: Installation Guide

**File**: `C:\Users\bceverly\dev\sysmanage-docs\docs\agent\installation.html`

Add to Windows MSI section (after "Quick Installation"):

```html
<div class="security-verification">
    <h4>🔒 Digital Signature Verification</h4>
    <p>All Windows MSI installers are digitally signed with a certificate from SignPath Foundation.</p>

    <h5>Verify Signature (PowerShell)</h5>
    <pre><code>$sig = Get-AuthenticodeSignature "sysmanage-agent-$VERSION-windows-$ARCH.msi"
Write-Host "Status: $($sig.Status)"
Write-Host "Signer: $($sig.SignerCertificate.Subject)"

# Expected: Status=Valid, Signer=CN=SysManage</code></pre>

    <p><strong>Certificate Information:</strong></p>
    <ul>
        <li><strong>Issuer:</strong> SignPath Foundation</li>
        <li><strong>Subject:</strong> SysManage</li>
        <li><strong>Algorithm:</strong> SHA256 with RSA</li>
    </ul>
</div>
```

## SignPath Foundation Terms Compliance

### Display Requirements

According to SignPath Foundation Terms of Use, Section 4.2, the download page must:

✅ **Be publicly accessible**: All download pages are public, no authentication required

✅ **Display signing information**: Will be added after certificate issuance (see templates above)

✅ **Show certificate issuer**: "SignPath Foundation" will be prominently displayed

✅ **Include verification instructions**: Detailed PowerShell and GUI verification steps provided

✅ **Link to certificate information**: Certificate details will be linked and displayed

## Verification Checklist

Before submitting to SignPath, verify:

- [ ] Download pages are publicly accessible
- [ ] MSI files can be downloaded without authentication
- [ ] SHA256 checksums are provided
- [ ] Installation instructions are clear and comprehensive
- [ ] Links are working and not broken

After SignPath approval:

- [ ] Add certificate information to all download pages
- [ ] Update GitHub Actions to sign releases
- [ ] Add verification instructions to documentation
- [ ] Test signature verification on clean Windows installation
- [ ] Update all language translations with signing information

## Reference Links

- GitHub Releases: https://github.com/bceverly/sysmanage-agent/releases
- Windows Repository: https://bceverly.github.io/sysmanage-docs/repo/windows/
- Installation Guide: https://bceverly.github.io/sysmanage-docs/docs/agent/installation.html
- SignPath Foundation Terms: https://about.signpath.io/code-signing/terms-of-use

## Notes

- Certificate information should be added **immediately** after SignPath approval
- Keep certificate expiration dates updated annually
- Maintain audit trail of all signed releases
- Report any signing issues to SignPath support promptly
