"""
Progress throttling utility for optimizing UI updates.
Prevents excessive progress callback spam that can slow down the UI.
"""
import time
import threading
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, field


@dataclass
class ThrottledProgress:
    """Container for throttled progress data."""
    last_update_time: float = field(default_factory=time.time)
    last_progress: float = 0.0
    pending_data: Optional[Dict[str, Any]] = None
    update_scheduled: bool = False


class ProgressThrottler:
    """
    Throttles progress updates to prevent UI spam while maintaining responsiveness.
    
    Features:
    - Configurable minimum update interval
    - Automatic batching of rapid updates
    - Thread-safe operation
    - Smart throttling based on progress change significance
    """
    
    def __init__(
        self, 
        min_interval: float = 0.2,  # Minimum 200ms between updates
        min_progress_change: float = 3.0,  # Minimum 3% progress change
        force_update_interval: float = 2.0  # Force update every 2 seconds
    ):
        """
        Initialize the progress throttler.
        
        Args:
            min_interval: Minimum time between updates in seconds
            min_progress_change: Minimum progress change percentage to trigger update
            force_update_interval: Maximum time to wait before forcing an update
        """
        self.min_interval = min_interval
        self.min_progress_change = min_progress_change
        self.force_update_interval = force_update_interval
        
        self._progress_data: Dict[str, ThrottledProgress] = {}
        self._lock = threading.Lock()
        self._callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
    
    def set_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Set the callback function for throttled updates."""
        self._callback = callback
    
    def update_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """
        Update progress for a task with throttling.
        
        Args:
            task_id: Unique identifier for the task
            progress_data: Progress information dictionary
        """
        if not self._callback:
            return
        
        current_time = time.time()
        current_progress = progress_data.get('progress', 0.0)
        
        with self._lock:
            # Get or create throttled progress entry
            if task_id not in self._progress_data:
                self._progress_data[task_id] = ThrottledProgress()
            
            throttled = self._progress_data[task_id]
            
            # Store the latest data
            throttled.pending_data = progress_data.copy()
            
            # Check if we should update immediately
            should_update = self._should_update_immediately(
                throttled, current_time, current_progress
            )
            
            if should_update and not throttled.update_scheduled:
                # Update immediately
                self._perform_update(task_id, throttled, current_time, current_progress)
            elif not throttled.update_scheduled:
                # Schedule a delayed update
                self._schedule_delayed_update(task_id, throttled)
    
    def _should_update_immediately(
        self, 
        throttled: ThrottledProgress, 
        current_time: float, 
        current_progress: float
    ) -> bool:
        """
        Determine if an update should be performed immediately.
        
        Args:
            throttled: Throttled progress data
            current_time: Current timestamp
            current_progress: Current progress value
            
        Returns:
            bool: True if update should be immediate
        """
        time_since_last = current_time - throttled.last_update_time
        progress_change = abs(current_progress - throttled.last_progress)
        
        # Check for important status changes that should update immediately
        status_changed = False
        important_status = False
        
        if throttled.pending_data:
            current_status = throttled.pending_data.get('status', 'downloading')
            # Important statuses that should update immediately
            important_status = current_status in ['completed', 'failed', 'cancelled', 'converting']
            # Any status change from downloading
            status_changed = current_status != 'downloading'
        
        # Update immediately if:
        # 1. Important status change (completed, failed, etc.)
        # 2. Enough time has passed since last update AND significant progress change
        # 3. Too much time has passed (force update)
        return (
            important_status or
            (time_since_last >= self.min_interval and progress_change >= self.min_progress_change) or
            time_since_last >= self.force_update_interval
        )
    
    def _perform_update(
        self, 
        task_id: str, 
        throttled: ThrottledProgress, 
        current_time: float, 
        current_progress: float
    ):
        """
        Perform the actual progress update.
        
        Args:
            task_id: Task identifier
            throttled: Throttled progress data
            current_time: Current timestamp
            current_progress: Current progress value
        """
        if throttled.pending_data and self._callback:
            try:
                self._callback(task_id, throttled.pending_data)
                throttled.last_update_time = current_time
                throttled.last_progress = current_progress
                throttled.update_scheduled = False
            except Exception as e:
                print(f"Error in throttled progress callback: {e}")
    
    def _schedule_delayed_update(self, task_id: str, throttled: ThrottledProgress):
        """
        Schedule a delayed update for the task.
        
        Args:
            task_id: Task identifier
            throttled: Throttled progress data
        """
        throttled.update_scheduled = True
        
        def delayed_update():
            time.sleep(self.min_interval)
            
            with self._lock:
                if task_id in self._progress_data:
                    current_throttled = self._progress_data[task_id]
                    if current_throttled.update_scheduled and current_throttled.pending_data:
                        current_progress = current_throttled.pending_data.get('progress', 0.0)
                        self._perform_update(
                            task_id, 
                            current_throttled, 
                            time.time(), 
                            current_progress
                        )
        
        # Run delayed update in a separate thread
        threading.Thread(target=delayed_update, daemon=True).start()
    
    def force_update(self, task_id: str):
        """
        Force an immediate update for a specific task.
        
        Args:
            task_id: Task identifier to force update
        """
        with self._lock:
            if task_id in self._progress_data:
                throttled = self._progress_data[task_id]
                if throttled.pending_data:
                    current_progress = throttled.pending_data.get('progress', 0.0)
                    self._perform_update(task_id, throttled, time.time(), current_progress)
    
    def force_update_all(self):
        """Force immediate updates for all tasks."""
        with self._lock:
            for task_id in list(self._progress_data.keys()):
                throttled = self._progress_data[task_id]
                if throttled.pending_data:
                    current_progress = throttled.pending_data.get('progress', 0.0)
                    self._perform_update(task_id, throttled, time.time(), current_progress)
    
    def clear_task(self, task_id: str):
        """
        Clear throttling data for a completed task.
        
        Args:
            task_id: Task identifier to clear
        """
        with self._lock:
            self._progress_data.pop(task_id, None)
    
    def clear_all(self):
        """Clear all throttling data."""
        with self._lock:
            self._progress_data.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get throttling statistics.
        
        Returns:
            Dict with throttling statistics
        """
        with self._lock:
            return {
                'active_tasks': len(self._progress_data),
                'scheduled_updates': sum(
                    1 for t in self._progress_data.values() 
                    if t.update_scheduled
                ),
                'min_interval': self.min_interval,
                'min_progress_change': self.min_progress_change,
                'force_update_interval': self.force_update_interval
            }