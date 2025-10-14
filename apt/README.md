# SysManage Agent APT Repository

This directory contains a Debian APT repository for distributing SysManage Agent packages.

## Repository Structure

The repository uses **version-based organization** for clean management of multiple package versions:

```
apt/
├── dists/
│   └── stable/
│       ├── Release                          # Repository metadata
│       └── main/
│           └── binary-amd64/
│               ├── Packages                  # Package index (auto-generated)
│               └── Packages.gz              # Compressed package index (auto-generated)
└── pool/
    └── main/
        ├── 0.9.0-1/                         # Version-specific directory
        │   └── sysmanage-agent_0.9.0-1_all.deb
        ├── 0.10.0-1/                        # Next version
        │   └── sysmanage-agent_0.10.0-1_all.deb
        └── ...                               # Additional versions
```

**Organization Benefits**:
- Each version in its own subdirectory
- Easy to track package history
- Clean separation between versions
- Automatic version detection from filename

## Adding the Repository (For Users)

Users can add this repository to their system with:

```bash
# Add the repository
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage.list

# Update package lists
sudo apt update

# Install sysmanage-agent
sudo apt install sysmanage-agent

# Or install a specific version
sudo apt install sysmanage-agent=0.9.0-1
```

**Note**: The `[trusted=yes]` option is used because we're not signing packages with GPG for the initial release. For production use, you should set up GPG signing.

## Accessing via GitHub Pages

This repository is served via GitHub Pages at:
- **Base URL**: `https://bceverly.github.io/sysmanage-docs/apt`
- **Repository URL**: `https://bceverly.github.io/sysmanage-docs/apt stable main`

## Updating the Repository (For Maintainers)

### Using the Helper Script (Recommended)

The `update-repo.sh` script automatically handles version-based organization:

```bash
cd ~/dev/sysmanage-docs/apt

# Add a new package (version is auto-detected from filename)
./update-repo.sh /path/to/sysmanage-agent_1.0.0-1_all.deb

# The script will:
# 1. Extract version from filename (e.g., "1.0.0-1")
# 2. Create pool/main/1.0.0-1/ directory
# 3. Copy the .deb file there
# 4. Regenerate package indexes
# 5. Update Release file
```

Then commit and push:
```bash
cd ~/dev/sysmanage-docs
git add apt/
git commit -m "Add sysmanage-agent version 1.0.0"
git push
```

### Manual Update Process

If you prefer to update manually:

1. **Create version directory and add package**:
   ```bash
   VERSION="1.0.0-1"
   mkdir -p apt/pool/main/$VERSION
   cp sysmanage-agent_${VERSION}_all.deb apt/pool/main/$VERSION/
   ```

2. **Generate package index**:
   ```bash
   cd apt
   dpkg-scanpackages pool/main /dev/null > dists/stable/main/binary-amd64/Packages
   gzip -k -f dists/stable/main/binary-amd64/Packages
   ```

3. **Update Release file**:
   ```bash
   cd dists/stable
   apt-ftparchive release . > Release
   cd ../..
   ```

4. **Commit and push** to GitHub:
   ```bash
   cd ~/dev/sysmanage-docs
   git add apt/
   git commit -m "Add sysmanage-agent version $VERSION"
   git push
   ```

5. **Wait for GitHub Pages** to update (usually within 2-5 minutes)

## Testing the Repository

After updating:

```bash
# On a test system
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage.list
sudo apt update

# Check available versions
apt-cache policy sysmanage-agent

# Should show something like:
#   sysmanage-agent:
#     Installed: (none)
#     Candidate: 1.0.0-1
#     Version table:
#        1.0.0-1 500
#        0.9.0-1 500

# Install specific version
sudo apt install sysmanage-agent=0.9.0-1

# Or install latest
sudo apt install sysmanage-agent
```

## Version Management

### Listing All Versions

```bash
# Show all available versions in repository
ls -la apt/pool/main/

# Show versions available to users
dpkg-scanpackages apt/pool/main /dev/null | grep -E "^Package:|^Version:"
```

### Removing Old Versions

```bash
# Remove a specific version
rm -rf apt/pool/main/0.8.0-1/

# Then regenerate indexes
cd apt
dpkg-scanpackages pool/main /dev/null > dists/stable/main/binary-amd64/Packages
gzip -k -f dists/stable/main/binary-amd64/Packages
cd dists/stable
apt-ftparchive release . > Release
cd ../..
```

