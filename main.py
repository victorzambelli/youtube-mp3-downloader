#!/usr/bin/env python3
"""
Main entry point for YouTube MP3 GUI Downloader.

This script initializes the application, sets up necessary resources,
and launches the main GUI window with comprehensive error handling
and resource management.
"""
import sys
import os
import logging
import traceback
from pathlib import Path
from typing import Optional

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from src.main_window import MainWindow
    from src.ffmpeg_service import FFmpegService
    from src.exceptions import FFmpegNotFoundError, DownloadError
except ImportError as e:
    print(f"✗ Error importing modules: {e}")
    print("Make sure all required dependencies are installed.")
    print("Run: pip install -r requirements.txt")
    input("Press Enter to exit...")
    sys.exit(1)


def setup_logging() -> logging.Logger:
    """
    Set up comprehensive logging configuration for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(
                log_dir / "youtube_mp3_gui.log",
                mode='a',
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create application logger
    logger = logging.getLogger('youtube_mp3_gui')
    logger.setLevel(logging.DEBUG)
    
    # Add debug file handler for detailed logging
    debug_handler = logging.FileHandler(
        log_dir / "debug.log",
        mode='a',
        encoding='utf-8'
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    debug_handler.setFormatter(debug_formatter)
    logger.addHandler(debug_handler)
    
    return logger


def check_dependencies(logger: logging.Logger) -> bool:
    """
    Check if all required dependencies are available.
    
    Args:
        logger: Logger instance for detailed logging
        
    Returns:
        bool: True if all dependencies are available, False otherwise
    """
    logger.info("Starting dependency check")
    
    # Check Python packages
    required_packages = [
        ('customtkinter', 'CustomTkinter GUI framework'),
        ('yt_dlp', 'YouTube downloader'),
        ('requests', 'HTTP library')
    ]
    
    missing_packages = []
    
    for package_name, description in required_packages:
        try:
            __import__(package_name)
            print(f"✓ {description} available")
            logger.debug(f"Package {package_name} imported successfully")
        except ImportError as e:
            print(f"✗ Missing {description}: {package_name}")
            missing_packages.append(package_name)
            logger.error(f"Failed to import {package_name}: {e}")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install required packages using: pip install -r requirements.txt")
        logger.error(f"Missing required packages: {missing_packages}")
        return False
    
    print("✓ All required Python packages are available")
    logger.info("All Python packages available")
    
    # Check FFmpeg availability (Requirements 4.1, 4.2, 4.3)
    try:
        ffmpeg_available, ffmpeg_path = FFmpegService.check_availability()
        if ffmpeg_available:
            print(f"✓ FFmpeg found at: {ffmpeg_path}")
            logger.info(f"FFmpeg available at: {ffmpeg_path}")
        else:
            print("⚠ FFmpeg not found. The application may not work properly.")
            print("Please ensure FFmpeg is available in the 'ffmpeg' folder or system PATH.")
            print("You can download FFmpeg from: https://ffmpeg.org/download.html")
            logger.warning("FFmpeg not found - application may not function properly")
            
            # Don't fail completely, but warn user
            return True
            
    except Exception as e:
        print(f"✗ Error checking FFmpeg: {e}")
        logger.error(f"Error during FFmpeg check: {e}", exc_info=True)
        return False
    
    logger.info("Dependency check completed successfully")
    return True


def setup_directories(logger: logging.Logger) -> bool:
    """
    Create necessary directories for the application.
    
    Args:
        logger: Logger instance for detailed logging
        
    Returns:
        bool: True if all directories were created successfully, False otherwise
    """
    logger.info("Setting up application directories")
    
    directories = {
        "downloads": "Download output directory",
        "logs": "Application logs directory",
        "ffmpeg": "FFmpeg binaries directory (if needed)"
    }
    
    try:
        for directory, description in directories.items():
            dir_path = Path(directory)
            
            # Create directory if it doesn't exist
            if not dir_path.exists():
                dir_path.mkdir(exist_ok=True)
                print(f"✓ Created directory '{directory}' ({description})")
                logger.info(f"Created directory: {directory}")
            else:
                print(f"✓ Directory '{directory}' ready")
                logger.debug(f"Directory already exists: {directory}")
            
            # Check if directory is writable
            if not os.access(dir_path, os.W_OK):
                print(f"✗ Directory '{directory}' is not writable")
                logger.error(f"Directory not writable: {directory}")
                return False
                
    except PermissionError as e:
        print(f"✗ Permission error creating directories: {e}")
        logger.error(f"Permission error during directory setup: {e}")
        return False
    except Exception as e:
        print(f"✗ Error setting up directories: {e}")
        logger.error(f"Unexpected error during directory setup: {e}", exc_info=True)
        return False
    
    logger.info("Directory setup completed successfully")
    return True


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    Handle uncaught exceptions by logging them and showing user-friendly messages.
    
    Args:
        exc_type: Exception type
        exc_value: Exception value
        exc_traceback: Exception traceback
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow KeyboardInterrupt to work normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger = logging.getLogger('youtube_mp3_gui')
    
    # Log the full exception with traceback
    logger.critical(
        "Uncaught exception occurred",
        exc_info=(exc_type, exc_value, exc_traceback)
    )
    
    # Show user-friendly error message
    error_msg = f"An unexpected error occurred: {exc_value}"
    print(f"\n✗ CRITICAL ERROR: {error_msg}")
    print("Please check the log files for detailed information.")
    print("Log location: logs/youtube_mp3_gui.log")
    
    # Try to show GUI error dialog if possible
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        messagebox.showerror(
            "Critical Error",
            f"An unexpected error occurred:\n\n{exc_value}\n\n"
            "Please check the log files for more details.\n"
            "Log location: logs/youtube_mp3_gui.log"
        )
        root.destroy()
    except:
        # If GUI error dialog fails, just continue
        pass
    
    input("Press Enter to exit...")
    sys.exit(1)


def initialize_resources(logger: logging.Logger) -> bool:
    """
    Initialize all application resources and dependencies.
    
    Args:
        logger: Logger instance for detailed logging
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    logger.info("Initializing application resources")
    
    # Check dependencies (Requirements 4.1, 4.2, 4.3)
    print("Checking dependencies...")
    if not check_dependencies(logger):
        logger.error("Dependency check failed")
        return False
    
    # Set up directories
    print("\nSetting up directories...")
    if not setup_directories(logger):
        logger.error("Directory setup failed")
        return False
    
    # Verify FFmpeg functionality (Requirements 4.1, 4.2, 4.3)
    try:
        ffmpeg_path = FFmpegService.get_ffmpeg_path()
        logger.info(f"FFmpeg verified and ready at: {ffmpeg_path}")
        print(f"✓ FFmpeg verified and ready")
    except FFmpegNotFoundError as e:
        print(f"⚠ Warning: {e}")
        logger.warning(f"FFmpeg not available: {e}")
        print("The application will start but downloads may fail without FFmpeg.")
    except Exception as e:
        print(f"✗ Error verifying FFmpeg: {e}")
        logger.error(f"FFmpeg verification failed: {e}", exc_info=True)
        return False
    
    logger.info("Resource initialization completed successfully")
    return True


