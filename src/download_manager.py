"""
Download Manager for coordinating multiple YouTube downloads with threading support.
"""
import threading
import time
from typing import List, Callable, Optional, Dict, Any
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, Future, as_completed

from .models import DownloadTask, DownloadStatus
from .youtube_downloader import YouTubeDownloader
from .url_validator import URLValidator
from .exceptions import DownloadError, URLValidationError
from .progress_throttler import ProgressThrottler
from .performance_monitor import record_progress_callback


class DownloadManager:
    """
    Manages multiple download tasks with threading support and progress callbacks.
    
    This class coordinates multiple YouTube downloads, providing:
    - Asynchronous downloads using threading
    - Progress callbacks for UI updates
    - Cancellation support
    - Error handling and recovery
    """
    
    def __init__(
        self, 
        progress_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
        download_folder: str = "downloads",
        max_concurrent_downloads: int = 3
    ):
        """
        Initialize the Download Manager.
        
        Args:
            progress_callback: Callback for progress updates (task_id, progress_data)
            log_callback: Callback for log messages
            download_folder: Directory to save downloaded files
            max_concurrent_downloads: Maximum number of concurrent downloads
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.download_folder = download_folder
        self.max_concurrent_downloads = max_concurrent_downloads
        
        # Download state management
        self.tasks: Dict[str, DownloadTask] = {}
        self.is_downloading = False
        self.is_cancelled = False
        
        # Threading components
        self._executor: Optional[ThreadPoolExecutor] = None
        self._futures: Dict[str, Future] = {}
        self._cancel_event = threading.Event()
        self._lock = threading.Lock()
        
        # Progress throttling for performance optimization
        self._progress_throttler = ProgressThrottler(
            min_interval=0.15,  # 150ms minimum between updates
            min_progress_change=3.0,  # 3% minimum progress change
            force_update_interval=1.5  # Force update every 1.5 seconds
        )
        self._progress_throttler.set_callback(self._throttled_progress_callback)
        
        # YouTube downloader instance
        self._downloader = YouTubeDownloader(download_folder=download_folder)
    
    def add_urls(self, urls: List[str]) -> List[str]:
        """
        Add URLs to the download queue after validation.
        
        Args:
            urls: List of YouTube URLs to add
            
        Returns:
            List[str]: List of task IDs for the added URLs
            
        Raises:
            URLValidationError: If no valid URLs are provided
        """
        if not urls:
            raise URLValidationError("No URLs provided")
        
        # Extract and validate URLs
        all_urls = []
        for url_text in urls:
            extracted = URLValidator.extract_urls_from_text(url_text)
            all_urls.extend(extracted)
        
        if not all_urls:
            raise URLValidationError("No valid YouTube URLs found")
        
        # Remove duplicates while preserving order
        unique_urls = []
        seen = set()
        for url in all_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        # Create download tasks
        task_ids = []
        with self._lock:
            for url in unique_urls:
                task_id = self._generate_task_id(url)
                task = DownloadTask(url=url)
                self.tasks[task_id] = task
                task_ids.append(task_id)
        
        if self.log_callback:
            self.log_callback(f"Adicionadas {len(task_ids)} URLs para download")
        
        return task_ids
    
    def start_download(self) -> bool:
        """
        Start downloading all queued tasks.
        
        Returns:
            bool: True if download started successfully, False otherwise
        """
        with self._lock:
            if self.is_downloading:
                if self.log_callback:
                    self.log_callback("Download já está em progresso")
                return False
            
            if not self.tasks:
                if self.log_callback:
                    self.log_callback("Nenhuma URL para download")
                return False
            
            # Reset state
            self.is_downloading = True
            self.is_cancelled = False
            self._cancel_event.clear()
            
            # Reset all tasks to pending
            for task in self.tasks.values():
                task.set_status(DownloadStatus.PENDING)
        
        if self.log_callback:
            self.log_callback(f"Iniciando download de {len(self.tasks)} arquivos...")
            self.log_callback(f"Pasta de destino: {self.download_folder}")
        
        # Start downloads in a separate thread
        download_thread = threading.Thread(target=self._run_downloads, daemon=True)
        download_thread.start()
        
        return True
    
    def cancel_download(self) -> None:
        """Cancel all ongoing downloads."""
        with self._lock:
            if not self.is_downloading:
                return
            
            self.is_cancelled = True
            self._cancel_event.set()
        
        if self.log_callback:
            self.log_callback("Cancelando downloads...")
        
        # Cancel all running futures
        for future in self._futures.values():
            future.cancel()
        
        # Update task statuses
        with self._lock:
            for task in self.tasks.values():
                if task.is_active():
                    task.set_status(DownloadStatus.CANCELLED)
        
        # Cleanup resources
        self._cleanup_resources()
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """
        Get overall download progress information.
        
        Returns:
            Dict containing progress statistics
        """
        with self._lock:
            if not self.tasks:
                return {
                    'total_tasks': 0,
                    'completed': 0,
                    'failed': 0,
                    'cancelled': 0,
                    'active': 0,
                    'pending': 0,
                    'overall_progress': 0.0
                }
            
            stats = {
                'total_tasks': len(self.tasks),
                'completed': 0,
                'failed': 0,
                'cancelled': 0,
                'active': 0,
                'pending': 0
            }
            
            total_progress = 0.0
            
            for task in self.tasks.values():
                if task.is_completed():
                    stats['completed'] += 1
                    total_progress += 100.0
                elif task.is_failed():
                    stats['failed'] += 1
                elif task.is_cancelled():
                    stats['cancelled'] += 1
                elif task.is_active():
                    stats['active'] += 1
                    total_progress += task.progress
                else:  # pending
                    stats['pending'] += 1
            
            stats['overall_progress'] = total_progress / len(self.tasks) if self.tasks else 0.0
            
            return stats
    
    def get_task_status(self, task_id: str) -> Optional[DownloadTask]:
        """
        Get the status of a specific task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            DownloadTask if found, None otherwise
        """
        with self._lock:
            return self.tasks.get(task_id)
    
    def clear_completed_tasks(self) -> int:
        """
        Remove completed tasks from the manager.
        
        Returns:
            int: Number of tasks removed
        """
        with self._lock:
            if self.is_downloading:
                return 0  # Don't clear while downloading
            
            completed_tasks = [
                task_id for task_id, task in self.tasks.items()
                if task.is_completed() or task.is_failed() or task.is_cancelled()
            ]
            
            for task_id in completed_tasks:
                del self.tasks[task_id]
                # Clear throttling data for completed tasks
                self._progress_throttler.clear_task(task_id)
            
            return len(completed_tasks)
    
    def _generate_task_id(self, url: str) -> str:
        """Generate a unique task ID for a URL."""
        video_id = URLValidator.extract_video_id(url)
        if video_id:
            return f"task_{video_id}_{int(time.time())}"
        else:
            return f"task_{hash(url)}_{int(time.time())}"
    
    def _run_downloads(self) -> None:
        """Run all downloads using thread pool executor."""
        try:
            with ThreadPoolExecutor(max_workers=self.max_concurrent_downloads) as executor:
                self._executor = executor
                
                # Submit all tasks
                for task_id, task in self.tasks.items():
                    if self._cancel_event.is_set():
                        break
                    
                    future = executor.submit(self._download_single_task, task_id, task)
                    self._futures[task_id] = future
                
                # Wait for completion
                for future in as_completed(self._futures.values()):
                    if self._cancel_event.is_set():
                        break
                    
                    try:
                        future.result()  # This will raise any exceptions
                    except Exception as e:
                        if self.log_callback:
                            self.log_callback(f"Erro em download: {str(e)}")
        
        finally:
            with self._lock:
                self.is_downloading = False
                self._executor = None
                self._futures.clear()
            
            if self.log_callback:
                if self.is_cancelled:
                    self.log_callback("Downloads cancelados")
                else:
                    stats = self.get_overall_progress()
                    self.log_callback(
                        f"Downloads concluídos! "
                        f"Sucessos: {stats['completed']}, "
                        f"Falhas: {stats['failed']}"
                    )
    
    def _download_single_task(self, task_id: str, task: DownloadTask) -> None:
        """
        Download a single task.
        
        Args:
            task_id: ID of the task
            task: DownloadTask instance
        """
        if self._cancel_event.is_set():
            task.set_status(DownloadStatus.CANCELLED)
            return
        
        try:
            # Update task status
            task.set_status(DownloadStatus.DOWNLOADING)
            self._notify_progress(task_id, {
                'status': 'downloading',
                'progress': 0.0,
                'url': task.url
            })
            
            # Create progress callback for this specific task
            def progress_callback(progress_data):
                if self._cancel_event.is_set():
                    return
                
                # Update task progress based on status
                if progress_data.get('status') == 'downloading':
                    # Calculate progress from bytes
                    downloaded = progress_data.get('downloaded_bytes', 0)
                    total = progress_data.get('total_bytes', 0)
                    if total > 0:
                        progress = (downloaded / total) * 80.0  # 80% for download
                    else:
                        progress = 0.0
                    
                    task.update_progress(progress)
                    
                elif progress_data.get('status') == 'converting':
                    task.set_status(DownloadStatus.CONVERTING)
                    task.update_progress(90.0)  # 90% when converting
                    
                elif progress_data.get('status') == 'completed':
                    task.set_status(DownloadStatus.COMPLETED)
                    task.update_progress(100.0)
                
                # Notify UI
                self._notify_progress(task_id, {
                    'status': task.status.value,
                    'progress': task.progress,
                    'url': task.url,
                    'title': task.title,
                    **progress_data
                })
            
            # Create log callback for this specific task
            def log_callback(message):
                if self.log_callback:
                    self.log_callback(f"[{task_id}] {message}")
            
            # Perform the download
            success = self._downloader.download_single(
                task.url,
                progress_callback=progress_callback,
                log_callback=log_callback,
                cancel_event=self._cancel_event
            )
            
            if success and not self._cancel_event.is_set():
                task.set_status(DownloadStatus.COMPLETED)
                task.update_progress(100.0)
                self._notify_progress(task_id, {
                    'status': 'completed',
                    'progress': 100.0,
                    'url': task.url
                })
            elif self._cancel_event.is_set():
                task.set_status(DownloadStatus.CANCELLED)
            else:
                task.set_status(DownloadStatus.FAILED, "Download failed")
        
        except Exception as e:
            if self._cancel_event.is_set():
                task.set_status(DownloadStatus.CANCELLED)
            else:
                error_msg = str(e)
                task.set_status(DownloadStatus.FAILED, error_msg)
                self._notify_progress(task_id, {
                    'status': 'failed',
                    'progress': task.progress,
                    'url': task.url,
                    'error': error_msg
                })
    
    def _cleanup_resources(self) -> None:
        """Clean up resources after cancellation."""
        try:
            # Shutdown executor if it exists
            if self._executor:
                self._executor.shutdown(wait=False)
            
            # Clear futures
            self._futures.clear()
            
            if self.log_callback:
                self.log_callback("Recursos limpos após cancelamento")
                
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"Erro na limpeza de recursos: {str(e)}")
    
    def _notify_progress(self, task_id: str, progress_data: Dict[str, Any]) -> None:
        """
        Notify progress callback with task information using throttling.
        
        Args:
            task_id: ID of the task
            progress_data: Progress information
        """
        # Use throttled progress updates for better performance
        self._progress_throttler.update_progress(task_id, progress_data)
    
    def _throttled_progress_callback(self, task_id: str, progress_data: Dict[str, Any]) -> None:
        """
        Internal callback for throttled progress updates.
        
        Args:
            task_id: ID of the task
            progress_data: Progress information
        """
        # Record progress callback for performance monitoring
        record_progress_callback()
        
        if self.progress_callback:
            try:
                self.progress_callback(task_id, progress_data)
            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"Erro no callback de progresso: {str(e)}")