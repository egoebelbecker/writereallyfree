#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 1. Setup Directories
BUILD_DIR="build_appimage"
APP_DIR="$BUILD_DIR/WriteReallyFree.AppDir"
rm -rf "$BUILD_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/256x256/apps"

# 2. Build via PyInstaller
echo "Installing pyinstaller if missing..."
.venv/bin/pip install pyinstaller

echo "Running PyInstaller compilation..."
.venv/bin/pyinstaller --clean \
    --name writereallyfree \
    --add-data "web:web" \
    --noconfirm \
    app.py

# Copy pyinstaller output to AppDir
cp -r dist/writereallyfree "$APP_DIR/usr/bin/"

# Bundle system libxcb helper libraries into AppDir so Qt platform plugin (libqxcb.so) works everywhere
echo "Bundling XCB system libraries for Qt..."
TARGET_LIB_DIR="$APP_DIR/usr/bin/writereallyfree/_internal"
if [ ! -d "$TARGET_LIB_DIR" ]; then
    TARGET_LIB_DIR="$APP_DIR/usr/bin/writereallyfree"
fi

for libdir in /usr/lib/x86_64-linux-gnu /usr/lib64 /usr/lib; do
    if [ -d "$libdir" ]; then
        cp -d "$libdir"/libxcb-*.so* "$TARGET_LIB_DIR/" 2>/dev/null || true
        cp -d "$libdir"/libxkbcommon*.so* "$TARGET_LIB_DIR/" 2>/dev/null || true
    fi
done

# 3. Setup Desktop file & Icons
cp "$SCRIPT_DIR/writereallyfree.desktop" "$APP_DIR/"
cp web/icon.png "$APP_DIR/writereallyfree.png"
cp web/icon.png "$APP_DIR/usr/share/icons/hicolor/256x256/apps/writereallyfree.png"

# Create custom AppRun script
cat << 'EOF' > "$APP_DIR/AppRun"
#!/bin/sh
SELF=$(readlink -f "$0")
HERE=$(dirname "$SELF")
exec "$HERE/usr/bin/writereallyfree/writereallyfree" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# 4. Download and run appimagetool
echo "Downloading appimagetool..."
APPIMAGE_TOOL="$BUILD_DIR/appimagetool-x86_64.AppImage"
curl -L -o "$APPIMAGE_TOOL" "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
chmod +x "$APPIMAGE_TOOL"

# Disable AppImage sandbox inside docker/container if needed
export APPIMAGE_EXTRACT_AND_RUN=1

echo "Packaging AppImage..."
ARCH=x86_64 "$APPIMAGE_TOOL" "$APP_DIR" WriteReallyFree-x86_64.AppImage

echo "SUCCESS: WriteReallyFree-x86_64.AppImage generated successfully!"