def main():
    """
    Main application entry point with comprehensive error handling.
    
    This function handles:
    - Application initialization and resource setup
    - Dependency checking (Requirements 4.1, 4.2, 4.3)
    - Exception handling for robust operation (Requirements 6.1, 6.2)
    - Logging setup for debugging and monitoring
    """
    print("YouTube MP3 GUI Downloader")
    print("=" * 40)
    print("Version: 1.0.0")
    print()
    
    logger: Optional[logging.Logger] = None
    
    try:
        # Set up logging first
        logger = setup_logging()
        logger.info("=" * 50)
        logger.info("YouTube MP3 GUI Downloader starting")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Platform: {sys.platform}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info("=" * 50)
        
        # Install global exception handler
        sys.excepthook = handle_uncaught_exception
        
        # Initialize all resources
        if not initialize_resources(logger):
            logger.error("Resource initialization failed - exiting")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("\nStarting application...")
        logger.info("Launching main application window")
        
        # Create and run the main application
        app = MainWindow()
        logger.info("MainWindow created successfully")
        
        # Start the application main loop
        app.run()
        
        logger.info("Application closed normally")
        print("Application closed successfully.")
        
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user (Ctrl+C)")
        if logger:
            logger.info("Application interrupted by user (KeyboardInterrupt)")
        sys.exit(0)
        
    except FFmpegNotFoundError as e:
        error_msg = f"FFmpeg dependency error: {e}"
        print(f"\n✗ {error_msg}")
        if logger:
            logger.error(error_msg)
        print("\nPlease install FFmpeg or place ffmpeg.exe in the 'ffmpeg' folder.")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except DownloadError as e:
        error_msg = f"Download system error: {e}"
        print(f"\n✗ {error_msg}")
        if logger:
            logger.error(error_msg, exc_info=True)
        input("Press Enter to exit...")
        sys.exit(1)
        
    except ImportError as e:
        error_msg = f"Module import error: {e}"
        print(f"\n✗ {error_msg}")
        if logger:
            logger.error(error_msg, exc_info=True)
        print("Please ensure all required packages are installed:")
        print("pip install -r requirements.txt")
        input("Press Enter to exit...")
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Unexpected error during startup: {str(e)}"
        print(f"\n✗ {error_msg}")
        if logger:
            logger.critical(error_msg, exc_info=True)
        else:
            # If logger wasn't set up, print traceback
            traceback.print_exc()
        
        print("\nPlease check the log files for detailed information.")
        print("Log location: logs/youtube_mp3_gui.log")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()