@echo off
setlocal

if not exist venv (
  echo [INFO] Creating virtual environment...
  python -m venv venv
)

call venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --noconfirm --onefile --windowed --name QR-Tool-GUI gui_app.py

echo.
echo [DONE] GUI EXE created at: dist\QR-Tool-GUI.exe
endlocal
