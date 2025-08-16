"""
URL Validator module for YouTube MP3 GUI Downloader.

This module provides functionality to validate YouTube URLs and extract
multiple URLs from text input.
"""

import re
from typing import List, Tuple
from urllib.parse import urlparse, parse_qs
import requests


class URLValidator:
    """Validates YouTube URLs and extracts URLs from text."""
    
    # YouTube URL patterns - video IDs must be exactly 11 characters
    YOUTUBE_PATTERNS = [
        r'^(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:&.*)?$',
        r'^(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})(?:\?.*)?$',
        r'^(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?:\?.*)?$',
        r'^(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})(?:\?.*)?$',
        r'^(?:https?://)?(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:&.*)?$',
    ]
    
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """
        Validate if a URL is a valid YouTube URL.
        
        Args:
            url (str): The URL to validate
            
        Returns:
            bool: True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
            
        url = url.strip()
        if not url:
            return False
            
        # Check against all YouTube patterns
        for pattern in URLValidator.YOUTUBE_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return True
                
        return False
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: Video ID if found, empty string otherwise
        """
        if not URLValidator.is_valid_youtube_url(url):
            return ""
            
        for pattern in URLValidator.YOUTUBE_PATTERNS:
            match = re.match(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return ""
    
    @staticmethod
    def extract_urls_from_text(text: str) -> List[str]:
        """
        Extract multiple YouTube URLs from text input.
        
        Args:
            text (str): Text containing potential YouTube URLs
            
        Returns:
            List[str]: List of valid YouTube URLs found in text
        """
        if not text or not isinstance(text, str):
            return []
            
        urls = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to find URLs in the line
            # First check if the entire line is a URL
            if URLValidator.is_valid_youtube_url(line):
                urls.append(URLValidator._normalize_url(line))
            else:
                # Look for URLs within the line using regex
                # Create search patterns (without ^ and $ anchors)
                search_patterns = [
                    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:&[^\s]*)?',
                    r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})(?:\?[^\s]*)?',
                    r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?:\?[^\s]*)?',
                    r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})(?:\?[^\s]*)?',
                    r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})(?:&[^\s]*)?',
                ]
                for pattern in search_patterns:
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        full_url = match.group(0)
                        if URLValidator.is_valid_youtube_url(full_url):
                            urls.append(URLValidator._normalize_url(full_url))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
                
        return unique_urls
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """
        Normalize YouTube URL to standard format.
        
        Args:
            url (str): YouTube URL to normalize
            
        Returns:
            str: Normalized YouTube URL
        """
        video_id = URLValidator.extract_video_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return url
    
    @staticmethod
    def validate_url_accessibility(url: str, timeout: int = 10) -> Tuple[bool, str]:
        """
        Check if a YouTube URL is accessible (not private, deleted, etc.).
        
        Args:
            url (str): YouTube URL to check
            timeout (int): Request timeout in seconds
            
        Returns:
            Tuple[bool, str]: (is_accessible, error_message)
        """
        if not URLValidator.is_valid_youtube_url(url):
            return False, "Invalid YouTube URL format"
            
        try:
            # Normalize the URL
            normalized_url = URLValidator._normalize_url(url)
            
            # Make a HEAD request to check if the video exists
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.head(normalized_url, headers=headers, timeout=timeout, allow_redirects=True)
            
            if response.status_code == 200:
                return True, ""
            elif response.status_code == 404:
                return False, "Video not found or has been deleted"
            elif response.status_code == 403:
                return False, "Video is private or restricted"
            else:
                return False, f"Video not accessible (HTTP {response.status_code})"
                
        except requests.exceptions.Timeout:
            return False, "Request timeout - check your internet connection"
        except requests.exceptions.ConnectionError:
            return False, "Connection error - check your internet connection"
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    @staticmethod
    def validate_multiple_urls(urls: List[str], check_accessibility: bool = False, timeout: int = 10) -> List[Tuple[str, bool, str]]:
        """
        Validate multiple URLs.
        
        Args:
            urls (List[str]): List of URLs to validate
            check_accessibility (bool): Whether to check URL accessibility
            timeout (int): Request timeout for accessibility checks
            
        Returns:
            List[Tuple[str, bool, str]]: List of (url, is_valid, error_message)
        """
        results = []
        
        for url in urls:
            if not URLValidator.is_valid_youtube_url(url):
                results.append((url, False, "Invalid YouTube URL format"))
                continue
                
            if check_accessibility:
                is_accessible, error_msg = URLValidator.validate_url_accessibility(url, timeout)
                results.append((url, is_accessible, error_msg))
            else:
                results.append((url, True, ""))
                
        return results