### Version Extraction

The `update-repo.sh` script extracts versions from .deb filenames using this pattern:
- **Format**: `package-name_VERSION_architecture.deb`
- **Example**: `sysmanage-agent_0.9.0-1_all.deb` → Version: `0.9.0-1`

## Automated Updates from GitHub Actions (Future)

The GitHub Actions workflow in `sysmanage-agent` repository will be enhanced to:

1. Build the .deb package on release
2. Download the built package
3. Clone `sysmanage-docs` repository
4. Run `./apt/update-repo.sh` with the new package
5. Commit and push to `sysmanage-docs`
6. Wait for GitHub Pages deployment

This will make releases fully automated!

## Future Enhancements

### GPG Signing (Recommended for Production)

1. **Generate GPG key**:
   ```bash
   gpg --full-generate-key
   ```

2. **Export public key**:
   ```bash
   gpg --armor --export YOUR_EMAIL > apt/public.key
   ```

3. **Sign Release file**:
   ```bash
   gpg --default-key YOUR_EMAIL -abs -o dists/stable/Release.gpg dists/stable/Release
   gpg --default-key YOUR_EMAIL --clearsign -o dists/stable/InRelease dists/stable/Release
   ```

4. **Users import key**:
   ```bash
   curl -s https://bceverly.github.io/sysmanage-docs/apt/public.key | sudo apt-key add -
   # Or for newer Ubuntu/Debian:
   curl -s https://bceverly.github.io/sysmanage-docs/apt/public.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/sysmanage.gpg
   ```

5. **Update sources.list** (remove `[trusted=yes]`):
   ```bash
   echo "deb https://bceverly.github.io/sysmanage-docs/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage.list
   ```

### Multiple Distributions

To support multiple Ubuntu/Debian versions with separate repositories:

```
apt/
├── dists/
│   ├── jammy/      # Ubuntu 22.04
│   ├── noble/      # Ubuntu 24.04
│   ├── bookworm/   # Debian 12
│   └── stable/     # Generic (current setup)
└── pool/
    └── main/
        └── 0.9.0-1/
            └── sysmanage-agent_0.9.0-1_all.deb
```

Since the package is architecture-independent (`_all.deb`), all distributions can share the same pool.

## Maintenance Commands

```bash
# List all packages in the repository
dpkg-scanpackages pool/main /dev/null

# Verify package integrity
dpkg-deb --info apt/pool/main/0.9.0-1/sysmanage-agent_0.9.0-1_all.deb

# Check package dependencies
dpkg-deb --field apt/pool/main/0.9.0-1/sysmanage-agent_0.9.0-1_all.deb Depends

# Get repository statistics
echo "Total packages: $(find apt/pool/main -name '*.deb' | wc -l)"
echo "Total size: $(du -sh apt/pool/main | cut -f1)"
```

## Troubleshooting

### Repository not found (404)
- Verify GitHub Pages is enabled for the repository
- Check that the `apt/` directory is in the `main` branch
- Wait a few minutes after pushing for GitHub Pages to update
- Test the URL in browser: `https://bceverly.github.io/sysmanage-docs/apt/dists/stable/Release`

### Package not installing
- Verify the Packages index is up to date
- Check that the .deb file exists in the version subdirectory
- Run `sudo apt update` to refresh the package list
- Check package path in Packages file: `grep Filename apt/dists/stable/main/binary-amd64/Packages`

### Wrong version installed
- APT installs the highest version number by default
- To install specific version: `sudo apt install sysmanage-agent=0.9.0-1`
- To pin a version, create `/etc/apt/preferences.d/sysmanage-agent`:
  ```
  Package: sysmanage-agent
  Pin: version 0.9.0-1
  Pin-Priority: 1001
  ```

### Repository structure verification
```bash
# Verify all paths are correct
cd ~/dev/sysmanage-docs/apt
dpkg-scanpackages pool/main /dev/null | grep Filename

# Should show paths like:
# Filename: pool/main/0.9.0-1/sysmanage-agent_0.9.0-1_all.deb
```

## Additional Resources

- **Debian Repository Format**: https://wiki.debian.org/DebianRepository/Format
- **GitHub Pages Documentation**: https://docs.github.com/en/pages
- **dpkg-scanpackages**: `man dpkg-scanpackages`
- **apt-ftparchive**: `man apt-ftparchive`

---

*Last Updated: October 14, 2025 (Version-based organization implemented)*
