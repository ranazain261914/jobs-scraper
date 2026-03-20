"""
Selenium-based web scraping module for job listing extraction.

This module provides tools for extracting job links from multiple websites:
- Greenhouse careers portal
- Ashby job listing platform
- Punjab government jobs portal
"""

# Avoid circular imports - don't import at module level
# These can be imported directly from selenium_utils and utils modules as needed

__all__ = [
    'SeleniumDriver',
    'add_delay',
    'is_valid_url',
    'check_url_accessible',
    'normalize_url',
    'clean_text',
    'remove_duplicates'
]

__version__ = '1.0.0'
