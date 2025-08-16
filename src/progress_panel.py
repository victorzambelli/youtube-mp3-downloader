"""
Progress panel component for YouTube MP3 GUI Downloader.
Provides progress tracking and logging functionality.
"""
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime
import threading
import time
from .models import DownloadTask, DownloadStatus
from .theme_manager import get_theme_manager


class LogLevel(Enum):
    """Log levels for different types of messages."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class ProgressPanel(ctk.CTkFrame):
    """
    Progress panel component that displays download progress and logs.
    
    Features:
    - Scrollable log area with different message types
    - General progress bar for overall progress
    - Individual progress bars for each download task
    - Auto-scroll functionality
    - Message formatting with timestamps and levels
    """
    
    def __init__(self, parent, **kwargs):
        # Get theme manager
        self.theme_manager = get_theme_manager()
        
        # Apply themed styling to kwargs
        themed_kwargs = {
            "fg_color": self.theme_manager.get_color("bg_secondary"),
            "border_color": self.theme_manager.get_color("border"),
            "corner_radius": 8
        }
        themed_kwargs.update(kwargs)
        
        super().__init__(parent, **themed_kwargs)
        
        # Internal state
        self._download_tasks: Dict[str, DownloadTask] = {}
        self._individual_progress_bars: Dict[str, ctk.CTkProgressBar] = {}
        self._lock = threading.Lock()
        
        # Performance optimization
        self._last_log_update = 0
        self._log_update_throttle = 0.1  # 100ms minimum between log updates
        self._pending_log_messages = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # General progress section
        self._create_general_progress_section()
        
        # Log area section
        self._create_log_section()
        
        # Individual progress section
        self._create_individual_progress_section()
    
    def _create_general_progress_section(self):
        """Create the general progress bar section."""
        # General progress frame
        progress_frame = self.theme_manager.create_themed_frame(self)
        progress_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        progress_frame.grid_columnconfigure(1, weight=1)
        
        # General progress label
        self.general_progress_label = self.theme_manager.create_themed_label(
            progress_frame, 
            text="Progresso Geral:",
            font_type="body_bold"
        )
        self.general_progress_label.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        
        # General progress bar
        self.general_progress_bar = ctk.CTkProgressBar(
            progress_frame,
            progress_color=self.theme_manager.get_color("progress_fill"),
            fg_color=self.theme_manager.get_color("progress_bg")
        )
        self.general_progress_bar.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ew")
        self.general_progress_bar.set(0)
        
        # Progress percentage label
        self.progress_percentage_label = self.theme_manager.create_themed_label(
            progress_frame,
            text="0%",
            font_type="body"
        )
        self.progress_percentage_label.grid(row=0, column=2, padx=(5, 10), pady=10, sticky="e")
    
    def _create_log_section(self):
        """Create the scrollable log area section."""
        # Log frame
        log_frame = self.theme_manager.create_themed_frame(self)
        log_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        # Log title
        self.log_title = self.theme_manager.create_themed_label(
            log_frame,
            text="Logs de Progresso:",
            font_type="body_bold"
        )
        self.log_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Create scrollable text widget for logs
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=200,
            font=self.theme_manager.get_font("console"),
            wrap="word",
            fg_color=self.theme_manager.get_color("bg_tertiary"),
            text_color=self.theme_manager.get_color("text_primary"),
            border_color=self.theme_manager.get_color("border")
        )
        self.log_text.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
    
    def _create_individual_progress_section(self):
        """Create the individual progress bars section."""
        # Individual progress frame
        self.individual_frame = self.theme_manager.create_themed_frame(self)
        self.individual_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.individual_frame.grid_columnconfigure(0, weight=1)
        
        # Individual progress title (initially hidden)
        self.individual_title = self.theme_manager.create_themed_label(
            self.individual_frame,
            text="Progresso Individual:",
            font_type="body_bold"
        )
        
        # Scrollable frame for individual progress bars
        self.individual_scroll_frame = ctk.CTkScrollableFrame(
            self.individual_frame,
            height=100,
            fg_color=self.theme_manager.get_color("bg_tertiary"),
            border_color=self.theme_manager.get_color("border")
        )
    
    def log_message(self, message: str, level: LogLevel = LogLevel.INFO):
        """
        Add a message to the log area with timestamp and formatting.
        Uses throttling to prevent log spam and improve performance.
        
        Args:
            message: The message to log
            level: The log level (INFO, WARNING, ERROR, SUCCESS)
        """
        current_time = time.time()
        
        # Add to pending messages
        self._pending_log_messages.append((message, level, current_time))
        
        # Throttle log updates for better performance
        if current_time - self._last_log_update >= self._log_update_throttle:
            self._flush_pending_logs()
        else:
            # Schedule a delayed flush if not already scheduled
            if not hasattr(self, '_log_flush_scheduled') or not self._log_flush_scheduled:
                self._log_flush_scheduled = True
                self.after(int(self._log_update_throttle * 1000), self._flush_pending_logs)
    
    def _flush_pending_logs(self):
        """Flush all pending log messages to the UI."""
        if not self._pending_log_messages:
            return
        
        def _add_logs():
            messages_to_add = self._pending_log_messages.copy()
            self._pending_log_messages.clear()
            self._last_log_update = time.time()
            self._log_flush_scheduled = False
            
            # Batch insert messages for better performance
            log_content = ""
            for message, level, timestamp_float in messages_to_add:
                timestamp = datetime.fromtimestamp(timestamp_float).strftime("%H:%M:%S")
                level_prefix = f"[{level.value.upper()}]"
                log_content += f"{timestamp} {level_prefix} {message}\n"
            
            if log_content:
                # Insert all messages at once
                self.log_text.insert("end", log_content)
                
                # Auto-scroll to bottom
                self.log_text.see("end")
        
        # Ensure thread safety
        try:
            if threading.current_thread() != threading.main_thread():
                self.after(0, _add_logs)
            else:
                _add_logs()
        except RuntimeError:
            # If we can't schedule the callback, just execute directly
            # This can happen during testing when the main loop isn't running
            _add_logs()
    
    def update_general_progress(self, progress: float):
        """
        Update the general progress bar.
        
        Args:
            progress: Progress value between 0.0 and 100.0
        """
        def _update():
            # Normalize progress to 0-1 range for the progress bar
            normalized_progress = max(0.0, min(1.0, progress / 100.0))
            self.general_progress_bar.set(normalized_progress)
            self.progress_percentage_label.configure(text=f"{progress:.1f}%")
        
        # Ensure thread safety
        try:
            if threading.current_thread() != threading.main_thread():
                self.after(0, _update)
            else:
                _update()
        except RuntimeError:
            # If we can't schedule the callback, just execute directly
            # This can happen during testing when the main loop isn't running
            _update()
    
    def add_download_task(self, task: DownloadTask):
        """
        Add a new download task and create its individual progress bar.
        
        Args:
            task: The download task to add
        """
        def _add_task():
            with self._lock:
                self._download_tasks[task.url] = task
                
                # Show individual progress section if first task
                if len(self._download_tasks) == 1:
                    self.individual_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
                    self.individual_scroll_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
                
                # Create individual progress bar
                task_frame = self.theme_manager.create_themed_frame(self.individual_scroll_frame)
                task_frame.grid(row=len(self._individual_progress_bars), column=0, sticky="ew", pady=2)
                task_frame.grid_columnconfigure(1, weight=1)
                
                # Task title (truncated if too long)
                title = task.title if task.title else task.url
                if len(title) > 50:
                    title = title[:47] + "..."
                
                task_label = self.theme_manager.create_themed_label(
                    task_frame,
                    text=title,
                    font_type="small"
                )
                task_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
                
                # Task progress bar
                task_progress = ctk.CTkProgressBar(
                    task_frame, 
                    height=15,
                    progress_color=self.theme_manager.get_color("progress_fill"),
                    fg_color=self.theme_manager.get_color("progress_bg")
                )
                task_progress.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
                task_progress.set(task.progress / 100.0)
                
                # Task status label
                task_status = self.theme_manager.create_themed_label(
                    task_frame,
                    text=task.status.value.upper(),
                    font_type="small"
                )
                task_status.grid(row=0, column=2, padx=(5, 10), pady=5, sticky="e")
                
                # Store references
                self._individual_progress_bars[task.url] = {
                    'frame': task_frame,
                    'progress': task_progress,
                    'status': task_status,
                    'label': task_label
                }
        
        # Ensure thread safety
        try:
            if threading.current_thread() != threading.main_thread():
                self.after(0, _add_task)
            else:
                _add_task()
        except RuntimeError:
            # If we can't schedule the callback, just execute directly
            # This can happen during testing when the main loop isn't running
            _add_task()
    
    def update_download_task(self, url: str, progress: float = None, status: DownloadStatus = None, title: str = None):
        """
        Update an existing download task's progress and status.
        
        Args:
            url: The URL of the task to update
            progress: New progress value (0-100)
            status: New status
            title: New title
        """
        def _update_task():
            with self._lock:
                if url not in self._download_tasks:
                    return
                
                task = self._download_tasks[url]
                progress_bar_info = self._individual_progress_bars.get(url)
                
                if not progress_bar_info:
                    return
                
                # Update task object
                if progress is not None:
                    task.update_progress(progress)
                    progress_bar_info['progress'].set(progress / 100.0)
                
                if status is not None:
                    task.set_status(status)
                    progress_bar_info['status'].configure(text=status.value.upper())
                
                if title is not None:
                    task.title = title
                    display_title = title if len(title) <= 50 else title[:47] + "..."
                    progress_bar_info['label'].configure(text=display_title)
                
                # Update general progress
                self._update_general_progress()
        
        # Ensure thread safety
        try:
            if threading.current_thread() != threading.main_thread():
                self.after(0, _update_task)
            else:
                _update_task()
        except RuntimeError:
            # If we can't schedule the callback, just execute directly
            # This can happen during testing when the main loop isn't running
            _update_task()
    
    def _update_general_progress(self):
        """Calculate and update the general progress based on all tasks."""
        if not self._download_tasks:
            self.update_general_progress(0.0)
            return
        
        total_progress = sum(task.progress for task in self._download_tasks.values())
        average_progress = total_progress / len(self._download_tasks)
        self.update_general_progress(average_progress)
    
    def clear_all_tasks(self):
        """Clear all download tasks and reset the progress panel."""
        def _clear():
            with self._lock:
                # Clear individual progress bars
                for progress_info in self._individual_progress_bars.values():
                    progress_info['frame'].destroy()
                
                self._individual_progress_bars.clear()
                self._download_tasks.clear()
                
                # Hide individual progress section
                self.individual_title.grid_remove()
                self.individual_scroll_frame.grid_remove()
                
                # Reset general progress
                self.update_general_progress(0.0)
                
                # Clear logs
                self.log_text.delete("1.0", "end")
        
        # Ensure thread safety
        try:
            if threading.current_thread() != threading.main_thread():
                self.after(0, _clear)
            else:
                _clear()
        except RuntimeError:
            # If we can't schedule the callback, just execute directly
            # This can happen during testing when the main loop isn't running
            _clear()
    
    def get_download_tasks(self) -> Dict[str, DownloadTask]:
        """Get a copy of all current download tasks."""
        with self._lock:
            return self._download_tasks.copy()
    
    def log_info(self, message: str):
        """Log an info message."""
        self.log_message(message, LogLevel.INFO)
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.log_message(message, LogLevel.WARNING)
    
    def log_error(self, message: str):
        """Log an error message."""
        self.log_message(message, LogLevel.ERROR)
    
    def log_success(self, message: str):
        """Log a success message."""
        self.log_message(message, LogLevel.SUCCESS)
    
    def update_theme(self):
        """Update the progress panel theme when theme changes."""
        # Update main frame colors
        self.configure(
            fg_color=self.theme_manager.get_color("bg_secondary"),
            border_color=self.theme_manager.get_color("border")
        )
        
        # Update progress bar colors
        if hasattr(self, 'general_progress_bar'):
            self.general_progress_bar.configure(
                progress_color=self.theme_manager.get_color("progress_fill"),
                fg_color=self.theme_manager.get_color("progress_bg")
            )
        
        # Update log text colors
        if hasattr(self, 'log_text'):
            self.log_text.configure(
                fg_color=self.theme_manager.get_color("bg_tertiary"),
                text_color=self.theme_manager.get_color("text_primary"),
                border_color=self.theme_manager.get_color("border")
            )
        
        # Update individual scroll frame colors
        if hasattr(self, 'individual_scroll_frame'):
            self.individual_scroll_frame.configure(
                fg_color=self.theme_manager.get_color("bg_tertiary"),
                border_color=self.theme_manager.get_color("border")
            )
        
        # Update individual progress bars
        for progress_info in self._individual_progress_bars.values():
            if 'progress' in progress_info:
                progress_info['progress'].configure(
                    progress_color=self.theme_manager.get_color("progress_fill"),
                    fg_color=self.theme_manager.get_color("progress_bg")
                )