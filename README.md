# WriteReallyFree - FreeWrite explorer

<img width="1006" height="722" alt="Screenshot_20260726_225607" src="https://github.com/user-attachments/assets/9922411f-4e65-4a92-be36-a91cb512f349" />

This is a work in progress. The current version synchronizes text files from a FreeWrite device to a configured directory on a Linux, Mac or PC. 

You can configure a location to sync files and set custom folder names.

<img width="451" height="612" alt="Screenshot_20260815_175235" src="https://github.com/user-attachments/assets/3da005bf-a5b5-4d65-bcbc-17c737a04299" />

It will optionally convert the files to .docx, supporting any markdown formatting you have in there, too.

You can configure a few options for the docx conversion:

<img width="447" height="360" alt="Screenshot_20260815_175116" src="https://github.com/user-attachments/assets/38924592-80c3-44ee-a0b4-c9f9df2c170e" />

It will find your FreeWrite on demand if you run the app before you remember to plug it in.

[Screencast_20260815_174659.webm](https://github.com/user-attachments/assets/37bd7b66-1860-405a-b98d-ee1dff53492d)

## Releases
The latest releases are [here](https://github.com/egoebelbecker/writereallyfree/releases). 

### Running the releases.

### Linux

Download the AppImage from the [releases](https://github.com/egoebelbecker/writereallyfree/releases/) page. Unzip it. Run the file. If you like it, use your favorite AppImage manager to add it to your desktop environment.

(I like [GearLever](https://github.com/mijorus/gearlever))

### Mac

Download the DMG from [releases](https://github.com/egoebelbecker/writereallyfree/releases/). Uncompress it. Open the DMG and run it from there. If you like it, drag it over to Applications.

### Windows
Unzip the [package](https://github.com/egoebelbecker/writereallyfree/releases/), run from the unzipped folder. Any help coming up with an easier to manage package is welcome.


## Running the Application from the repository

### Prerequisites

If you want to check out the repo and run from source, you'll need a couple of packages for Linux.

#### 1. System Dependencies (Linux)

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


#### 2. System Dependencies (macOS)

On macOS, `pywebview` uses the native WebKit engine via Cocoa. When using a Python virtual environment, you need Python bindings for Objective-C:

```bash
pip install pywebview[cocoa]
# This automatically installs the required pyobjc modules (such as pyobjc-framework-Cocoa and pyobjc-framework-WebKit)
```
But you can download a DMG and just run the app.

#### 3. System Dependencies

On Windows, `pywebview` renders windows using **WebView2** (Edge Chromium engine) and interfaces with the system via `.NET`.

- **Runtime**: Windows 10 & 11 come with the **WebView2 Runtime** pre-installed. For older Windows versions, download and install the WebView2 Runtime from Microsoft's website.
- **Python bindings**:
  ```bash
  pip install pywebview[winforms]
  # This automatically installs pythonnet (the Python-to-.NET bridge)
  ```

#### 4. Python Virtual Environment Setup

Initialize and install Python packages using the local virtual environment:

```bash
# 1. Navigate to the project directory
cd ~/src/writereallyfree

# 2. Create and activate a virtual environment
source .venv/bin/activate

# 3. Install Python dependencies
pip3 install -r requirements.txt
```

Ensure your virtual environment is active, then launch the entry script:

```bash
python app.py
```

To close the app, simply close the desktop window.

## License

This project is licensed under the terms of the GNU General Public License v3.0. See [LICENSE](LICENSE) for the full text.
