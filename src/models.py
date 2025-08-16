"""
Data models for YouTube MP3 GUI Downloader.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DownloadStatus(Enum):
    """Enum representing the different states of a download task."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    CONVERTING = "converting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class DownloadTask:
    """Represents a single download task with its current state and progress."""
    url: str
    title: str = ""
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    error_message: str = ""
    
    def __post_init__(self):
        """Validate the download task after initialization."""
        if not self.url:
            raise ValueError("URL cannot be empty")
        if not (0.0 <= self.progress <= 100.0):
            raise ValueError("Progress must be between 0.0 and 100.0")
    
    def update_progress(self, progress: float) -> None:
        """Update the progress of the download task."""
        if not (0.0 <= progress <= 100.0):
            raise ValueError("Progress must be between 0.0 and 100.0")
        self.progress = progress
    
    def set_status(self, status: DownloadStatus, error_message: str = "") -> None:
        """Update the status of the download task."""
        self.status = status
        if status == DownloadStatus.FAILED and error_message:
            self.error_message = error_message
        elif status != DownloadStatus.FAILED:
            self.error_message = ""
    
    def is_active(self) -> bool:
        """Check if the download task is currently active (downloading or converting)."""
        return self.status in [DownloadStatus.DOWNLOADING, DownloadStatus.CONVERTING]
    
    def is_completed(self) -> bool:
        """Check if the download task has completed successfully."""
        return self.status == DownloadStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if the download task has failed."""
        return self.status == DownloadStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """Check if the download task was cancelled."""
        return self.status == DownloadStatus.CANCELLED