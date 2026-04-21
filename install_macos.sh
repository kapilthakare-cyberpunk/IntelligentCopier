#!/bin/bash
# Install script for macOS

set -e

echo "🍎 Intelligent File Copier - macOS Installer"
echo "============================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.7 or higher from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.7"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $PYTHON_VERSION found, but 3.7+ required"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check rsync
echo "Checking rsync..."
if ! command -v rsync &> /dev/null; then
    echo "❌ rsync not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install rsync
    else
        echo "Please install Homebrew first: https://brew.sh"
        exit 1
    fi
else
    echo "✅ rsync found"
fi

# Create app bundle
echo ""
echo "Creating application bundle..."

APP_NAME="Intelligent Copier"
APP_DIR="$HOME/Applications/${APP_NAME}.app"

# Remove old version if exists
if [ -d "$APP_DIR" ]; then
    echo "Removing old version..."
    rm -rf "$APP_DIR"
fi

# Create directory structure
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Copy executable
cp "src/intelligent_copier.py" "$APP_DIR/Contents/MacOS/"

# Create launcher script
cat > "$APP_DIR/Contents/MacOS/${APP_NAME}" << 'EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
python3 intelligent_copier.py
EOF

chmod +x "$APP_DIR/Contents/MacOS/${APP_NAME}"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>English</string>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.kapil.intelligentcopier</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
EOF

echo "✅ Application bundle created: $APP_DIR"

# Create symlink in Desktop
echo ""
echo "Creating Desktop shortcut..."
DESKTOP_LINK="$HOME/Desktop/Intelligent Copier.app"
if [ -L "$DESKTOP_LINK" ]; then
    rm "$DESKTOP_LINK"
fi
ln -s "$APP_DIR" "$DESKTOP_LINK"
echo "✅ Desktop shortcut created"

echo ""
echo "============================================"
echo "🎉 Installation complete!"
echo ""
echo "Launch from:"
echo "  • Applications folder: $APP_DIR"
echo "  • Desktop: $DESKTOP_LINK"
echo "  • Terminal: python3 src/intelligent_copier.py"
echo ""
echo "Note: On first launch, you may need to:"
echo "  Right-click → Open to bypass Gatekeeper"
echo "============================================"
