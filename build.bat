@echo off
REM Automated build script for YouTube MP3 GUI Downloader (Windows)
REM This batch file runs the Python build script

echo YouTube MP3 GUI Downloader - Build Script
echo ==========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if build.py exists
if not exist "build.py" (
    echo Error: build.py not found
    echo Make sure you're running this from the project directory
    pause
    exit /b 1
)

REM Run the build script
echo Running build script...
python build.py %*

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Check the 'dist' directory for the exec