"""
Configuration management for YouTube MP3 GUI Downloader.
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Manages application configuration and settings."""
    
    DEFAULT_CONFIG = {
        "download_folder": "downloads",
        "audio_quality": "192",
        "audio_format": "mp3",
        "ffmpeg_path": "",
        "theme": "dark",
        "window_width": 800,
        "window_height": 600,
        "auto_scroll_logs": True,
        "max_concurrent_downloads": 3
    }
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the configuration manager."""
        self.config_file = Path(config_file)
        self._config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file, creating default if it doesn't exist."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Update default config with loaded values
                    self._config.update(loaded_config)
            else:
                # Create default config file
                self.save_config()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config file: {e}. Using default configuration.")
            self._config = self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            # Ensure the directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._config[key] = value
    
    def get_download_folder(self) -> str:
        """Get the download folder path."""
        folder = self._config.get("download_folder", "downloads")
        # Ensure the folder exists
        Path(folder).mkdir(parents=True, exist_ok=True)
        return folder
    
    def get_audio_quality(self) -> str:
        """Get the audio quality setting."""
        return self._config.get("audio_quality", "192")
    
    def get_audio_format(self) -> str:
        """Get the audio format setting."""
        return self._config.get("audio_format", "mp3")
    
    def get_ffmpeg_path(self) -> str:
        """Get the FFmpeg path, checking local and system paths."""
        # First check if a custom path is configured
        custom_path = self._config.get("ffmpeg_path", "")
        if custom_path and os.path.exists(custom_path):
            return custom_path
        
        # Check local ffmpeg folder
        local_ffmpeg = Path("ffmpeg/ffmpeg.exe")
        if local_ffmpeg.exists():
            return str(local_ffmpeg.absolute())
        
        # Return empty string to let the system find ffmpeg
        return ""
    
    def get_theme(self) -> str:
        """Get the UI theme setting."""
        return self._config.get("theme", "dark")
    
    def get_window_size(self) -> tuple[int, int]:
        """Get the window size settings."""
        width = self._config.get("window_width", 800)
        height = self._config.get("window_height", 600)
        return width, height
    
    def get_max_concurrent_downloads(self) -> int:
        """Get the maximum number of concurrent downloads."""
        return self._config.get("max_concurrent_downloads", 3)
    
    def is_auto_scroll_enabled(self) -> bool:
        """Check if auto-scroll for logs is enabled."""
        return self._config.get("auto_scroll_logs", True)
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """Update multiple settings at once."""
        for key, value in settings.items():
            if key in self.DEFAULT_CONFIG:
                self._config[key] = value
        self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = self.DEFAULT_CONFIG.copy()
        self.save_config()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings."""
        return self._config.copy()