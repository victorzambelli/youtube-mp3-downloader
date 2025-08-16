"""
UI Animation utilities for smooth transitions and visual feedback.
Provides smooth animations for state changes and visual enhancements.
"""
import tkinter as tk
import customtkinter as ctk
import threading
import time
from typing import Callable, Optional, Dict, Any
from enum import Enum


class AnimationType(Enum):
    """Types of animations available."""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    SCALE_IN = "scale_in"
    SCALE_OUT = "scale_out"
    PULSE = "pulse"
    SHAKE = "shake"


class AnimationEasing(Enum):
    """Easing functions for animations."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"


class UIAnimator:
    """
    Provides smooth animations for UI elements.
    
    Features:
    - Multiple animation types (fade, slide, scale, pulse, shake)
    - Configurable easing functions
    - Thread-safe animation execution
    - Animation chaining and callbacks
    """
    
    def __init__(self):
        """Initialize the UI animator."""
        self._active_animations: Dict[str, bool] = {}
        self._animation_lock = threading.Lock()
    
    def animate_fade(
        self,
        widget: ctk.CTkBaseClass,
        target_alpha: float,
        duration: float = 0.3,
        easing: AnimationEasing = AnimationEasing.EASE_OUT,
        callback: Optional[Callable] = None,
        animation_id: Optional[str] = None
    ):
        """
        Animate widget opacity/alpha.
        
        Args:
            widget: Widget to animate
            target_alpha: Target alpha value (0.0 to 1.0)
            duration: Animation duration in seconds
            easing: Easing function to use
            callback: Optional callback when animation completes
            animation_id: Optional unique ID for the animation
        """
        if not hasattr(widget, 'configure'):
            return
        
        animation_id = animation_id or f"fade_{id(widget)}"
        
        # Cancel existing animation for this widget
        self._cancel_animation(animation_id)
        
        def animate():
            try:
                with self._animation_lock:
                    self._active_animations[animation_id] = True
                
                start_time = time.time()
                start_alpha = getattr(widget, '_current_alpha', 1.0)
                alpha_diff = target_alpha - start_alpha
                
                while True:
                    if not self._active_animations.get(animation_id, False):
                        break
                    
                    elapsed = time.time() - start_time
                    progress = min(elapsed / duration, 1.0)
                    
                    # Apply easing
                    eased_progress = self._apply_easing(progress, easing)
                    current_alpha = start_alpha + (alpha_diff * eased_progress)
                    
                    # Update widget alpha (simulate with color changes)
                    try:
                        widget.after(0, lambda: self._update_widget_alpha(widget, current_alpha))
                    except tk.TclError:
                        break  # Widget was destroyed
                    
                    if progress >= 1.0:
                        break
                    
                    time.sleep(0.016)  # ~60 FPS
                
                # Animation complete
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                print(f"Animation error: {e}")
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
        
        # Start animation in separate thread
        threading.Thread(target=animate, daemon=True).start()
    
    def animate_slide(
        self,
        widget: ctk.CTkBaseClass,
        target_x: int,
        target_y: int,
        duration: float = 0.3,
        easing: AnimationEasing = AnimationEasing.EASE_OUT,
        callback: Optional[Callable] = None,
        animation_id: Optional[str] = None
    ):
        """
        Animate widget position.
        
        Args:
            widget: Widget to animate
            target_x: Target X position
            target_y: Target Y position
            duration: Animation duration in seconds
            easing: Easing function to use
            callback: Optional callback when animation completes
            animation_id: Optional unique ID for the animation
        """
        if not hasattr(widget, 'place'):
            return
        
        animation_id = animation_id or f"slide_{id(widget)}"
        
        # Cancel existing animation for this widget
        self._cancel_animation(animation_id)
        
        def animate():
            try:
                with self._animation_lock:
                    self._active_animations[animation_id] = True
                
                start_time = time.time()
                
                # Get current position
                current_info = widget.place_info()
                start_x = int(current_info.get('x', 0))
                start_y = int(current_info.get('y', 0))
                
                x_diff = target_x - start_x
                y_diff = target_y - start_y
                
                while True:
                    if not self._active_animations.get(animation_id, False):
                        break
                    
                    elapsed = time.time() - start_time
                    progress = min(elapsed / duration, 1.0)
                    
                    # Apply easing
                    eased_progress = self._apply_easing(progress, easing)
                    
                    current_x = start_x + (x_diff * eased_progress)
                    current_y = start_y + (y_diff * eased_progress)
                    
                    # Update widget position
                    try:
                        widget.after(0, lambda x=current_x, y=current_y: widget.place(x=x, y=y))
                    except tk.TclError:
                        break  # Widget was destroyed
                    
                    if progress >= 1.0:
                        break
                    
                    time.sleep(0.016)  # ~60 FPS
                
                # Animation complete
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                print(f"Animation error: {e}")
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
        
        # Start animation in separate thread
        threading.Thread(target=animate, daemon=True).start()
    
    def animate_pulse(
        self,
        widget: ctk.CTkBaseClass,
        pulse_count: int = 3,
        pulse_duration: float = 0.2,
        intensity: float = 0.3,
        callback: Optional[Callable] = None,
        animation_id: Optional[str] = None
    ):
        """
        Create a pulsing animation effect.
        
        Args:
            widget: Widget to animate
            pulse_count: Number of pulses
            pulse_duration: Duration of each pulse
            intensity: Pulse intensity (0.0 to 1.0)
            callback: Optional callback when animation completes
            animation_id: Optional unique ID for the animation
        """
        animation_id = animation_id or f"pulse_{id(widget)}"
        
        # Cancel existing animation for this widget
        self._cancel_animation(animation_id)
        
        def animate():
            try:
                with self._animation_lock:
                    self._active_animations[animation_id] = True
                
                for pulse in range(pulse_count):
                    if not self._active_animations.get(animation_id, False):
                        break
                    
                    # Pulse in
                    self._animate_scale_step(widget, 1.0 + intensity, pulse_duration / 2, animation_id)
                    time.sleep(pulse_duration / 2)
                    
                    if not self._active_animations.get(animation_id, False):
                        break
                    
                    # Pulse out
                    self._animate_scale_step(widget, 1.0, pulse_duration / 2, animation_id)
                    time.sleep(pulse_duration / 2)
                
                # Animation complete
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                print(f"Animation error: {e}")
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
        
        # Start animation in separate thread
        threading.Thread(target=animate, daemon=True).start()
    
    def animate_shake(
        self,
        widget: ctk.CTkBaseClass,
        intensity: int = 5,
        duration: float = 0.5,
        callback: Optional[Callable] = None,
        animation_id: Optional[str] = None
    ):
        """
        Create a shaking animation effect.
        
        Args:
            widget: Widget to animate
            intensity: Shake intensity in pixels
            duration: Animation duration in seconds
            callback: Optional callback when animation completes
            animation_id: Optional unique ID for the animation
        """
        if not hasattr(widget, 'place'):
            return
        
        animation_id = animation_id or f"shake_{id(widget)}"
        
        # Cancel existing animation for this widget
        self._cancel_animation(animation_id)
        
        def animate():
            try:
                with self._animation_lock:
                    self._active_animations[animation_id] = True
                
                start_time = time.time()
                
                # Get original position
                original_info = widget.place_info()
                original_x = int(original_info.get('x', 0))
                original_y = int(original_info.get('y', 0))
                
                import random
                
                while True:
                    if not self._active_animations.get(animation_id, False):
                        break
                    
                    elapsed = time.time() - start_time
                    if elapsed >= duration:
                        break
                    
                    # Calculate shake offset
                    progress = elapsed / duration
                    current_intensity = intensity * (1.0 - progress)  # Fade out shake
                    
                    offset_x = random.randint(-int(current_intensity), int(current_intensity))
                    offset_y = random.randint(-int(current_intensity), int(current_intensity))
                    
                    shake_x = original_x + offset_x
                    shake_y = original_y + offset_y
                    
                    # Update widget position
                    try:
                        widget.after(0, lambda x=shake_x, y=shake_y: widget.place(x=x, y=y))
                    except tk.TclError:
                        break  # Widget was destroyed
                    
                    time.sleep(0.016)  # ~60 FPS
                
                # Return to original position
                try:
                    widget.after(0, lambda: widget.place(x=original_x, y=original_y))
                except tk.TclError:
                    pass
                
                # Animation complete
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                print(f"Animation error: {e}")
                with self._animation_lock:
                    self._active_animations.pop(animation_id, None)
        
        # Start animation in separate thread
        threading.Thread(target=animate, daemon=True).start()
    
    def _animate_scale_step(
        self, 
        widget: ctk.CTkBaseClass, 
        target_scale: float, 
        duration: float, 
        animation_id: str
    ):
        """Helper method for scale animation steps."""
        # This is a simplified scale effect using configure
        # In a real implementation, you might use widget transformations
        try:
            if hasattr(widget, 'configure'):
                # Simulate scaling with size changes for buttons
                if hasattr(widget, '_original_width'):
                    original_width = widget._original_width
                    original_height = widget._original_height
                else:
                    original_width = widget.cget('width') if hasattr(widget, 'cget') else 100
                    original_height = widget.cget('height') if hasattr(widget, 'cget') else 30
                    widget._original_width = original_width
                    widget._original_height = original_height
                
                new_width = int(original_width * target_scale)
                new_height = int(original_height * target_scale)
                
                widget.after(0, lambda: widget.configure(width=new_width, height=new_height))
        except Exception:
            pass  # Ignore errors in scale animation
    
    def _update_widget_alpha(self, widget: ctk.CTkBaseClass, alpha: float):
        """Helper method to simulate alpha changes."""
        # Store current alpha for future reference
        widget._current_alpha = alpha
        
        # For CustomTkinter widgets, we can simulate alpha with color intensity
        # This is a simplified approach - real alpha would require more complex implementation
        try:
            if hasattr(widget, 'configure') and alpha < 1.0:
                # Simulate transparency by adjusting colors (simplified)
                pass  # In a full implementation, you'd adjust colors based on alpha
        except Exception:
            pass  # Ignore errors in alpha simulation
    
    def _apply_easing(self, progress: float, easing: AnimationEasing) -> float:
        """
        Apply easing function to animation progress.
        
        Args:
            progress: Linear progress (0.0 to 1.0)
            easing: Easing function to apply
            
        Returns:
            float: Eased progress value
        """
        if easing == AnimationEasing.LINEAR:
            return progress
        elif easing == AnimationEasing.EASE_IN:
            return progress * progress
        elif easing == AnimationEasing.EASE_OUT:
            return 1 - (1 - progress) * (1 - progress)
        elif easing == AnimationEasing.EASE_IN_OUT:
            if progress < 0.5:
                return 2 * progress * progress
            else:
                return 1 - 2 * (1 - progress) * (1 - progress)
        elif easing == AnimationEasing.BOUNCE:
            if progress < 0.5:
                return 2 * progress * progress
            else:
                return 1 - 2 * (1 - progress) * (1 - progress) * abs(1 - 2 * progress)
        else:
            return progress
    
    def _cancel_animation(self, animation_id: str):
        """Cancel an active animation."""
        with self._animation_lock:
            if animation_id in self._active_animations:
                self._active_animations[animation_id] = False
    
    def cancel_all_animations(self):
        """Cancel all active animations."""
        with self._animation_lock:
            for animation_id in list(self._active_animations.keys()):
                self._active_animations[animation_id] = False
    
    def is_animating(self, animation_id: str) -> bool:
        """Check if a specific animation is active."""
        with self._animation_lock:
            return self._active_animations.get(animation_id, False)
    
    def get_active_animations(self) -> list:
        """Get list of active animation IDs."""
        with self._animation_lock:
            return [aid for aid, active in self._active_animations.items() if active]


# Global animator instance
_global_animator = None


def get_animator() -> UIAnimator:
    """Get the global UI animator instance."""
    global _global_animator
    if _global_animator is None:
        _global_animator = UIAnimator()
    return _global_animator


def animate_button_click(button: ctk.CTkButton, callback: Optional[Callable] = None):
    """
    Animate a button click with a quick scale effect.
    
    Args:
        button: Button to animate
        callback: Optional callback after animation
    """
    animator = get_animator()
    animator.animate_pulse(
        button, 
        pulse_count=1, 
        pulse_duration=0.1, 
        intensity=0.1, 
        callback=callback
    )


def animate_error_shake(widget: ctk.CTkBaseClass, callback: Optional[Callable] = None):
    """
    Animate an error with a shake effect.
    
    Args:
        widget: Widget to shake
        callback: Optional callback after animation
    """
    animator = get_animator()
    animator.animate_shake(
        widget, 
        intensity=3, 
        duration=0.3, 
        callback=callback
    )


def animate_success_pulse(widget: ctk.CTkBaseClass, callback: Optional[Callable] = None):
    """
    Animate success with a gentle pulse effect.
    
    Args:
        widget: Widget to pulse
        callback: Optional callback after animation
    """
    animator = get_animator()
    animator.animate_pulse(
        widget, 
        pulse_count=2, 
        pulse_duration=0.15, 
        intensity=0.15, 
        callback=callback
    )