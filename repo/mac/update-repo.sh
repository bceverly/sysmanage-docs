#!/bin/bash
# Helper script to update the macOS repository after adding a new package
# Usage: ./update-repo.sh [path-to-pkg-file]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "====================================="
echo "SysManage macOS Repository Updater"
echo "====================================="
echo ""

# Check if a .pkg file was provided
if [ $# -eq 1 ]; then
    PKG_FILE="$1"
    if [ ! -f "$PKG_FILE" ]; then
        echo "Error: File not found: $PKG_FILE"
        exit 1
    fi

    echo "📦 Adding package: $PKG_FILE"

    # Extract package name and version from .pkg filename
    # Format: sysmanage-agent-version-macos.pkg
    BASENAME=$(basename "$PKG_FILE")

    # Extract version (between first - after sysmanage-agent- and -macos.pkg)
    VERSION=$(echo "$BASENAME" | sed 's/^sysmanage-agent-\(.*\)-macos\.pkg$/\1/')

    if [ -z "$VERSION" ] || [ "$VERSION" = "$BASENAME" ]; then
        echo "Error: Could not extract version from filename: $BASENAME"
        exit 1
    fi

    echo "   Version detected: $VERSION"

    # Create version-specific directory
    VERSION_DIR="packages/$VERSION"
    mkdir -p "$VERSION_DIR"

    # Copy to version-specific packages directory
    cp "$PKG_FILE" "$VERSION_DIR/"
    echo "✓ Copied to $VERSION_DIR/"

    # Copy checksums if they exist
    if [ -f "$PKG_FILE.sha256" ]; then
        cp "$PKG_FILE.sha256" "$VERSION_DIR/"
        echo "✓ Copied checksum file"
    fi
fi

# Generate package index (JSON format for easy parsing)
echo ""
echo "📝 Generating package index..."

# Create index.json with all available packages
INDEX_FILE="index.json"
echo "{" > "$INDEX_FILE"
echo '  "repository": "sysmanage-agent-macos",' >> "$INDEX_FILE"
echo '  "updated": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",' >> "$INDEX_FILE"
echo '  "packages": [' >> "$INDEX_FILE"

FIRST=1
for PKG in $(find packages -name "*.pkg" | sort -V -r); do
    if [ $FIRST -eq 0 ]; then
        echo "    }," >> "$INDEX_FILE"
    fi
    FIRST=0

    BASENAME=$(basename "$PKG")
    VERSION=$(echo "$BASENAME" | sed 's/^sysmanage-agent-\(.*\)-macos\.pkg$/\1/')
    SIZE=$(stat -f%z "$PKG" 2>/dev/null || stat -c%s "$PKG" 2>/dev/null)
    CHECKSUM=""

    if [ -f "$PKG.sha256" ]; then
        CHECKSUM=$(cat "$PKG.sha256" | awk '{print $1}')
    fi

    echo "    {" >> "$INDEX_FILE"
    echo '      "version": "'$VERSION'",' >> "$INDEX_FILE"
    echo '      "filename": "'$BASENAME'",' >> "$INDEX_FILE"
    echo '      "path": "'$PKG'",' >> "$INDEX_FILE"
    echo '      "size": '$SIZE',' >> "$INDEX_FILE"
    if [ -n "$CHECKSUM" ]; then
        echo '      "sha256": "'$CHECKSUM'",' >> "$INDEX_FILE"
    fi
    echo '      "url": "https://bceverly.github.io/sysmanage-docs/repo/mac/'$PKG'"' >> "$INDEX_FILE"
done

if [ $FIRST -eq 0 ]; then
    echo "    }" >> "$INDEX_FILE"
fi

echo "  ]" >> "$INDEX_FILE"
echo "}" >> "$INDEX_FILE"

echo "✓ Created index.json"

# Create latest.txt for quick version check
if [ $FIRST -eq 0 ]; then
    LATEST_VERSION=$(find packages -name "*.pkg" | sort -V -r | head -1 | xargs basename | sed 's/^sysmanage-agent-\(.*\)-macos\.pkg$/\1/')
    echo "$LATEST_VERSION" > latest.txt
    echo "✓ Created latest.txt (version: $LATEST_VERSION)"
fi

# List packages in repository
echo ""
echo "====================================="
echo "Packages in repository:"
echo "====================================="
find packages -name "*.pkg" | sort -V -r | while read pkg; do
    BASENAME=$(basename "$pkg")
    VERSION=$(echo "$BASENAME" | sed 's/^sysmanage-agent-\(.*\)-macos\.pkg$/\1/')
    SIZE=$(du -h "$pkg" | cut -f1)
    echo "  • sysmanage-agent $VERSION ($SIZE)"
done

echo ""
echo "====================================="
echo "✓ Repository updated successfully!"
echo "====================================="
echo ""
echo "Next steps:"
echo "  1. Commit and push the changes:"
echo "     git add repo/mac/"
echo "     git commit -m 'Update macOS repository'"
echo "     git push"
echo ""
echo "  2. Wait for GitHub Pages to update (usually a few minutes)"
echo ""
echo "  3. Test the installation:"
echo "     curl -O https://bceverly.github.io/sysmanage-docs/repo/mac/packages/$VERSION/sysmanage-agent-$VERSION-macos.pkg"
echo "     sudo installer -pkg sysmanage-agent-$VERSION-macos.pkg -target /"
echo ""
