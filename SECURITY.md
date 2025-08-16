# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Create a Public Issue

Please **do not** create a public GitHub issue for security vulnerabilities. This could put users at risk.

### 2. Report Privately

Send an email to the project maintainers with:
- **Subject**: "Security Vulnerability Report"
- **Description**: Detailed description of the vulnerability
- **Steps to Reproduce**: How to reproduce the issue
- **Impact**: What could an attacker do with this vulnerability
- **Suggested Fix**: If you have ideas for fixing it

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 1 week
- **Fix Timeline**: Depends on severity, typically 2-4 weeks

## Security Considerations

### Application Security

This application:
- **Does not collect personal data**
- **Does not store credentials**
- **Does not transmit data** except for downloading videos
- **Runs locally** on your machine

### Network Security

- All network requests are made directly to YouTube's servers
- No data is sent to third-party servers
- FFmpeg processes are run locally

### File System Security

- Files are only written to the designated downloads folder
- No system files are modified
- No registry changes are made (except for theme preferences)

### Dependencies

We regularly monitor our dependencies for security vulnerabilities:
- **yt-dlp**: Actively maintained YouTube downloader
- **CustomTkinter**: Modern GUI framework
- **Python standard library**: Minimal external dependencies

## Best Practices for Users

### Safe Usage
1. **Download from official sources** only
2. **Verify file integrity** of downloads
3. **Keep the application updated**
4. **Use antivirus software**

### Privacy Protection
1. **Review URLs** before downloading
2. **Be aware of copyright laws**
3. **Don't download sensitive content**

### System Security
1. **Run with standard user privileges** (not administrator)
2. **Keep your system updated**
3. **Use Windows Defender** or equivalent

## Known Security Considerations

### FFmpeg
- We bundle FFmpeg binaries for audio conversion
- FFmpeg is a trusted, widely-used tool
- Binaries are obtained from official sources

### yt-dlp
- We use yt-dlp for YouTube interaction
- This is the most trusted YouTube downloading library
- Regularly updated for security and compatibility

### Network Requests
- The application makes requests to YouTube servers
- No user data is transmitted
- All requests are for legitimate video downloading

## Vulnerability Disclosure

When we receive a security report:

1. **Acknowledge** receipt within 48 hours
2. **Investigate** the reported vulnerability
3. **Develop and test** a fix
4. **Release** a security update
5. **Publish** a security advisory (if appropriate)
6. **Credit** the reporter (if desired)

## Security Updates

Security updates are released as:
- **Patch versions** (e.g., 1.0.1) for minor security fixes
- **Minor versions** (e.g., 1.1.0) for significant security improvements
- **Emergency releases** for critical vulnerabilities

## Contact Information

For security-related questions or reports:
- **Create a private security advisory** on GitHub
- **Email**: (Add your email here)
- **Response time**: Within 48 hours

## Legal

### Responsible Disclosure

We follow responsible disclosure practices:
- We will work with security researchers
- We provide credit for valid reports
- We coordinate public disclosure timing

### Safe Harbor

We will not pursue legal action against security researchers who:
- Follow responsible disclosure practices
- Do not access data beyond what's necessary to demonstrate the vulnerability
- Do not intentionally harm users or the service
- Report vulnerabilities in good faith

---

**Thank you for helping keep YouTube MP3 Downloader secure!**