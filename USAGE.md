# 📖 YouTube MP3 Downloader - Usage Guide

Complete guide for using the YouTube MP3 Downloader application.

## 📋 Table of Contents
- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Step-by-Step Guide](#step-by-step-guide)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Tips & Tricks](#tips--tricks)

---

## 🚀 Getting Started

### System Requirements
- **Operating System:** Windows 10 or later
- **RAM:** 4 GB minimum (8 GB recommended)
- **Storage:** 500 MB free space
- **Internet:** Stable connection

### Installation Options

#### Option 1: Executable (Easiest)
1. Download the latest release
2. Extract the ZIP file
3. Run `youtube-mp3-gui.exe`

#### Option 2: Python Source
1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

---

## 🖥️ Interface Overview

### Main Components

#### 1. Header Section
- **Application Title** - "YouTube MP3 Downloader"
- **Theme Toggle** - 🌙/☀️ button to switch between dark/light themes

#### 2. URL Input Area
- **Text Field** - Paste YouTube URLs here (one per line)
- **Placeholder Text** - Helpful instructions when empty

#### 3. Control Buttons (Centered)
- **Download Button** - Start downloading (primary blue button)
- **Cancel Button** - Stop downloads (red button, appears during downloads)

#### 4. Progress Panel
- **General Progress Bar** - Overall download progress
- **Individual Progress Bars** - Progress for each video
- **Log Area** - Real-time status messages and details

#### 5. Status Bar
- **Current Status** - Shows what the application is doing

---

## 📝 Step-by-Step Guide

### Basic Download Process

#### Step 1: Launch Application
- Double-click `youtube-mp3-gui.exe`
- The application opens with a modern interface
- Default theme is dark (can be changed)

#### Step 2: Add YouTube URLs
- Click in the text area (placeholder text disappears)
- Paste your YouTube URLs

**Supported Formats:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/oHg5SJYRHA0
https://youtube.com/watch?v=kJQP7kiw5Fk
```

**Multiple URLs:**
```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

#### Step 3: Start Download
- Click the **"Download"** button (centered in the interface)
- URLs are automatically validated
- Downloads begin immediately for valid URLs

#### Step 4: Monitor Progress
- **General Progress Bar** - Shows overall completion
- **Individual Bars** - Track each video's progress
- **Log Messages** - Detailed information about each step

**Progress Stages:**
- 🔵 **Blue** - Downloading video
- 🟡 **Yellow** - Converting to MP3
- 🟢 **Green** - Completed successfully
- 🔴 **Red** - Error occurred
- ⚫ **Gray** - Cancelled

#### Step 5: Find Your Files
- MP3 files are saved in the `downloads/` folder
- Files are named with the video title
- Quality: 192 kbps MP3 format

### Cancelling Downloads

#### During Download
1. Click the **"Cancel"** button (replaces Download button)
2. Confirm cancellation in the dialog
3. Active downloads stop immediately
4. Partial files are removed

---

## 🎯 Advanced Features

### Theme Switching
- Click the 🌙/☀️ button in the top-right corner
- **Dark Theme** - Easy on the eyes, default setting
- **Light Theme** - Clean, bright interface
- Changes apply instantly

### Responsive Design
The interface adapts to different window sizes:

- **Large Windows (≥550px)** - Full button text and normal spacing
- **Medium Windows (450-550px)** - Compact layout with smaller buttons
- **Small Windows (<450px)** - Icon buttons (▶ for Download, ⏹ for Cancel)

### Concurrent Downloads
- Up to **3 simultaneous downloads** by default
- Downloads are processed in parallel for efficiency
- Each download has its own progress tracking

### Performance Optimization
- **Smart Throttling** - UI updates are optimized to prevent lag
- **Memory Management** - Efficient resource usage
- **Progress Batching** - Smooth progress updates without spam

---

## 🔧 Troubleshooting

### Common Issues

#### "FFmpeg not found"
**Problem:** Missing FFmpeg binaries
**Solution:**
1. Ensure `ffmpeg/` folder exists in the application directory
2. Download FFmpeg from https://ffmpeg.org/download.html
3. Extract `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe` to the `ffmpeg/` folder

#### "No valid YouTube URLs found"
**Possible Causes:**
- Incorrect URL format
- Private or deleted videos
- Regional restrictions

**Solutions:**
- Verify URLs work in your browser
- Use full YouTube URLs: `https://www.youtube.com/watch?v=...`
- Check if videos are publicly available

#### "Network error"
**Solutions:**
- Check internet connection
- Try again in a few minutes
- Verify YouTube is accessible
- Check firewall settings

#### Slow Downloads
**Optimization Tips:**
- Reduce concurrent downloads (close other downloads)
- Close bandwidth-intensive applications
- Check internet speed
- Try downloading during off-peak hours

#### Interface Issues
**Buttons not visible:**
- Resize window to minimum 500x450 pixels
- The interface is now fully responsive and buttons should always be visible

**Application freezing:**
- Wait a few seconds (may be processing)
- If persistent, restart the application
- Check system resources (RAM, CPU)

### Error Messages

#### Download Errors
- **"Video unavailable"** - Video is private, deleted, or restricted
- **"Format not available"** - Try a different video
- **"Connection timeout"** - Network issue, try again

#### Conversion Errors
- **"FFmpeg error"** - Check FFmpeg installation
- **"Audio extraction failed"** - Video may have no audio track

---

## 💡 Tips & Tricks

### For Best Performance
- **Limit concurrent downloads** to 3-5 for optimal speed
- **Close other applications** that use internet bandwidth
- **Use direct video URLs** instead of playlist URLs
- **Ensure stable internet** connection

### File Organization
- Files are saved with **original video titles**
- Create subfolders in `downloads/` to organize by category
- Use bulk rename tools for consistent naming

### Quality Settings
- **Default quality:** 192 kbps MP3 (good balance of quality and size)
- **Format:** MP3 (compatible with all players)
- **Metadata:** Title and basic information preserved

### Keyboard Shortcuts
- **Ctrl+A** - Select all text in URL area
- **Ctrl+V** - Paste URLs
- **Ctrl+C** - Copy selected text
- **Alt+F4** - Close application

### Advanced Usage
- **Batch processing:** Paste multiple URLs for bulk downloads
- **Theme preference:** Your theme choice is remembered
- **Window size:** Application remembers your preferred window size

### Monitoring Downloads
- **Log messages** provide detailed information about each step
- **Progress bars** show both individual and overall progress
- **Status bar** displays current application state
- **Color coding** helps identify download states quickly

---

## 🎵 Audio Quality Information

### Output Specifications
- **Format:** MP3
- **Bitrate:** 192 kbps
- **Sample Rate:** 44.1 kHz
- **Channels:** Stereo (when available)

### File Naming
- Files are named using the original video title
- Special characters are handled automatically
- Maximum filename length is respected

---

## 🔄 Updates and Maintenance

### Keeping Updated
- Check for new releases on GitHub
- Download the latest version for bug fixes and new features
- No automatic updates - manual download required

### Maintenance
- Clear `downloads/` folder periodically to save space
- Check `logs/` folder for troubleshooting information
- FFmpeg binaries rarely need updating

---

## 📞 Getting Help

### Self-Help Resources
1. **Read this guide** thoroughly
2. **Check error messages** in the log area
3. **Try basic troubleshooting** steps

### Reporting Issues
When reporting problems, include:
- **Error message** (exact text)
- **YouTube URL** that caused the issue
- **Steps to reproduce** the problem
- **System information** (Windows version, etc.)

### Community Support
- Check existing GitHub issues
- Search for similar problems
- Create detailed issue reports

---

**Happy downloading! 🎵**

*Remember to respect copyright laws and YouTube's Terms of Service. Only download content you have the right to download.*