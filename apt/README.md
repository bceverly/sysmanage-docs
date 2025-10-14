# SysManage Agent APT Repository

This directory contains a Debian APT repository for distributing SysManage Agent packages.

## Repository Structure

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
        └── sysmanage-agent_X.Y.Z-1_all.deb  # Package files
```

## Adding the Repository (For Users)

Users can add this repository to their system with:

```bash
# Add the repository
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage.list

# Update package lists
sudo apt update

# Install sysmanage-agent
sudo apt install sysmanage-agent
```

**Note**: The `[trusted=yes]` option is used because we're not signing packages with GPG for the initial release. For production use, you should set up GPG signing.

## Accessing via GitHub Pages

This repository is served via GitHub Pages at:
- **Base URL**: `https://bceverly.github.io/sysmanage-docs/apt`
- **Repository URL**: `https://bceverly.github.io/sysmanage-docs/apt stable main`

## Updating the Repository (For Maintainers)

### Manual Update Process

1. **Add new .deb package** to `apt/pool/main/`:
   ```bash
   cp sysmanage-agent_1.0.0-1_all.deb apt/pool/main/
   ```

2. **Generate package index**:
   ```bash
   cd apt
   dpkg-scanpackages pool/main /dev/null > dists/stable/main/binary-amd64/Packages
   gzip -k -f dists/stable/main/binary-amd64/Packages
   ```

3. **Update Release file** (optional, for verification):
   ```bash
   cd dists/stable
   apt-ftparchive release . > Release
   ```

4. **Commit and push** to GitHub:
   ```bash
   git add apt/
   git commit -m "Add sysmanage-agent version 1.0.0"
   git push
   ```

5. **Wait for GitHub Pages** to update (usually within a few minutes)

### Automated Update (TODO)

The GitHub Actions workflow in sysmanage-agent will automatically:
1. Build the .deb package
2. Copy it to this repository
3. Regenerate the package index
4. Create a commit and push to main branch

## Testing the Repository

After updating:

```bash
# On a test system
echo "deb [trusted=yes] https://bceverly.github.io/sysmanage-docs/apt stable main" | sudo tee /etc/apt/sources.list.d/sysmanage.list
sudo apt update
apt-cache policy sysmanage-agent
```

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

### Multiple Distributions

To support multiple Ubuntu/Debian versions:

```
apt/
├── dists/
│   ├── jammy/    # Ubuntu 22.04
│   ├── noble/    # Ubuntu 24.04
│   └── bookworm/ # Debian 12
```

## Maintenance Commands

```bash
# List all packages in the repository
dpkg-scanpackages pool/main /dev/null

# Remove old package versions
rm apt/pool/main/sysmanage-agent_0.9.0-1_all.deb

# Verify package integrity
dpkg-deb --info apt/pool/main/sysmanage-agent_*.deb
```

## Troubleshooting

### Repository not found
- Verify GitHub Pages is enabled for the repository
- Check that the `apt/` directory is in the `main` branch
- Wait a few minutes after pushing for GitHub Pages to update

### Package not installing
- Verify the Packages index is up to date
- Check that the .deb file exists in `pool/main/`
- Run `sudo apt update` to refresh the package list
