"""
Theme Manager for YouTube MP3 GUI Downloader.
Manages application themes, colors, fonts, and responsive behavior.
"""
import customtkinter as ctk
from typing import Dict, Any, Callable, Optional
from enum import Enum
import json
import os


class ThemeMode(Enum):
    """Available theme modes."""
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"


class ThemeManager:
    """
    Manages application theming and responsive behavior.
    
    Features:
    - Dark/Light theme switching
    - Consistent color scheme management
    - Font configuration
    - Responsive layout utilities
    - Theme persistence
    """
    
    def __init__(self):
        self._current_theme = ThemeMode.DARK
        self._theme_callbacks: list[Callable] = []
        self._config_file = ".kiro/theme_config.json"
        
        # Define color schemes according to design specification
        self._color_schemes = {
            ThemeMode.DARK: {
                # Primary colors
                "primary": "#1f538d",
                "primary_hover": "#14375e",
                "secondary": "#14375e",
                "secondary_hover": "#0f2a47",
                
                # Status colors
                "success": "#2fa572",
                "success_hover": "#258a5f",
                "warning": "#FFA500",
                "warning_hover": "#e6940a",
                "error": "#fa2d2d",
                "error_hover": "#d42525",
                
                # Background colors
                "bg_primary": "#212121",
                "bg_secondary": "#2b2b2b",
                "bg_tertiary": "#3b3b3b",
                
                # Text colors
                "text_primary": "#FFFFFF",
                "text_secondary": "#CCCCCC",
                "text_disabled": "#808080",
                "text_placeholder": "#808080",
                
                # Border colors
                "border": "#404040",
                "border_hover": "#505050",
                
                # Progress colors
                "progress_bg": "#404040",
                "progress_fill": "#1f538d",
                
                # Log colors
                "log_info": "#FFFFFF",
                "log_warning": "#FFA500",
                "log_error": "#FF4444",
                "log_success": "#00FF88"
            },
            
            ThemeMode.LIGHT: {
                # Primary colors
                "primary": "#1f538d",
                "primary_hover": "#14375e",
                "secondary": "#14375e",
                "secondary_hover": "#0f2a47",
                
                # Status colors
                "success": "#2fa572",
                "success_hover": "#258a5f",
                "warning": "#FF8C00",
                "warning_hover": "#e67e00",
                "error": "#dc3545",
                "error_hover": "#c82333",
                
                # Background colors
                "bg_primary": "#FFFFFF",
                "bg_secondary": "#F8F9FA",
                "bg_tertiary": "#E9ECEF",
                
                # Text colors
                "text_primary": "#212529",
                "text_secondary": "#495057",
                "text_disabled": "#6C757D",
                "text_placeholder": "#6C757D",
                
                # Border colors
                "border": "#DEE2E6",
                "border_hover": "#CED4DA",
                
                # Progress colors
                "progress_bg": "#E9ECEF",
                "progress_fill": "#1f538d",
                
                # Log colors
                "log_info": "#212529",
                "log_warning": "#FF8C00",
                "log_error": "#dc3545",
                "log_success": "#28a745"
            }
        }
        
        # Define font configurations according to design specification
        # Fonts will be created lazily when first requested
        self._font_configs = {
            "title": {"family": "Roboto", "size": 24, "weight": "bold"},
            "heading": {"family": "Roboto", "size": 16, "weight": "bold"},
            "subheading": {"family": "Roboto", "size": 14, "weight": "bold"},
            "body": {"family": "Roboto", "size": 12, "weight": "normal"},
            "body_bold": {"family": "Roboto", "size": 12, "weight": "bold"},
            "small": {"family": "Roboto", "size": 10, "weight": "normal"},
            "console": {"family": "Consolas", "size": 10, "weight": "normal"},
            "button": {"family": "Roboto", "size": 14, "weight": "bold"},
            "button_large": {"family": "Roboto", "size": 16, "weight": "bold"}
        }
        self._fonts = {}
        
        # Responsive breakpoints (window width in pixels)
        self._breakpoints = {
            "small": 600,
            "medium": 800,
            "large": 1200
        }
        
        # Load saved theme preference
        self._load_theme_config()
        
        # Apply initial theme
        self._apply_theme()
    
    def get_current_theme(self) -> ThemeMode:
        """Get the current theme mode."""
        return self._current_theme
    
    def set_theme(self, theme: ThemeMode):
        """
        Set the application theme.
        
        Args:
            theme: The theme mode to apply
        """
        if theme != self._current_theme:
            self._current_theme = theme
            self._apply_theme()
            self._save_theme_config()
            self._notify_theme_change()
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        if self._current_theme == ThemeMode.DARK:
            self.set_theme(ThemeMode.LIGHT)
        else:
            self.set_theme(ThemeMode.DARK)
    
    def get_color(self, color_key: str) -> str:
        """
        Get a color value for the current theme.
        
        Args:
            color_key: The color key to retrieve
            
        Returns:
            The color value as a hex string
        """
        return self._color_schemes[self._current_theme].get(color_key, "#FFFFFF")
    
    def get_font(self, font_key: str) -> ctk.CTkFont:
        """
        Get a font configuration.
        
        Args:
            font_key: The font key to retrieve
            
        Returns:
            The CTkFont object
        """
        # Create font lazily if not already created
        if font_key not in self._fonts:
            config = self._font_configs.get(font_key, self._font_configs["body"])
            try:
                self._fonts[font_key] = ctk.CTkFont(**config)
            except RuntimeError:
                # If no root window exists yet, create a placeholder that will work later
                # Store the config for later creation
                return config
        
        return self._fonts[font_key]
    
    def get_font_config(self, font_key: str) -> Dict[str, Any]:
        """
        Get font configuration as a dictionary.
        
        Args:
            font_key: The font key to retrieve
            
        Returns:
            Dictionary with font configuration
        """
        return self._font_configs.get(font_key, self._font_configs["body"])
    
    def get_responsive_size(self, window_width: int, sizes: Dict[str, Any]) -> Any:
        """
        Get a responsive size value based on window width.
        
        Args:
            window_width: Current window width in pixels
            sizes: Dictionary with 'small', 'medium', 'large' keys
            
        Returns:
            The appropriate size value
        """
        if window_width < self._breakpoints["small"]:
            return sizes.get("small", sizes.get("medium", sizes.get("large")))
        elif window_width < self._breakpoints["medium"]:
            return sizes.get("medium", sizes.get("large", sizes.get("small")))
        else:
            return sizes.get("large", sizes.get("medium", sizes.get("small")))
    
    def get_responsive_padding(self, window_width: int) -> tuple[int, int]:
        """
        Get responsive padding values based on window width.
        
        Args:
            window_width: Current window width in pixels
            
        Returns:
            Tuple of (horizontal_padding, vertical_padding)
        """
        if window_width < self._breakpoints["small"]:
            return (10, 10)
        elif window_width < self._breakpoints["medium"]:
            return (15, 15)
        else:
            return (20, 20)
    
    def register_theme_callback(self, callback: Callable):
        """
        Register a callback to be called when theme changes.
        
        Args:
            callback: Function to call on theme change
        """
        if callback not in self._theme_callbacks:
            self._theme_callbacks.append(callback)
    
    def unregister_theme_callback(self, callback: Callable):
        """
        Unregister a theme change callback.
        
        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._theme_callbacks:
            self._theme_callbacks.remove(callback)
    
    def create_themed_button(self, parent, text: str, command: Callable = None, 
                           button_type: str = "primary", **kwargs) -> ctk.CTkButton:
        """
        Create a button with consistent theming.
        
        Args:
            parent: Parent widget
            text: Button text
            command: Button command
            button_type: Type of button (primary, secondary, success, warning, error)
            **kwargs: Additional button arguments
            
        Returns:
            Configured CTkButton
        """
        # Get colors based on button type
        color_map = {
            "primary": ("primary", "primary_hover"),
            "secondary": ("secondary", "secondary_hover"),
            "success": ("success", "success_hover"),
            "warning": ("warning", "warning_hover"),
            "error": ("error", "error_hover")
        }
        
        fg_color_key, hover_color_key = color_map.get(button_type, ("primary", "primary_hover"))
        
        # Default button configuration
        button_config = {
            "text": text,
            "command": command,
            "font": self.get_font("button"),
            "fg_color": self.get_color(fg_color_key),
            "hover_color": self.get_color(hover_color_key),
            "text_color": self.get_color("text_primary"),
            "corner_radius": 8,
            "height": 40
        }
        
        # Override with provided kwargs
        button_config.update(kwargs)
        
        return ctk.CTkButton(parent, **button_config)
    
    def create_themed_frame(self, parent, **kwargs) -> ctk.CTkFrame:
        """
        Create a frame with consistent theming.
        
        Args:
            parent: Parent widget
            **kwargs: Additional frame arguments
            
        Returns:
            Configured CTkFrame
        """
        frame_config = {
            "fg_color": self.get_color("bg_secondary"),
            "border_color": self.get_color("border"),
            "corner_radius": 8
        }
        
        frame_config.update(kwargs)
        return ctk.CTkFrame(parent, **frame_config)
    
    def create_themed_label(self, parent, text: str, font_type: str = "body", **kwargs) -> ctk.CTkLabel:
        """
        Create a label with consistent theming.
        
        Args:
            parent: Parent widget
            text: Label text
            font_type: Font type to use
            **kwargs: Additional label arguments
            
        Returns:
            Configured CTkLabel
        """
        label_config = {
            "text": text,
            "font": self.get_font(font_type),
            "text_color": self.get_color("text_primary")
        }
        
        label_config.update(kwargs)
        return ctk.CTkLabel(parent, **label_config)
    
    def _apply_theme(self):
        """Apply the current theme to CustomTkinter."""
        # Set CustomTkinter appearance mode
        if self._current_theme == ThemeMode.SYSTEM:
            ctk.set_appearance_mode("system")
        else:
            ctk.set_appearance_mode(self._current_theme.value)
        
        # Set color theme
        ctk.set_default_color_theme("blue")
    
    def _notify_theme_change(self):
        """Notify all registered callbacks about theme change."""
        for callback in self._theme_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in theme callback: {e}")
    
    def _load_theme_config(self):
        """Load theme configuration from file."""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, 'r') as f:
                    config = json.load(f)
                    theme_str = config.get('theme', 'dark')
                    self._current_theme = ThemeMode(theme_str)
        except Exception as e:
            print(f"Error loading theme config: {e}")
            self._current_theme = ThemeMode.DARK
    
    def _save_theme_config(self):
        """Save theme configuration to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._config_file), exist_ok=True)
            
            config = {
                'theme': self._current_theme.value
            }
            
            with open(self._config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving theme config: {e}")


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager