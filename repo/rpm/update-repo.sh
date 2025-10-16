#!/bin/bash
# update-repo.sh - Add or update RPM packages in the repository
# Usage: ./update-repo.sh /path/to/package.rpm <target>
#   target: el8, el9, or fedora/39

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 /path/to/package.rpm <target>"
    echo ""
    echo "Targets:"
    echo "  el8       - RHEL 8, Rocky 8, AlmaLinux 8"
    echo "  el9       - RHEL 9, Rocky 9, AlmaLinux 9, CentOS Stream 9"
    echo "  fedora/39 - Fedora 39+"
    echo ""
    echo "Example:"
    echo "  $0 /tmp/sysmanage-agent-1.0.0.el9.x86_64.rpm el9"
    exit 1
fi

RPM_FILE="$1"
TARGET="$2"

# Validate inputs
if [ ! -f "$RPM_FILE" ]; then
    echo "ERROR: RPM file not found: $RPM_FILE"
    exit 1
fi

if [[ ! "$RPM_FILE" =~ \.rpm$ ]]; then
    echo "ERROR: File must have .rpm extension"
    exit 1
fi

# Set target directory
case "$TARGET" in
    el8)
        TARGET_DIR="el8/x86_64"
        ;;
    el9)
        TARGET_DIR="el9/x86_64"
        ;;
    fedora/39)
        TARGET_DIR="fedora/39/x86_64"
        ;;
    *)
        echo "ERROR: Invalid target: $TARGET"
        echo "Valid targets: el8, el9, fedora/39"
        exit 1
        ;;
esac

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="$REPO_DIR/$TARGET_DIR"

# Check if createrepo_c is installed
if ! command -v createrepo_c &> /dev/null; then
    echo "ERROR: createrepo_c is not installed"
    echo "Install with: sudo dnf install createrepo_c"
    exit 1
fi

# Create directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Copy the RPM
RPM_BASENAME=$(basename "$RPM_FILE")
echo "Copying $RPM_BASENAME to $TARGET_DIR/"
cp "$RPM_FILE" "$DEST_DIR/"

# Generate repository metadata
echo "Generating repository metadata..."
cd "$DEST_DIR"
createrepo_c .

echo ""
echo "=========================================="
echo "Repository updated successfully!"
echo "=========================================="
echo ""
echo "Package: $RPM_BASENAME"
echo "Target:  $TARGET_DIR"
echo ""
echo "Next steps:"
echo "  1. Test the repository:"
echo "     curl https://bceverly.github.io/sysmanage-docs/repo/rpm/$TARGET_DIR/repodata/repomd.xml"
echo ""
echo "  2. Commit and push the changes:"
echo "     cd $REPO_DIR"
echo "     git add $TARGET_DIR/"
echo "     git commit -m \"Add $RPM_BASENAME to $TARGET repository\""
echo "     git push"
echo ""
