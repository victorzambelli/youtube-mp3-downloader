"""
Main Window for YouTube MP3 GUI Downloader.
Provides the primary user interface for the application.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import List, Dict, Any, Optional, Tuple
import threading
import time
import os

from .progress_panel import ProgressPanel, LogLevel
from .download_manager import DownloadManager
from .url_validator import URLValidator
from .models import DownloadTask, DownloadStatus
from .exceptions import URLValidationError, DownloadError
from .theme_manager import get_theme_manager, ThemeMode
from .ui_animations import get_animator, animate_button_click, animate_error_shake, animate_success_pulse
from .performance_monitor import get_performance_monitor, record_ui_update


class MainWindow(ctk.CTk):
    """
    Main application window using CustomTkinter.
    
    Features:
    - URL input field with scroll support
    - Download/Cancel buttons with visual state management
    - Integrated progress panel
    - Modern, responsive interface
    - Status bar for application state
    """
    
    def __init__(self):
        super().__init__()
        
        # Get theme manager
        self.theme_manager = get_theme_manager()
        
        # Window configuration
        self.title("YouTube MP3 Downloader")
        self.geometry("800x650")  # Slightly smaller default height
        self.minsize(500, 450)    # Smaller minimum size for better compatibility
        
        # Application state
        self.is_downloading = False
        self.download_manager: Optional[DownloadManager] = None
        self._current_window_width = 800
        
        # Animation and performance components
        self._animator = get_animator()
        self._last_progress_update = 0
        self._progress_update_throttle = 0.1  # 100ms minimum between UI updates
        self._performance_monitor = get_performance_monitor()
        
        # Start performance monitoring in debug mode
        if os.getenv('DEBUG_PERFORMANCE', '').lower() == 'true':
            self._performance_monitor.start_monitoring()
            self._performance_monitor.add_warning_callback(self._on_performance_warning)
        
        # Register for theme changes
        self.theme_manager.register_theme_callback(self._on_theme_changed)
        
        # Initialize components
        self._setup_ui()
        self._setup_download_manager()
        
        # Configure window closing behavior
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Bind resize event for responsiveness
        self.bind("<Configure>", self._on_window_resize)
    
    def _setup_ui(self):
        """Set up the user interface components."""
        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Progress panel gets most space (row 3)
        
        # Create main sections
        self._create_header_section()
        self._create_url_input_section()
        self._create_button_section()
        self._create_progress_section()
        self._create_status_bar()
    
    def _create_header_section(self):
        """Create the application header."""
        header_frame = self.theme_manager.create_themed_frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 8))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)
        
        # Application title - responsive
        self.title_label = self.theme_manager.create_themed_label(
            header_frame,
            text="YouTube MP3 Downloader",
            font_type="title"
        )
        self.title_label.grid(row=0, column=0, pady=15, sticky="w", padx=(15, 0))
        
        # Theme toggle button
        self.theme_button = self.theme_manager.create_themed_button(
            header_frame,
            text="🌙" if self.theme_manager.get_current_theme() == ThemeMode.DARK else "☀️",
            command=self._toggle_theme,
            button_type="secondary",
            width=35,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.theme_button.grid(row=0, column=1, pady=15, padx=(0, 15), sticky="e")
    
    def _create_url_input_section(self):
        """Create the URL input section."""
        input_frame = self.theme_manager.create_themed_frame(self)
        input_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # URL input label
        self.url_label = self.theme_manager.create_themed_label(
            input_frame,
            text="URLs dos Vídeos:",
            font_type="subheading"
        )
        self.url_label.grid(row=0, column=0, padx=20, pady=(15, 8), sticky="w")
        
        # URL input text area with scroll - responsive height
        self.url_textbox = ctk.CTkTextbox(
            input_frame,
            height=100,  # Reduced height for better responsiveness
            font=self.theme_manager.get_font("body"),
            wrap="word",
            fg_color=self.theme_manager.get_color("bg_tertiary"),
            text_color=self.theme_manager.get_color("text_primary"),
            border_color=self.theme_manager.get_color("border")
        )
        self.url_textbox.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        # Add placeholder text
        placeholder_text = "Cole aqui as URLs dos vídeos do YouTube (uma por linha)..."
        self.url_textbox.insert("1.0", placeholder_text)
        self.url_textbox.configure(text_color=self.theme_manager.get_color("text_placeholder"))
        
        # Track if placeholder is active
        self._placeholder_active = True
        
        # Bind events for real-time validation feedback and placeholder management
        self.url_textbox.bind("<KeyRelease>", self._on_url_text_changed)
        self.url_textbox.bind("<Button-1>", self._on_url_text_focus)
        self.url_textbox.bind("<FocusIn>", self._on_url_text_focus)
        self.url_textbox.bind("<FocusOut>", self._on_url_text_focus_out)
    
    def _create_button_section(self):
        """Create the button section with centered Download/Cancel buttons."""
        button_frame = self.theme_manager.create_themed_frame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        # Configure grid for centered buttons
        button_frame.grid_columnconfigure(0, weight=1)  # Left spacer
        button_frame.grid_columnconfigure(1, weight=0)  # Download button
        button_frame.grid_columnconfigure(2, weight=0)  # Cancel button  
        button_frame.grid_columnconfigure(3, weight=1)  # Right spacer
        
        # Download button - centered with fixed width
        self.download_button = self.theme_manager.create_themed_button(
            button_frame,
            text="Download",
            command=self._on_download_clicked_animated,
            button_type="primary",
            font=self.theme_manager.get_font("button_large"),
            height=40,
            width=140
        )
        self.download_button.grid(row=0, column=1, padx=(0, 8), pady=15)
        
        # Cancel button (initially hidden) - centered with fixed width
        self.cancel_button = self.theme_manager.create_themed_button(
            button_frame,
            text="Cancelar",
            command=self._on_cancel_clicked_animated,
            button_type="error",
            font=self.theme_manager.get_font("button_large"),
            height=40,
            width=140
        )
        self.cancel_button.grid(row=0, column=2, padx=(8, 0), pady=15)
        self.cancel_button.grid_remove()  # Hide initially
    
    def _create_progress_section(self):
        """Create the progress panel section."""
        # Progress panel (integrated component)
        self.progress_panel = ProgressPanel(self)
        self.progress_panel.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
    
    def _create_status_bar(self):
        """Create the status bar at the bottom."""
        status_frame = self.theme_manager.create_themed_frame(self)
        status_frame.grid(row=4, column=0, sticky="ew", padx=15, pady=(8, 15))
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = self.theme_manager.create_themed_label(
            status_frame,
            text="Status: Pronto",
            font_type="small",
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=8, sticky="w")
    
    def _setup_download_manager(self):
        """Initialize the download manager with callbacks."""
        self.download_manager = DownloadManager(
            progress_callback=self._on_download_progress,
            log_callback=self._on_download_log,
            download_folder="downloads",
            max_concurrent_downloads=3
        )
    
    def _validate_download_environment(self) -> Tuple[bool, str]:
        """
        Validate that the download environment is ready.
        
        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            # Check if downloads directory exists and is writable
            import os
            downloads_dir = "downloads"
            
            if not os.path.exists(downloads_dir):
                try:
                    os.makedirs(downloads_dir, exist_ok=True)
                except Exception as e:
                    return False, f"Não foi possível criar a pasta de downloads: {str(e)}"
            
            # Test write permissions
            test_file = os.path.join(downloads_dir, ".test_write")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except Exception as e:
                return False, f"Sem permissão de escrita na pasta de downloads: {str(e)}"
            
            # Check FFmpeg availability
            from .ffmpeg_service import FFmpegService
            ffmpeg_available, ffmpeg_path = FFmpegService.check_availability()
            if not ffmpeg_available:
                return False, "FFmpeg não encontrado. Verifique se está instalado na pasta 'ffmpeg' ou no sistema."
            
            return True, ""
            
        except Exception as e:
            return False, f"Erro ao validar ambiente: {str(e)}"
    
    def _on_url_text_focus(self, event=None):
        """Handle URL text focus events to manage placeholder."""
        if self._placeholder_active:
            self.url_textbox.delete("1.0", "end")
            self.url_textbox.configure(text_color=self.theme_manager.get_color("text_primary"))
            self._placeholder_active = False
    
    def _on_url_text_focus_out(self, event=None):
        """Handle URL text focus out events to restore placeholder if empty."""
        content = self.url_textbox.get("1.0", "end-1c").strip()
        if not content:
            placeholder_text = "Cole aqui as URLs dos vídeos do YouTube (uma por linha)..."
            self.url_textbox.insert("1.0", placeholder_text)
            self.url_textbox.configure(text_color=self.theme_manager.get_color("text_placeholder"))
            self._placeholder_active = True
    
    def _on_url_text_changed(self, event=None):
        """Handle URL text changes for real-time validation."""
        # Don't validate if placeholder is active
        if self._placeholder_active:
            self.download_button.configure(state="disabled")
            return
        
        # Update button state based on content
        content = self.url_textbox.get("1.0", "end-1c").strip()
        
        if content and not self.is_downloading:
            self.download_button.configure(state="normal")
        else:
            self.download_button.configure(state="disabled")
    
    def _on_download_clicked_animated(self):
        """Handle download button click with animation."""
        if self.is_downloading:
            return
        
        # Animate button click
        animate_button_click(self.download_button, self._on_download_clicked)
    
    def _on_download_clicked(self):
        """Handle download button click."""
        if self.is_downloading:
            return
        
        # Get URLs from text input (skip if placeholder is active)
        if self._placeholder_active:
            messagebox.showwarning("Aviso", "Por favor, insira pelo menos uma URL.")
            return
        
        url_text = self.url_textbox.get("1.0", "end-1c").strip()
        if not url_text:
            messagebox.showwarning("Aviso", "Por favor, insira pelo menos uma URL.")
            return
        
        try:
            # Clear previous progress
            self.progress_panel.clear_all_tasks()
            
            # Validate download environment first
            env_valid, env_error = self._validate_download_environment()
            if not env_valid:
                self.progress_panel.log_error(f"Ambiente inválido: {env_error}")
                messagebox.showerror("Erro de Configuração", env_error)
                self._update_status("Erro de configuração")
                return
            
            # Extract and validate URLs
            urls = URLValidator.extract_urls_from_text(url_text)
            if not urls:
                error_msg = "Nenhuma URL válida do YouTube foi encontrada.\n\nVerifique se as URLs estão no formato correto:\n• https://www.youtube.com/watch?v=...\n• https://youtu.be/..."
                self.progress_panel.log_error("Nenhuma URL válida encontrada")
                
                # Animate error with shake effect
                animate_error_shake(self.url_textbox)
                
                messagebox.showerror("Erro de Validação", error_msg)
                self._update_status("URLs inválidas")
                return
            
            # Log found URLs for user confirmation
            self.progress_panel.log_info(f"Encontradas {len(urls)} URL(s) válida(s) para download")
            
            # Add URLs to download manager
            task_ids = self.download_manager.add_urls([url_text])
            
            # Create download tasks in progress panel
            for task_id in task_ids:
                task = self.download_manager.get_task_status(task_id)
                if task:
                    self.progress_panel.add_download_task(task)
            
            # Update UI state
            self._set_downloading_state(True)
            
            # Start download
            if self.download_manager.start_download():
                self.progress_panel.log_info(f"Iniciando download de {len(urls)} arquivo(s)...")
                self.progress_panel.log_info(f"Pasta de destino: {self.download_manager.download_folder}")
                self._update_status(f"Preparando download de {len(urls)} arquivo(s)...")
            else:
                self._set_downloading_state(False)
                error_msg = "Não foi possível iniciar o download. Verifique se há URLs válidas."
                self.progress_panel.log_error(error_msg)
                messagebox.showerror("Erro", error_msg)
                self._update_status("Erro ao iniciar download")
        
        except URLValidationError as e:
            self.progress_panel.log_error(f"Erro de validação: {str(e)}")
            animate_error_shake(self.url_textbox)
            messagebox.showerror("Erro de Validação", str(e))
            self._update_status("Erro de validação")
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            self.progress_panel.log_error(error_msg)
            animate_error_shake(self.download_button)
            messagebox.showerror("Erro", error_msg)
            self._set_downloading_state(False)
            self._update_status("Erro")
    
    def _on_cancel_clicked_animated(self):
        """Handle cancel button click with animation."""
        if not self.is_downloading:
            return
        
        # Animate button click
        animate_button_click(self.cancel_button, self._on_cancel_clicked)
    
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        if not self.is_downloading:
            return
        
        # Get current download stats for better confirmation message
        stats = self.download_manager.get_overall_progress()
        active_count = stats['active'] + stats['pending']
        
        # Ask for confirmation with specific details
        result = messagebox.askyesno(
            "Confirmar Cancelamento",
            f"Tem certeza que deseja cancelar {active_count} download(s) em progresso?\n\n"
            f"Downloads ativos: {stats['active']}\n"
            f"Downloads pendentes: {stats['pending']}\n\n"
            f"Esta ação não pode ser desfeita e arquivos parcialmente baixados serão perdidos."
        )
        
        if result:
            try:
                # Update UI immediately to show cancellation is in progress
                self.cancel_button.configure(text="Cancelando...", state="disabled")
                self._update_status("Cancelando downloads...")
                
                # Log cancellation request
                self.progress_panel.log_warning("Cancelamento solicitado pelo usuário...")
                self.progress_panel.log_info("Interrompendo downloads em progresso...")
                
                # Cancel downloads
                self.download_manager.cancel_download()
                
                # Schedule UI updates
                self._schedule_cancellation_updates()
                
            except Exception as e:
                error_msg = f"Erro ao cancelar downloads: {str(e)}"
                self.progress_panel.log_error(error_msg)
                messagebox.showerror("Erro", error_msg)
                
                # Reset cancel button on error
                self.cancel_button.configure(text="Cancelar", state="normal")
    
    def _schedule_cancellation_updates(self):
        """Schedule periodic updates during cancellation process."""
        def check_cancellation_progress():
            if not self.is_downloading:
                # Cancellation completed
                self.cancel_button.configure(text="Cancelar", state="normal")
                return
            
            # Check if downloads are still active
            stats = self.download_manager.get_overall_progress()
            active_count = stats['active'] + stats['pending']
            
            if active_count == 0:
                # All downloads cancelled
                self.progress_panel.log_warning("Todos os downloads foram cancelados")
                self._set_downloading_state(False)
                self._update_status("Downloads cancelados")
            else:
                # Still cancelling, check again in 500ms
                # Update cancel button text to show progress
                remaining_text = f"Cancelando... ({active_count})"
                self.cancel_button.configure(text=remaining_text)
                self.after(500, check_cancellation_progress)
        
        # Start checking after a short delay
        self.after(500, check_cancellation_progress)
    
    def _on_download_progress(self, task_id: str, progress_data: Dict[str, Any]):
        """
        Handle download progress updates with throttling for better performance.
        
        Args:
            task_id: ID of the task being updated
            progress_data: Progress information
        """
        # Throttle UI updates for better performance
        current_time = time.time()
        if current_time - self._last_progress_update < self._progress_update_throttle:
            # Skip this update if too frequent, unless it's a status change
            status = progress_data.get('status', '')
            if status not in ['completed', 'failed', 'cancelled', 'converting']:
                return
        
        self._last_progress_update = current_time
        
        # Record UI update for performance monitoring
        record_ui_update()
        
        try:
            url = progress_data.get('url', '')
            status_str = progress_data.get('status', 'unknown')
            progress = progress_data.get('progress', 0.0)
            title = progress_data.get('title', '')
            error = progress_data.get('error', '')
            
            # Convert status string to DownloadStatus enum
            status_mapping = {
                'downloading': DownloadStatus.DOWNLOADING,
                'converting': DownloadStatus.CONVERTING,
                'completed': DownloadStatus.COMPLETED,
                'failed': DownloadStatus.FAILED,
                'cancelled': DownloadStatus.CANCELLED
            }
            
            status = status_mapping.get(status_str, DownloadStatus.PENDING)
            
            # Log status changes for better user feedback
            if status == DownloadStatus.DOWNLOADING and title:
                self.progress_panel.log_info(f"Baixando: {title}")
            elif status == DownloadStatus.CONVERTING:
                self.progress_panel.log_info(f"Convertendo para MP3: {title or url}")
            elif status == DownloadStatus.COMPLETED:
                self.progress_panel.log_success(f"Concluído: {title or url}")
                # Animate success with subtle pulse
                animate_success_pulse(self.progress_panel)
            elif status == DownloadStatus.FAILED:
                error_msg = f"Falha no download: {title or url}"
                if error:
                    error_msg += f" - {error}"
                self.progress_panel.log_error(error_msg)
            elif status == DownloadStatus.CANCELLED:
                self.progress_panel.log_warning(f"Cancelado: {title or url}")
            
            # Update progress panel
            self.progress_panel.update_download_task(
                url=url,
                progress=progress,
                status=status,
                title=title
            )
            
            # Update overall progress
            overall_stats = self.download_manager.get_overall_progress()
            self.progress_panel.update_general_progress(overall_stats['overall_progress'])
            
            # Update status bar with current activity
            if status == DownloadStatus.DOWNLOADING:
                self._update_status(f"Baixando: {title or 'arquivo'}")
            elif status == DownloadStatus.CONVERTING:
                self._update_status(f"Convertendo: {title or 'arquivo'}")
            
            # Check if all downloads are complete
            if status in [DownloadStatus.COMPLETED, DownloadStatus.FAILED, DownloadStatus.CANCELLED]:
                self._check_download_completion()
        
        except Exception as e:
            error_msg = f"Erro ao atualizar progresso: {str(e)}"
            self.progress_panel.log_error(error_msg)
            print(f"Progress callback error: {e}")  # Debug logging
    
    def _on_download_log(self, message: str):
        """
        Handle download log messages.
        
        Args:
            message: Log message to display
        """
        # Determine log level based on message content
        message_lower = message.lower()
        
        # Check for specific error types and provide helpful messages
        if "erro" in message_lower or "falha" in message_lower or "failed" in message_lower:
            # Add helpful context for common errors
            if "network" in message_lower or "connection" in message_lower:
                enhanced_message = f"{message}\nDica: Verifique sua conexão com a internet."
            elif "ffmpeg" in message_lower:
                enhanced_message = f"{message}\nDica: Verifique se o FFmpeg está instalado corretamente."
            elif "private" in message_lower or "unavailable" in message_lower:
                enhanced_message = f"{message}\nDica: O vídeo pode estar privado ou indisponível."
            else:
                enhanced_message = message
            
            self.progress_panel.log_error(enhanced_message)
            
        elif "aviso" in message_lower or "warning" in message_lower:
            self.progress_panel.log_warning(message)
        elif "sucesso" in message_lower or "concluído" in message_lower or "completed" in message_lower:
            self.progress_panel.log_success(message)
        else:
            self.progress_panel.log_info(message)
    
    def _check_download_completion(self):
        """Check if all downloads are complete and update UI accordingly."""
        if not self.download_manager:
            return
        
        stats = self.download_manager.get_overall_progress()
        active_downloads = stats['active'] + stats['pending']
        
        if active_downloads == 0 and self.is_downloading:
            # All downloads are complete
            self._set_downloading_state(False)
            
            # Create comprehensive completion message
            completion_parts = []
            status_parts = []
            
            if stats['completed'] > 0:
                completion_parts.append(f"{stats['completed']} arquivo(s) baixado(s) com sucesso")
                status_parts.append(f"{stats['completed']} concluído(s)")
            
            if stats['failed'] > 0:
                completion_parts.append(f"{stats['failed']} download(s) falharam")
                status_parts.append(f"{stats['failed']} falharam")
            
            if stats['cancelled'] > 0:
                completion_parts.append(f"{stats['cancelled']} download(s) cancelado(s)")
                status_parts.append(f"{stats['cancelled']} cancelado(s)")
            
            # Log final results
            if completion_parts:
                final_message = "Downloads finalizados! " + ", ".join(completion_parts) + "."
                if stats['completed'] > 0 and stats['failed'] == 0 and stats['cancelled'] == 0:
                    self.progress_panel.log_success(final_message)
                elif stats['failed'] > 0 or stats['cancelled'] > 0:
                    self.progress_panel.log_warning(final_message)
                else:
                    self.progress_panel.log_info(final_message)
            
            # Update status bar
            if status_parts:
                status_message = "Finalizado: " + ", ".join(status_parts)
                self._update_status(status_message)
            else:
                self._update_status("Pronto")
            
            # Show completion notification if there were successful downloads
            if stats['completed'] > 0:
                self.progress_panel.log_info(f"Arquivos salvos na pasta: {self.download_manager.download_folder}")
                # Animate overall success
                animate_success_pulse(self.progress_panel)
    
    def _set_downloading_state(self, downloading: bool):
        """
        Update UI state based on downloading status.
        
        Args:
            downloading: True if downloading, False otherwise
        """
        self.is_downloading = downloading
        
        if downloading:
            # Show cancel button, hide download button
            self.download_button.grid_remove()
            self.cancel_button.grid()
            
            # Disable URL input
            self.url_textbox.configure(state="disabled")
            
        else:
            # Show download button, hide cancel button
            self.cancel_button.grid_remove()
            self.download_button.grid()
            
            # Enable URL input
            self.url_textbox.configure(state="normal")
            
            # Update button state based on content
            self._on_url_text_changed()
            
            # Update status
            if not downloading:
                self._update_status("Pronto")
    
    def _update_status(self, status: str):
        """
        Update the status bar text.
        
        Args:
            status: Status message to display
        """
        self.status_label.configure(text=f"Status: {status}")
    
    def _on_closing(self):
        """Handle window closing event."""
        if self.is_downloading:
            stats = self.download_manager.get_overall_progress()
            active_count = stats['active'] + stats['pending']
            
            result = messagebox.askyesno(
                "Confirmar Saída",
                f"Existem {active_count} download(s) em progresso.\n\nDeseja cancelar os downloads e sair da aplicação?"
            )
            
            if result:
                try:
                    if self.download_manager:
                        self.download_manager.cancel_download()
                        self._update_status("Cancelando e fechando...")
                        # Give a moment for cancellation to process
                        self.after(1000, self._force_close)
                    else:
                        self._force_close()
                except Exception as e:
                    print(f"Error during shutdown: {e}")
                    self._force_close()
        else:
            self._force_close()
    
    def _force_close(self):
        """Force close the application."""
        try:
            # Unregister theme callback
            if hasattr(self, 'theme_manager'):
                self.theme_manager.unregister_theme_callback(self._on_theme_changed)
            self.destroy()
        except Exception as e:
            print(f"Error during force close: {e}")
            import sys
            sys.exit(0)
    
    def _toggle_theme(self):
        """Toggle between dark and light themes."""
        self.theme_manager.toggle_theme()
    
    def _on_theme_changed(self):
        """Handle theme change events."""
        # Update theme button icon
        current_theme = self.theme_manager.get_current_theme()
        icon = "🌙" if current_theme == ThemeMode.DARK else "☀️"
        self.theme_button.configure(text=icon)
        
        # Update URL textbox colors
        self.url_textbox.configure(
            fg_color=self.theme_manager.get_color("bg_tertiary"),
            border_color=self.theme_manager.get_color("border")
        )
        
        # Update placeholder text color if active
        if self._placeholder_active:
            self.url_textbox.configure(text_color=self.theme_manager.get_color("text_placeholder"))
        else:
            self.url_textbox.configure(text_color=self.theme_manager.get_color("text_primary"))
        
        # Update progress panel theme
        if hasattr(self, 'progress_panel'):
            self.progress_panel.update_theme()
    
    def _on_window_resize(self, event=None):
        """Handle window resize events for responsive behavior."""
        if event and event.widget == self:
            new_width = event.width
            new_height = event.height
            
            # Update current dimensions
            self._current_window_width = new_width
            
            # Adjust layout for very small windows
            if new_width < 600:
                self._update_compact_layout()
            else:
                self._update_normal_layout()
    
    def _update_compact_layout(self):
        """Update layout for compact/small windows."""
        # Update button text and size for small windows
        if hasattr(self, 'download_button'):
            if self._current_window_width < 450:
                self.download_button.configure(text="▶", width=60)  # Very compact
            elif self._current_window_width < 550:
                self.download_button.configure(text="Download", width=100)  # Compact
            else:
                self.download_button.configure(text="Download", width=140)  # Normal
        
        if hasattr(self, 'cancel_button'):
            if self._current_window_width < 450:
                self.cancel_button.configure(text="⏹", width=60)  # Very compact
            elif self._current_window_width < 550:
                self.cancel_button.configure(text="Cancelar", width=100)  # Compact
            else:
                self.cancel_button.configure(text="Cancelar", width=140)  # Normal
    
    def _update_normal_layout(self):
        """Update layout for normal/large windows."""
        # Restore normal button text and size
        if hasattr(self, 'download_button'):
            self.download_button.configure(text="Download", width=140)
        
        if hasattr(self, 'cancel_button'):
            self.cancel_button.configure(text="Cancelar", width=140)
    
    def _update_responsive_layout(self):
        """Update layout based on current window size."""
        # Get responsive padding
        h_pad, v_pad = self.theme_manager.get_responsive_padding(self._current_window_width)
        
        # Update responsive font sizes for title
        title_size = self.theme_manager.get_responsive_size(
            self._current_window_width,
            {"small": 18, "medium": 22, "large": 24}
        )
        
        # Update title font
        title_font = ctk.CTkFont(family="Roboto", size=title_size, weight="bold")
    
    def _on_performance_warning(self, warning_type: str, details: Dict[str, str]):
        """
        Handle performance warnings from the monitor.
        
        Args:
            warning_type: Type of performance warning
            details: Warning details and suggestions
        """
        if warning_type in ['high_ui_updates', 'high_callbacks']:
            # Automatically adjust throttling for better performance
            if warning_type == 'high_ui_updates':
                self._progress_update_throttle = min(0.2, self._progress_update_throttle * 1.5)
                if self.progress_panel:
                    self.progress_panel._log_update_throttle = min(0.2, 
                        self.progress_panel._log_update_throttle * 1.5)
            
            # Log performance optimization
            if hasattr(self, 'progress_panel') and self.progress_panel:
                self.progress_panel.log_warning(
                    f"Performance: {details.get('description', 'Unknown issue')}"
                )
        
        # In debug mode, print all warnings
        if os.getenv('DEBUG_PERFORMANCE', '').lower() == 'true':
            print(f"Performance Warning [{warning_type}]: {details.get('description', 'Unknown')}")
            print(f"Suggestion: {details.get('suggestion', 'No suggestion')}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics.
        
        Returns:
            Dict with performance statistics
        """
        return self._performance_monitor.get_performance_summary()
        self.title_label.configure(font=title_font)
        
        # Update button sizes
        button_width = self.theme_manager.get_responsive_size(
            self._current_window_width,
            {"small": 120, "medium": 140, "large": 150}
        )
        
        self.download_button.configure(width=button_width)
        self.cancel_button.configure(width=button_width)
        
        # Update textbox height
        textbox_height = self.theme_manager.get_responsive_size(
            self._current_window_width,
            {"small": 100, "medium": 110, "large": 120}
        )
        
        self.url_textbox.configure(height=textbox_height)
        
        # Provide visual feedback for resize
        self._show_resize_feedback()
    
    def _show_resize_feedback(self):
        """Show subtle visual feedback during window resize."""
        # Briefly highlight the window border
        original_bg = self.cget("fg_color")
        
        # Flash effect
        self.configure(fg_color=self.theme_manager.get_color("primary"))
        self.after(100, lambda: self.configure(fg_color=original_bg))
    
    def run(self):
        """Start the application main loop."""
        self.mainloop()


def main():
    """Main entry point for the application."""
    # Ensure downloads directory exists
    os.makedirs("downloads", exist_ok=True)
    
    # Create and run the application
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()