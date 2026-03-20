"""
Selenium-based web scraping module
Contains browser automation scripts and helper utilities for job scraping
"""

from .base_scraper import BaseScraper
from .config import PROJECT_ROOT, DATA_DIR, RAW_DATA_DIR, FINAL_DATA_DIR

__all__ = ['BaseScraper', 'PROJECT_ROOT', 'DATA_DIR', 'RAW_DATA_DIR', 'FINAL_DATA_DIR']
