@echo off
title GliaCore Studio 0.3.0 - Modular Micro-AI Collective Intelligence Ecosystem
color 0B

echo ===============================================================================
echo                GLIACORE 0.3.0 -- ASTROCYTE COLLECTIVE INTELLIGENCE
echo                Target: Windows 11 ^| NVIDIA RTX 2050 (4GB VRAM) ^| 16GB RAM
echo ===============================================================================
echo.

:: Move to repository directory
cd /d "%~dp0"

:: Set PYTHONPATH to include src
set PYTHONPATH=src;%PYTHONPATH%

:: Verify Python is installed and accessible
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    color 0C
    echo [ERROR] Python was not found in your PATH!
    echo Please install Python 3.10+ and ensure "Add python.exe to PATH" is enabled.
    echo.
    pause
    exit /b 1
)

echo [*] Starting GliaCore Studio Local Server...
echo [*] Web Interface URL: http://127.0.0.1:8000
echo [*] Press Ctrl+C in this terminal window to stop the server anytime.
echo.

:: Automatically open browser after 2 seconds in the background
start "" /b cmd /c "timeout /t 5 /nobreak >nul && start http://127.0.0.1:8000"

:: Start the GliaCore Studio Server
python -m gliacore.ui.server

if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] GliaCore Server exited with error code %ERRORLEVEL%.
    pause
)
