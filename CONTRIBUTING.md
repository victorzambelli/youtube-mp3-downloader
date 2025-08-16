# 🤝 Contributing to YouTube MP3 Downloader

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## 📋 Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Guidelines](#code-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic knowledge of Python and GUI development

### Development Environment
1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/youtube-mp3-downloader.git
   cd youtube-mp3-downloader
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🛠️ Development Setup

### Project Structure
```
src/
├── main_window.py           # Main GUI window
├── download_manager.py      # Download coordination
├── youtube_downloader.py    # Core download logic
├── progress_throttler.py    # Performance optimization
├── ui_animations.py         # UI animations
├── theme_manager.py         # Theme management
└── ...                      # Other modules
```

### Running in Development Mode
```bash
python main.py
```

### Building Executable
```bash
python build.py
```

## 📝 Code Guidelines

### Python Style
- Follow **PEP 8** guidelines
- Use **type hints** where possible
- Maximum line length: **88 characters**
- Use **docstrings** for all functions and classes

### Code Example
```python
def download_video(url: str, output_path: str) -> bool:
    """
    Download a video from YouTube and convert to MP3.
    
    Args:
        url: YouTube video URL
        output_path: Path to save the MP3 file
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        DownloadError: If download fails
        ValidationError: If URL is invalid
    """
    # Implementation here
    pass
```

### GUI Development
- Use **CustomTkinter** for all GUI components
- Follow the existing **theme system**
- Ensure **responsive design** principles
- Add **proper error handling**

### Performance Considerations
- Use **progress throttling** for UI updates
- Implement **proper threading** for long operations
- **Clean up resources** properly
- **Test memory usage** under load

## 🔧 Code Quality

### Linting
```bash
# Install development tools
pip install flake8 black mypy

# Format code
black src/

# Check style
flake8 src/

# Type checking
mypy src/
```

### Testing
- Write **unit tests** for new features
- Test **GUI components** with mock data
- Verify **cross-platform compatibility**
- Test **error handling** scenarios

## 📤 Submitting Changes

### Pull Request Process
1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code guidelines

3. **Test thoroughly**:
   - Run the application
   - Test new features
   - Verify existing functionality still works

4. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

### Pull Request Guidelines
- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Reference any related issues**
- **Include screenshots** for UI changes
- **Test instructions** for reviewers

### Commit Message Format
```
type: brief description

Longer description if needed, explaining what and why.

Fixes #123
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

## 🐛 Reporting Issues

### Before Reporting
1. **Search existing issues** to avoid duplicates
2. **Try the latest version** to see if it's already fixed
3. **Gather relevant information**

### Issue Template
```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: Windows 10/11
- Python version: 3.x
- Application version: x.x.x

**Additional Context**
Screenshots, error messages, etc.
```

### Feature Requests
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should it work?

**Alternatives Considered**
Other ways to solve the problem
```

## 🎯 Areas for Contribution

### High Priority
- **Bug fixes** and stability improvements
- **Performance optimizations**
- **UI/UX enhancements**
- **Error handling** improvements

### Medium Priority
- **New features** (with discussion first)
- **Code refactoring**
- **Documentation** improvements
- **Test coverage** expansion

### Low Priority
- **Code style** improvements
- **Minor UI** tweaks
- **Build process** enhancements

## 🏗️ Architecture Guidelines

### Adding New Features
1. **Discuss the feature** in an issue first
2. **Follow existing patterns** in the codebase
3. **Maintain separation of concerns**
4. **Add proper error handling**
5. **Update documentation**

### Modifying Existing Code
1. **Understand the current implementation**
2. **Maintain backward compatibility** when possible
3. **Test thoroughly** after changes
4. **Update related documentation**

## 📚 Resources

### Learning Resources
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [Python GUI Best Practices](https://realpython.com/python-gui-tkinter/)

### Development Tools
- **IDE:** VS Code, PyCharm, or similar
- **Git GUI:** GitHub Desktop, SourceTree, or command line
- **Python Tools:** pip, venv, black, flake8

## 🎉 Recognition

Contributors will be:
- **Listed in the README** (if desired)
- **Credited in release notes**
- **Thanked in the community**

## 📞 Getting Help

### Development Questions
- **Create a discussion** on GitHub
- **Ask in issues** with the "question" label
- **Check existing documentation**

### Code Review
- All pull requests are reviewed
- Feedback is provided constructively
- Multiple iterations are normal

---

**Thank you for contributing to YouTube MP3 Downloader!** 🎵

Your contributions help make this tool better for everyone. Whether it's a bug fix, new feature, or documentation improvement, every contribution is valued and appreciated.