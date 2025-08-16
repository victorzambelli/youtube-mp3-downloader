"""
Custom exceptions for the YouTube MP3 GUI Downloader.
"""


class DownloadError(Exception):
    """Base exception for download-related errors."""
    pass


class FFmpegNotFoundError(DownloadError):
    """Raised when FFmpeg is not found on the system."""
    pass


class URLValidationError(DownloadError):
    """Raised when URL validation fails."""
    pass


class FileSystemError(DownloadError):
    """Raised when file system operations fail."""
    pass


class NetworkError(DownloadError):
    """Raised when network-related errors occur during download."""
    pass


class ConversionError(DownloadError):
    """Raised when audio conversion fails."""
    pass