@echo off
setlocal

cd /d "%~dp0"

echo [1/4] Verifying Python is available...
where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    exit /b 1
)

echo [2/4] Installing dependencies...
python -m pip install --upgrade pip
if errorlevel 1 exit /b 1
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1

echo [3/4] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "qr-tool.spec" del /q "qr-tool.spec"

echo [4/4] Building executable with PyInstaller...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name qr-tool main.py
if errorlevel 1 (
    echo Build failed.
    exit /b 1
)

echo.
echo Build complete: dist\qr-tool.exe
endlocal
