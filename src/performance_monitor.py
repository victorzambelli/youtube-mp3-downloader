"""
Performance monitoring utilities for the YouTube MP3 GUI Downloader.
Provides tools to monitor and optimize application performance.
"""
import time
import threading
import os
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque

# Optional psutil import for system metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    thread_count: int
    ui_update_count: int = 0
    progress_callback_count: int = 0


class PerformanceMonitor:
    """
    Monitors application performance and provides optimization insights.
    
    Features:
    - CPU and memory usage tracking
    - UI update frequency monitoring
    - Progress callback frequency tracking
    - Performance bottleneck detection
    - Automatic optimization suggestions
    """
    
    def __init__(self, max_history: int = 300):  # 5 minutes at 1-second intervals
        """
        Initialize the performance monitor.
        
        Args:
            max_history: Maximum number of metrics to keep in history
        """
        self.max_history = max_history
        self._metrics_history: deque = deque(maxlen=max_history)
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Counters for tracking
        self._ui_update_count = 0
        self._progress_callback_count = 0
        self._last_reset_time = time.time()
        
        # Performance thresholds
        self.cpu_warning_threshold = 80.0  # %
        self.memory_warning_threshold = 500.0  # MB
        self.ui_update_warning_rate = 100  # updates per second
        self.progress_callback_warning_rate = 50  # callbacks per second
        
        # Callbacks for warnings
        self._warning_callbacks: List[Callable[[str, Dict], None]] = []
    
    def start_monitoring(self, interval: float = 1.0):
        """
        Start performance monitoring.
        
        Args:
            interval: Monitoring interval in seconds
        """
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
    
    def add_warning_callback(self, callback: Callable[[str, Dict], None]):
        """
        Add a callback for performance warnings.
        
        Args:
            callback: Function to call with (warning_type, details)
        """
        self._warning_callbacks.append(callback)
    
    def record_ui_update(self):
        """Record a UI update event."""
        with self._lock:
            self._ui_update_count += 1
    
    def record_progress_callback(self):
        """Record a progress callback event."""
        with self._lock:
            self._progress_callback_count += 1
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """
        Get current performance metrics.
        
        Returns:
            PerformanceMetrics: Current performance data
        """
        try:
            with self._lock:
                current_time = time.time()
                time_elapsed = current_time - self._last_reset_time
                
                ui_rate = self._ui_update_count / time_elapsed if time_elapsed > 0 else 0
                callback_rate = self._progress_callback_count / time_elapsed if time_elapsed > 0 else 0
                
                # Get system metrics if psutil is available
                cpu_percent = 0.0
                memory_mb = 0.0
                thread_count = 0
                
                if PSUTIL_AVAILABLE:
                    try:
                        process = psutil.Process(os.getpid())
                        cpu_percent = process.cpu_percent()
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        thread_count = process.num_threads()
                    except Exception:
                        pass  # Use default values if psutil fails
                
                metrics = PerformanceMetrics(
                    timestamp=current_time,
                    cpu_percent=cpu_percent,
                    memory_mb=memory_mb,
                    thread_count=thread_count,
                    ui_update_count=ui_rate,
                    progress_callback_count=callback_rate
                )
                
                return metrics
                
        except Exception as e:
            print(f"Error getting performance metrics: {e}")
            return PerformanceMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_mb=0.0,
                thread_count=0
            )
    
    def get_metrics_history(self) -> List[PerformanceMetrics]:
        """
        Get performance metrics history.
        
        Returns:
            List[PerformanceMetrics]: Historical performance data
        """
        with self._lock:
            return list(self._metrics_history)
    
    def get_performance_summary(self) -> Dict[str, float]:
        """
        Get a summary of performance metrics.
        
        Returns:
            Dict with performance summary statistics
        """
        with self._lock:
            if not self._metrics_history:
                return {}
            
            cpu_values = [m.cpu_percent for m in self._metrics_history]
            memory_values = [m.memory_mb for m in self._metrics_history]
            thread_values = [m.thread_count for m in self._metrics_history]
            ui_update_values = [m.ui_update_count for m in self._metrics_history]
            callback_values = [m.progress_callback_count for m in self._metrics_history]
            
            return {
                'avg_cpu_percent': sum(cpu_values) / len(cpu_values),
                'max_cpu_percent': max(cpu_values),
                'avg_memory_mb': sum(memory_values) / len(memory_values),
                'max_memory_mb': max(memory_values),
                'avg_thread_count': sum(thread_values) / len(thread_values),
                'max_thread_count': max(thread_values),
                'avg_ui_update_rate': sum(ui_update_values) / len(ui_update_values),
                'max_ui_update_rate': max(ui_update_values),
                'avg_callback_rate': sum(callback_values) / len(callback_values),
                'max_callback_rate': max(callback_values),
                'monitoring_duration': time.time() - self._last_reset_time
            }
    
    def detect_performance_issues(self) -> List[Dict[str, str]]:
        """
        Detect potential performance issues.
        
        Returns:
            List of detected issues with descriptions and suggestions
        """
        issues = []
        current_metrics = self.get_current_metrics()
        summary = self.get_performance_summary()
        
        # Check CPU usage
        if current_metrics.cpu_percent > self.cpu_warning_threshold:
            issues.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'description': f'High CPU usage: {current_metrics.cpu_percent:.1f}%',
                'suggestion': 'Consider reducing progress update frequency or optimizing download threads'
            })
        
        # Check memory usage
        if current_metrics.memory_mb > self.memory_warning_threshold:
            issues.append({
                'type': 'high_memory',
                'severity': 'warning',
                'description': f'High memory usage: {current_metrics.memory_mb:.1f} MB',
                'suggestion': 'Check for memory leaks or reduce concurrent downloads'
            })
        
        # Check UI update rate
        if current_metrics.ui_update_count > self.ui_update_warning_rate:
            issues.append({
                'type': 'high_ui_updates',
                'severity': 'performance',
                'description': f'High UI update rate: {current_metrics.ui_update_count:.1f}/sec',
                'suggestion': 'Implement better UI update throttling'
            })
        
        # Check progress callback rate
        if current_metrics.progress_callback_count > self.progress_callback_warning_rate:
            issues.append({
                'type': 'high_callbacks',
                'severity': 'performance',
                'description': f'High callback rate: {current_metrics.progress_callback_count:.1f}/sec',
                'suggestion': 'Implement progress callback throttling'
            })
        
        # Check for excessive threads
        if current_metrics.thread_count > 20:
            issues.append({
                'type': 'high_threads',
                'severity': 'warning',
                'description': f'High thread count: {current_metrics.thread_count}',
                'suggestion': 'Review thread pool configuration and cleanup'
            })
        
        return issues
    
    def get_optimization_suggestions(self) -> List[str]:
        """
        Get optimization suggestions based on current performance.
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        summary = self.get_performance_summary()
        
        if not summary:
            return suggestions
        
        # UI update optimization
        if summary.get('max_ui_update_rate', 0) > 50:
            suggestions.append(
                "Consider implementing UI update batching to reduce update frequency"
            )
        
        # Progress callback optimization
        if summary.get('max_callback_rate', 0) > 30:
            suggestions.append(
                "Implement progress callback throttling to improve performance"
            )
        
        # Memory optimization
        if summary.get('max_memory_mb', 0) > 300:
            suggestions.append(
                "Monitor memory usage and implement cleanup for completed downloads"
            )
        
        # Thread optimization
        if summary.get('max_thread_count', 0) > 15:
            suggestions.append(
                "Review thread pool size and ensure proper thread cleanup"
            )
        
        return suggestions
    
    def reset_counters(self):
        """Reset performance counters."""
        with self._lock:
            self._ui_update_count = 0
            self._progress_callback_count = 0
            self._last_reset_time = time.time()
    
    def _monitor_loop(self, interval: float):
        """Main monitoring loop."""
        while self._monitoring:
            try:
                # Collect metrics
                metrics = self.get_current_metrics()
                
                with self._lock:
                    self._metrics_history.append(metrics)
                
                # Check for performance issues
                issues = self.detect_performance_issues()
                for issue in issues:
                    self._notify_warning(issue['type'], issue)
                
                # Reset counters periodically
                if time.time() - self._last_reset_time > 60:  # Reset every minute
                    self.reset_counters()
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error in performance monitoring: {e}")
                time.sleep(interval)
    
    def _notify_warning(self, warning_type: str, details: Dict):
        """Notify warning callbacks."""
        for callback in self._warning_callbacks:
            try:
                callback(warning_type, details)
            except Exception as e:
                print(f"Error in warning callback: {e}")


# Global performance monitor instance
_global_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def start_performance_monitoring():
    """Start global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.start_monitoring()


def stop_performance_monitoring():
    """Stop global performance monitoring."""
    monitor = get_performance_monitor()
    monitor.stop_monitoring()


def record_ui_update():
    """Record a UI update for performance tracking."""
    monitor = get_performance_monitor()
    monitor.record_ui_update()


def record_progress_callback():
    """Record a progress callback for performance tracking."""
    monitor = get_performance_monitor()
    monitor.record_progress_callback()