"""
FFmpeg service for checking availability and managing FFmpeg operations.
"""
import os
import subprocess
from typing import Tuple
from .exceptions import FFmpegNotFoundError


class FFmpegService:
    """Service class for FFmpeg operations and validation."""
    
    @staticmethod
    def check_availability() -> Tuple[bool, str]:
        """
        Check if FFmpeg is available either locally or in system PATH.
        
        Returns:
            Tuple[bool, str]: (is_available, ffmpeg_path)
        """
        # First try to find local FFmpeg
        ffmpeg_local = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg', 'ffmpeg.exe')
        
        if os.path.exists(ffmpeg_local):
            return True, ffmpeg_local
        
        # If not found locally, try system PATH
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=10
            )
            if result.returncode == 0:
                return True, 'ffmpeg'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return False, ""
    
    @staticmethod
    def get_ffmpeg_path() -> str:
        """
        Get the FFmpeg path, raising an exception if not found.
        
        Returns:
            str: Path to FFmpeg executable
            
        Raises:
            FFmpegNotFoundError: If FFmpeg is not available
        """
        is_available, ffmpeg_path = FFmpegService.check_availability()
        
        if not is_available:
            raise FFmpegNotFoundError(
                "FFmpeg não encontrado. Por favor, instale o FFmpeg ou "
                "coloque o executável na pasta 'ffmpeg/'."
            )
        
        return ffmpeg_path
    
    @staticmethod
    def get_ffmpeg_location_for_ydl(ffmpeg_path: str) -> str:
        """
        Get the directory containing FFmpeg for yt-dlp configuration.
        
        Args:
            ffmpeg_path: Path to FFmpeg executable
            
        Returns:
            str: Directory containing FFmpeg executable
        """
        if ffmpeg_path == 'ffmpeg':
            # System FFmpeg, return None to let yt-dlp find it
            return None
        
        # Local FFmpeg, return the directory
        return os.path.dirname(ffmpeg_path)