#!/usr/bin/env python3
"""
Automated build script for YouTube MP3 GUI Downloader
Handles PyInstaller build process with proper error handling and validation
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✅ PyInstaller found: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    # Check if FFmpeg binaries exist
    ffmpeg_dir = Path("ffmpeg")
    required_binaries = ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]
    
    if not ffmpeg_dir.exists():
        print("❌ FFmpeg directory not found")
        return False
    
    for binary in required_binaries:
        binary_path = ffmpeg_dir / binary
        if not binary_path.exists():
            print(f"❌ {binary} not found in ffmpeg directory")
            return False
        print(f"✅ {binary} found")
    
    # Check if main.py exists
    if not Path("main.py").exists():
        print("❌ main.py not found")
        return False
    print("✅ main.py found")
    
    return True


def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.pyc"]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✅ Removed {dir_name}")
    
    # Clean __pycache__ directories recursively
    for pycache_dir in Path(".").rglob("__pycache__"):
        shutil.rmtree(pycache_dir)
        print(f"✅ Removed {pycache_dir}")


def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Run PyInstaller with the spec file
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "build.spec"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print(result.stdout)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def validate_build():
    """Validate the built executable"""
    print("🔍 Validating build...")
    
    # Check for directory-based distribution first
    exe_path = Path("dist/youtube-mp3-gui/youtube-mp3-gui.exe")
    dist_ffmpeg = Path("dist/youtube-mp3-gui/_internal/ffmpeg")
    
    # Fallback to single-file distribution
    if not exe_path.exists():
        exe_path = Path("dist/youtube-mp3-gui.exe")
        dist_ffmpeg = Path("dist/ffmpeg")
    
    if not exe_path.exists():
        print("❌ Executable not found in dist directory")
        return False
    
    print(f"✅ Executable found: {exe_path}")
    print(f"📦 Size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    
    # Check if FFmpeg binaries are included
    if dist_ffmpeg.exists():
        print("✅ FFmpeg directory found in dist")
        for binary in ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]:
            if (dist_ffmpeg / binary).exists():
                print(f"✅ {binary} included")
            else:
                print(f"❌ {binary} missing")
                return False
    else:
        print("❌ FFmpeg directory not found in dist")
        return False
    
    return True


def create_distribution():
    """Create a clean distribution directory"""
    print("📦 Creating distribution package...")
    
    # Check for directory-based distribution first
    app_dir = Path("dist/youtube-mp3-gui")
    if app_dir.exists():
        dist_dir = app_dir
    else:
        dist_dir = Path("dist")
    
    if not dist_dir.exists():
        print("❌ Dist directory not found")
        return False
    
    # Create downloads directory in dist
    downloads_dir = dist_dir / "downloads"
    downloads_dir.mkdir(exist_ok=True)
    print("✅ Created downloads directory")
    
    # Copy README if it exists
    if Path("README.md").exists():
        shutil.copy2("README.md", dist_dir / "README.txt")
        print("✅ Copied README")
    
    # Create a simple usage instruction file
    usage_file = dist_dir / "USAGE.txt"
    with open(usage_file, "w", encoding="utf-8") as f:
        f.write("""YouTube MP3 GUI Downloader
==========================

Usage:
1. Double-click youtube-mp3-gui.exe to start the application
2. Paste YouTube URLs in the text field (one per line)
3. Click Download to start downloading
4. Files will be saved in the 'downloads' folder

Requirements:
- Windows 10 or later
- Internet connection
- FFmpeg binaries (included)

The application includes all necessary dependencies and FFmpeg binaries.
No additional installation is required.

Distribution Contents:
- youtube-mp3-gui.exe: Main application executable
- _internal/: Application dependencies and libraries
- _internal/ffmpeg/: FFmpeg binaries for audio conversion
- downloads/: Default download directory
- USAGE.txt: This file
""")
    print("✅ Created usage instructions")
    
    return True


def main():
    """Main build process"""
    parser = argparse.ArgumentParser(description="Build YouTube MP3 GUI Downloader")
    parser.add_argument("--clean-only", action="store_true", help="Only clean build artifacts")
    parser.add_argument("--no-clean", action="store_true", help="Skip cleaning step")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing build")
    
    args = parser.parse_args()
    
    print("🚀 YouTube MP3 GUI Downloader Build Script")
    print("=" * 50)
    
    if args.clean_only:
        clean_build()
        return
    
    if args.validate_only:
        if validate_build():
            print("✅ Build validation passed!")
        else:
            print("❌ Build validation failed!")
            sys.exit(1)
        return
    
    # Full build process
    if not check_dependencies():
        print("❌ Dependency check failed!")
        sys.exit(1)
    
    if not args.no_clean:
        clean_build()
    
    if not build_executable():
        print("❌ Build process failed!")
        sys.exit(1)
    
    if not validate_build():
        print("❌ Build validation failed!")
        sys.exit(1)
    
    if not create_distribution():
        print("❌ Distribution creation failed!")
        sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print(f"📁 Executable location: {Path('dist/youtube-mp3-gui.exe').absolute()}")
    print("🚀 You can now distribute the contents of the 'dist' directory")


if __name__ == "__main__":
    main()