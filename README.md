# 🎵 YouTube MP3 Downloader

A modern GUI application for downloading YouTube videos as MP3 files with a sleek, responsive interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🎨 **Modern Interface** - Dark/Light themes with smooth animations
- ⚡ **Concurrent Downloads** - Up to 3 simultaneous downloads
- 📊 **Real-time Progress** - Individual progress bars and detailed logs
- 🛑 **Quick Cancellation** - Stop downloads instantly
- 🎵 **High Quality** - 192 kbps MP3 output
- 📱 **Responsive Design** - Works on any window size
- 🎯 **Centered Layout** - Professional, balanced interface

## 🖼️ Screenshots

### Main Interface
- Clean, modern design with centered buttons
- Real-time progress tracking
- Responsive layout that adapts to window size

### Features Showcase
- **Dark/Light Theme Toggle** - Switch themes with one click
- **Batch Downloads** - Process multiple URLs simultaneously
- **Smart Progress Throttling** - Optimized performance without UI spam

## 🚀 Quick Start

### Option 1: Download Executable (Recommended)
1. Download the latest release from [Releases](../../releases)
2. Extract the ZIP file
3. Run `youtube-mp3-gui.exe`
4. Paste YouTube URLs and click Download!

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-mp3-downloader.git
cd youtube-mp3-downloader

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 3: Build Your Own Executable
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
python build.py
# or
build.bat

# Find executable in dist/youtube-mp3-gui/
```

## 📖 Usage

1. **Launch** the application
2. **Paste YouTube URLs** in the text area (one per line)
3. **Click Download** - the centered button is easy to find!
4. **Monitor Progress** - watch real-time progress bars and logs
5. **Find Your MP3s** - files are saved in the `downloads/` folder

### Supported URL Formats
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/watch?v=VIDEO_ID`

## 🛠️ System Requirements

### Minimum
- **OS:** Windows 10 or later
- **RAM:** 4 GB
- **Storage:** 500 MB free space
- **Internet:** Stable connection

### Recommended
- **RAM:** 8 GB or more
- **Storage:** 2 GB free space (for downloads)
- **Internet:** Broadband connection

## 📁 Project Structure

```
youtube-mp3-downloader/
├── 📄 main.py                    # Main entry point
├── 📄 README.md                  # This file
├── 📄 USAGE.md                   # Detailed usage guide
├── 📄 requirements.txt           # Python dependencies
├── 📄 build.py                   # Build script
├── 📄 build.spec                 # PyInstaller configuration
├── 📂 src/                       # Source code
│   ├── main_window.py           # Main GUI window
│   ├── download_manager.py      # Download coordination
│   ├── youtube_downloader.py    # Core download logic
│   ├── progress_throttler.py    # Performance optimization
│   ├── ui_animations.py         # Smooth animations
│   └── ...                      # Other modules
├── 📂 ffmpeg/                    # FFmpeg binaries (required)
├── 📂 downloads/                 # Downloaded MP3 files
└── 📂 dist/                      # Built executable (after build)
```

## 🔧 Technical Features

### Performance Optimizations
- **Progress Throttling** - Reduces UI updates by 5-10x for smooth performance
- **Concurrent Processing** - Multiple downloads without blocking the UI
- **Memory Efficient** - Smart cleanup and resource management
- **Responsive UI** - Never freezes, even during intensive operations

### User Experience
- **Centered Buttons** - Professional, balanced layout
- **Responsive Design** - Adapts to any window size (minimum 500x450)
- **Smart Animations** - Smooth visual feedback for all actions
- **Theme Support** - Dark and light themes with instant switching

### Architecture
- **Modular Design** - Clean separation of concerns
- **Error Handling** - Comprehensive error management with user-friendly messages
- **Logging System** - Detailed logs for troubleshooting
- **Configuration** - Flexible settings and customization

## 🎯 Advanced Usage

### Multiple Downloads
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/oHg5SJYRHA0
https://www.youtube.com/watch?v=kJQP7kiw5Fk
```

### Performance Tips
- Limit to 3-5 concurrent downloads for optimal speed
- Close other bandwidth-intensive applications
- Use direct video URLs (avoid playlist URLs for better performance)

### Troubleshooting
- **"FFmpeg not found"** - Ensure FFmpeg binaries are in the `ffmpeg/` folder
- **"No valid URLs"** - Check URL format and video availability
- **Slow downloads** - Check internet connection and reduce concurrent downloads

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

This tool is for educational and personal use only. Please respect copyright laws and YouTube's Terms of Service. Only download content you have the right to download.

## 🙏 Acknowledgments

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - Powerful YouTube downloader library
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Modern GUI framework
- **[FFmpeg](https://ffmpeg.org/)** - Audio/video processing

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Usage Guide](USAGE.md)
2. Look through existing [Issues](../../issues)
3. Create a new issue with detailed information

---

**Made with ❤️ using Python and CustomTkinter**

⭐ **Star this repository if you found it helpful!**