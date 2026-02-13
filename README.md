## QR Tool

**A CLI tool to generate QR codes and scan QR codes from image or camera.**

## Features

**- Generate QR (PNG)**

**- Scan QR from image**

**- Scan QR from camera**

**- Optional Desktop GUI build (Windows EXE) alongside CLI**

## Setup

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run (CLI)

```bash
python main.py
```

## Run (GUI)

```bash
python gui_app.py
```

## Build Windows GUI EXE

Use the helper script:

```bat
build_gui_exe.bat
```

Or run manually:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name QR-Tool-GUI gui_app.py
```

Output file:

```text
dist/QR-Tool-GUI.exe
```

**Notes**

* **Image paths with quotes are supported**
* **If camera index 0 doesn't work, try 1 or 2**
* **CLI version remains unchanged (`main.py`) and can be used in parallel with GUI.**
