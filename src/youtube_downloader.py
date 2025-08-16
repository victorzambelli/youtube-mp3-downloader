"""
YouTube downloader service with progress callbacks and error handling.
"""
import os
import yt_dlp
from typing import List, Callable, Optional
from .ffmpeg_service import FFmpegService
from .exceptions import (
    DownloadError, 
    NetworkError, 
    ConversionError, 
    FileSystemError,
    FFmpegNotFoundError
)


class YouTubeDownloader:
    """Service class for downloading YouTube videos and converting to MP3."""
    
    def __init__(self, download_folder: str = "downloads", ffmpeg_path: Optional[str] = None):
        """
        Initialize the YouTube downloader.
        
        Args:
            download_folder: Directory to save downloaded files
            ffmpeg_path: Optional custom FFmpeg path
        """
        self.download_folder = download_folder
        self._ffmpeg_path = ffmpeg_path
        self._cancel_requested = False
        self._ensure_download_folder()
    
    def request_cancellation(self):
        """Request cancellation of current download."""
        self._cancel_requested = True
    
    def _ensure_download_folder(self):
        """Create download folder if it doesn't exist."""
        try:
            if not os.path.exists(self.download_folder):
                os.makedirs(self.download_folder)
        except OSError as e:
            raise FileSystemError(f"Não foi possível criar a pasta de download: {e}")
    
    def _get_ffmpeg_path(self) -> str:
        """Get FFmpeg path, using custom path if provided or detecting automatically."""
        if self._ffmpeg_path:
            return self._ffmpeg_path
        
        return FFmpegService.get_ffmpeg_path()
    
    def _get_ydl_opts(self, progress_hook: Optional[Callable] = None) -> dict:
        """
        Get yt-dlp options configuration.
        
        Args:
            progress_hook: Optional callback for progress updates
            
        Returns:
            dict: yt-dlp configuration options
        """
        ffmpeg_path = self._get_ffmpeg_path()
        ffmpeg_location = FFmpegService.get_ffmpeg_location_for_ydl(ffmpeg_path)
        
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
        
        if ffmpeg_location:
            opts['ffmpeg_location'] = ffmpeg_location
        
        if progress_hook:
            opts['progress_hooks'] = [progress_hook]
        
        return opts
    
    def download_single(
        self, 
        url: str, 
        progress_callback: Optional[Callable[[dict], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        cancel_event: Optional[object] = None
    ) -> bool:
        """
        Download a single YouTube video and convert to MP3.
        
        Args:
            url: YouTube video URL
            progress_callback: Optional callback for progress updates
            log_callback: Optional callback for log messages
            cancel_event: Optional threading event to check for cancellation
            
        Returns:
            bool: True if download successful, False otherwise
            
        Raises:
            FFmpegNotFoundError: If FFmpeg is not available
            NetworkError: If network-related error occurs
            ConversionError: If audio conversion fails
            DownloadError: For other download-related errors
        """
        try:
            # Reset cancellation flag
            self._cancel_requested = False
            
            # Check for cancellation before starting
            if cancel_event and cancel_event.is_set():
                if log_callback:
                    log_callback(f"Download cancelado antes de iniciar: {url}")
                return False
            
            if log_callback:
                log_callback(f"Iniciando download: {url}")
            
            def progress_hook(d):
                # Check for cancellation during download
                if cancel_event and cancel_event.is_set():
                    self._cancel_requested = True
                    # Force yt-dlp to stop by raising an exception
                    raise yt_dlp.utils.DownloadError("Download cancelado pelo usuário")
                
                if progress_callback and d['status'] == 'downloading':
                    progress_callback({
                        'url': url,
                        'status': 'downloading',
                        'downloaded_bytes': d.get('downloaded_bytes', 0),
                        'total_bytes': d.get('total_bytes', 0),
                        'speed': d.get('speed', 0),
                        'eta': d.get('eta', 0)
                    })
                elif progress_callback and d['status'] == 'finished':
                    # Check for cancellation before conversion
                    if cancel_event and cancel_event.is_set():
                        self._cancel_requested = True
                        raise yt_dlp.utils.DownloadError("Download cancelado pelo usuário")
                    
                    progress_callback({
                        'url': url,
                        'status': 'converting',
                        'filename': d.get('filename', '')
                    })
            
            ydl_opts = self._get_ydl_opts(progress_hook)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Final check for cancellation
            if cancel_event and cancel_event.is_set():
                if log_callback:
                    log_callback(f"Download cancelado: {url}")
                return False
            
            if log_callback:
                log_callback(f"Download concluído: {url}")
            
            if progress_callback:
                progress_callback({
                    'url': url,
                    'status': 'completed'
                })
            
            return True
            
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            # Check if this was a user cancellation
            if "cancelado pelo usuário" in error_msg.lower():
                if log_callback:
                    log_callback(f"Download cancelado: {url}")
                return False
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                raise NetworkError(f"Erro de rede ao baixar {url}: {error_msg}")
            elif "postprocess" in error_msg.lower() or "ffmpeg" in error_msg.lower():
                raise ConversionError(f"Erro na conversão de {url}: {error_msg}")
            else:
                raise DownloadError(f"Erro ao baixar {url}: {error_msg}")
        
        except Exception as e:
            raise DownloadError(f"Erro inesperado ao baixar {url}: {str(e)}")
    
    def download_multiple(
        self, 
        urls: List[str], 
        progress_callback: Optional[Callable[[dict], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """
        Download multiple YouTube videos and convert to MP3.
        
        Args:
            urls: List of YouTube video URLs
            progress_callback: Optional callback for progress updates
            log_callback: Optional callback for log messages
            
        Returns:
            dict: Results with 'successful', 'failed', and 'errors' keys
        """
        results = {
            'successful': [],
            'failed': [],
            'errors': {}
        }
        
        if log_callback:
            log_callback(f"Iniciando download de {len(urls)} vídeos...")
            log_callback(f"Pasta de destino: {self.download_folder}")
            
            try:
                ffmpeg_path = self._get_ffmpeg_path()
                log_callback(f"Usando FFmpeg: {ffmpeg_path}")
            except FFmpegNotFoundError as e:
                log_callback(f"Erro: {str(e)}")
                raise
        
        for i, url in enumerate(urls, 1):
            try:
                if log_callback:
                    log_callback(f"[{i}/{len(urls)}] Processando: {url}")
                
                # Create a wrapper for progress callback to include overall progress
                def overall_progress_callback(progress_data):
                    progress_data['overall_progress'] = i / len(urls)
                    progress_data['current_index'] = i
                    progress_data['total_count'] = len(urls)
                    if progress_callback:
                        progress_callback(progress_data)
                
                success = self.download_single(
                    url, 
                    overall_progress_callback, 
                    log_callback
                )
                
                if success:
                    results['successful'].append(url)
                else:
                    results['failed'].append(url)
                    
            except Exception as e:
                results['failed'].append(url)
                results['errors'][url] = str(e)
                
                if log_callback:
                    log_callback(f"Erro ao processar {url}: {str(e)}")
        
        if log_callback:
            log_callback(f"Download concluído! {len(results['successful'])} sucessos, {len(results['failed'])} falhas")
        
        return results