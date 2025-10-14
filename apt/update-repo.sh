#!/bin/bash
# Helper script to update the APT repository after adding a new package
# Usage: ./update-repo.sh [path-to-deb-file]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "====================================="
echo "SysManage APT Repository Updater"
echo "====================================="
echo ""

# Check if a .deb file was provided
if [ $# -eq 1 ]; then
    DEB_FILE="$1"
    if [ ! -f "$DEB_FILE" ]; then
        echo "Error: File not found: $DEB_FILE"
        exit 1
    fi

    echo "📦 Adding package: $DEB_FILE"

    # Extract package name and version from .deb filename
    # Format: package-name_version-revision_arch.deb
    BASENAME=$(basename "$DEB_FILE")

    # Extract version (everything between first _ and last _)
    VERSION=$(echo "$BASENAME" | sed 's/^[^_]*_\([^_]*\)_.*$/\1/')

    if [ -z "$VERSION" ]; then
        echo "Error: Could not extract version from filename: $BASENAME"
        exit 1
    fi

    echo "   Version detected: $VERSION"

    # Create version-specific directory
    VERSION_DIR="pool/main/$VERSION"
    mkdir -p "$VERSION_DIR"

    # Copy to version-specific pool directory
    cp "$DEB_FILE" "$VERSION_DIR/"
    echo "✓ Copied to $VERSION_DIR/"
fi

# Generate package index
echo ""
echo "📝 Generating package index..."
dpkg-scanpackages pool/main /dev/null > dists/stable/main/binary-amd64/Packages
echo "✓ Created Packages file"

# Compress package index
echo ""
echo "🗜️  Compressing package index..."
gzip -k -f dists/stable/main/binary-amd64/Packages
echo "✓ Created Packages.gz"

# Update Release file
echo ""
echo "📄 Updating Release file..."
cd dists/stable
apt-ftparchive release . > Release
cd ../..
echo "✓ Updated Release file"

# List packages in repository
echo ""
echo "====================================="
echo "Packages in repository:"
echo "====================================="
dpkg-scanpackages pool/main /dev/null | grep -E "^Package:|^Version:" | sed 's/^Package: /  • /' | sed 's/^Version: /    Version: /'

echo ""
echo "====================================="
echo "✓ Repository updated successfully!"
echo "====================================="
echo ""
echo "Next steps:"
echo "  1. Commit and push the changes:"
echo "     git add apt/"
echo "     git commit -m 'Update APT repository'"
echo "     git push"
echo ""
echo "  2. Wait for GitHub Pages to update (usually a few minutes)"
echo ""
echo "  3. Test the installation:"
echo "     sudo apt update"
echo "     apt-cache policy sysmanage-agent"
echo ""
