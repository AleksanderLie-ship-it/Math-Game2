@echo off
title Build - Math Practice Game
set VERSION=0.6.1
echo.
echo ============================================
echo   Building Math Practice v%VERSION%
echo ============================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python from https://python.org
    pause
    exit /b 1
)

echo [1/3] Installing PyInstaller...
python -m pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [2/3] Building executable...
python -m PyInstaller --onefile --windowed --name "MathPractice_v%VERSION%" --paths . game.py
if errorlevel 1 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

echo [3/3] Cleaning up build files...
rmdir /s /q build
rmdir /s /q __pycache__
del /q "MathPractice_v%VERSION%.spec"

echo.
echo ============================================
echo   Done! Find MathPractice_v%VERSION%.exe in dist\
echo ============================================
echo.
pause
