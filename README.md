# ReallyFree - FreeWrite explorer.

A work in progress.


## Prerequisites & Installation

### 1. System Dependencies (Linux)

PyWebView requires a rendering engine. On Linux, it supports either GTK (via WebKit2GTK) or Qt.

To use the WebKit2GTK backend, install the packages for your distribution:

**On Ubuntu / Debian / Mint:**
```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.0
# Or for newer distributions:
sudo apt install gir1.2-webkit2-4.1
```

**On Fedora:**
```bash
sudo dnf install python3-gobject webkit2gtk4.0
# Or webkit2gtk4.1 depending on version
```

**On Arch Linux:**
```bash
sudo pacman -S python-gobject webkit2gtk
```

### 2. System Dependencies (macOS)

On macOS, `pywebview` uses the native WebKit engine via Cocoa. When using a Python virtual environment, you need Python bindings for Objective-C:

```bash
pip install pywebview[cocoa]
# This automatically installs the required pyobjc modules (such as pyobjc-framework-Cocoa and pyobjc-framework-WebKit)
```

### 3. System Dependencies (Windows)

On Windows, `pywebview` renders windows using **WebView2** (Edge Chromium engine) and interfaces with the system via `.NET`.

- **Runtime**: Windows 10 & 11 come with the **WebView2 Runtime** pre-installed. For older Windows versions, download and install the WebView2 Runtime from Microsoft's website.
- **Python bindings**:
  ```bash
  pip install pywebview[winforms]
  # This automatically installs pythonnet (the Python-to-.NET bridge)
  ```

### 4. Python Virtual Environment Setup

Initialize and install Python packages using the local virtual environment:

```bash
# 1. Navigate to the project directory
cd ~/src/reallyfree

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt
```

## Running the Application

Ensure your virtual environment is active, then launch the entry script:

```bash
python app.py
```

To close the app, simply close the desktop window.

## License

This project is licensed under the terms of the GNU General Public License v3.0. See [LICENSE](LICENSE) for the full text.
