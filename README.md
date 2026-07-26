# ReallyFree - Home Explorer

A modern, cross-platform desktop application built with **PyWebView** that allows secure exploration of your home directory right from a sleek, dark-themed, glassmorphic UI.

## Features

- 🏠 **Quick Access places:** Easily jump to Home, Desktop, Documents, or Downloads.
- 📂 **Directory Traversal:** Double click folders to enter, or use the path breadcrumbs and "Up" button to navigate.
- 🔍 **Real-time Filter:** Instant search filtering of files in the current folder.
- 📄 **Text Previews:** Select any compatible text-based file (like `.txt`, `.md`, `.py`, `.js`, `.json`, etc.) to view its content dynamically in the preview pane.
- 🛡️ **Secure Backend:** Restricts file access strictly to subfolders of the user's home directory, avoiding accidental navigation to system root folders.
- 💅 **Premium UI:** Custom typography (Outfit & JetBrains Mono), responsive flex grids, custom scrollbars, and fine hover micro-animations.

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

### 2. Python Virtual Environment Setup

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
