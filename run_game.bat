@echo off
echo ========================================
echo   Stacking Plates Game Launcher
echo ========================================
echo.

REM Check if audio files exist
if not exist "background.mp3" (
    echo Audio files not found. Generating...
    python generate_audio.py
    echo.
)

echo Starting game...
echo.
python Python_project.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Error: Game failed to start
    echo ========================================
    echo.
    echo Possible solutions:
    echo 1. Install dependencies: pip install -r requirements.txt
    echo 2. Check Python version: python --version
    echo 3. Make sure pygame is installed: pip install pygame
    echo.
    pause
)
