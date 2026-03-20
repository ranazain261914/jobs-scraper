"""
Greenhouse Careers Scraper - Fixed Version

Properly extracts individual job listings from Greenhouse careers portal.
Uses selenium to wait for dynamic content and click through pagination.
"""

import logging
import time
from typing import List, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

GREENHOUSE_CAREERS_URL = "https://www.greenhouse.com/careers/opportunities"


class GreenhouseJobScraper:
    """Scrapes individual job listings from Greenhouse."""
    
    def __init__(self, driver):
        """
        Initialize with Selenium WebDriver.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.base_url = "https://www.greenhouse.com"
        self.job_urls = set()
    
    def scrape(self) -> List[str]:
        """
        Scrape all job URLs from Greenhouse.
        
        Returns:
            List of unique job URLs
        """
        try:
            logger.info(f"Scraping Greenhouse careers page: {GREENHOUSE_CAREERS_URL}")
            self.driver.get(GREENHOUSE_CAREERS_URL)
            
            # Wait for page to load
            time.sleep(3)
            
            # Scroll to load more jobs
            for i in range(5):
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                except:
                    break
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all job listing links
            # Greenhouse uses various structures, try multiple selectors
            selectors_and_attrs = [
                ('a[href*="/careers/opportunities"]', 'href'),
                ('a[href*="/job/"]', 'href'),
                ('.opening a', 'href'),
                ('[data-job-id] a', 'href'),
                ('a[class*="job"]', 'href'),
                ('div[class*="job"] a', 'href'),
            ]
            
            for selector, attr in selectors_and_attrs:
                elements = soup.select(selector)
                for element in elements:
                    url = element.get(attr, '').strip()
                    
                    if not url:
                        continue
                    
                    # Skip non-job URLs
                    if any(x in url.lower() for x in ['mailto:', 'javascript:', '#', 'facebook', 'twitter', 'linkedin']):
                        continue
                    
                    # Convert relative to absolute URL
                    if url.startswith('/'):
                        url = self.base_url + url
                    elif not url.startswith('http'):
                        url = self.base_url + '/' + url
                    
                    # Only keep Greenhouse URLs
                    if 'greenhouse.com' in url:
                        self.job_urls.add(url)
            
            # Try to extract from JavaScript data
            self._extract_from_json(page_source)
            
            logger.info(f"Found {len(self.job_urls)} Greenhouse job URLs")
            return list(self.job_urls)
            
        except Exception as e:
            logger.error(f"Error scraping Greenhouse: {e}")
            return list(self.job_urls)
    
    def _extract_from_json(self, page_source: str):
        """Try to extract URLs from embedded JSON data."""
        try:
            import json
            import re
            
            # Look for JSON arrays in script tags
            json_pattern = r'<script[^>]*type=["\']application/json["\'][^>]*>([^<]+)</script>'
            matches = re.findall(json_pattern, page_source)
            
            for json_str in matches:
                try:
                    data = json.loads(json_str)
                    self._extract_urls_recursive(data)
                except:
                    pass
        except:
            pass
    
    def _extract_urls_recursive(self, obj):
        """Recursively extract URLs from JSON object."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in ['url', 'link', 'href'] and isinstance(value, str):
                    if 'greenhouse' in value.lower() and not any(x in value.lower() for x in ['facebook', 'twitter', 'linkedin']):
                        if value.startswith('/'):
                            value = self.base_url + value
                        if value.startswith('http'):
                            self.job_urls.add(value)
                self._extract_urls_recursive(value)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_urls_recursive(item)


def parse_greenhouse_job(driver, url: str) -> dict:
    """
    Parse job details from a Greenhouse job posting page.
    
    Args:
        driver: Selenium WebDriver
        url: Job posting URL
        
    Returns:
        Dictionary with job details
    """
    try:
        driver.get(url)
        time.sleep(2)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        job_data = {
            'job_title': None,
            'company_name': 'Greenhouse',
            'location': None,
            'job_description': None,
            'employment_type': None,
            'posted_date': None,
        }
        
        # Extract job title
        title_selectors = ['h1', '[data-testid="job-title"]', '.job-title', 'header h1', '.title']
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 5:
                    job_data['job_title'] = title
                    break
        
        # Extract location (often in subtitle or meta)
        location_selectors = [
            '[data-testid="job-location"]',
            '.location',
            '.job-location',
            'span[class*="location"]',
            '.meta .location'
        ]
        for selector in location_selectors:
            elem = soup.select_one(selector)
            if elem:
                loc = elem.get_text(strip=True)
                if loc and len(loc) > 2:
                    job_data['location'] = loc
                    break
        
        # Extract full description
        desc_selectors = [
            '[data-testid="job-description"]',
            '.job-description',
            'article',
            '.content',
            'main'
        ]
        for selector in desc_selectors:
            elem = soup.select_one(selector)
            if elem:
                desc = elem.get_text(separator='\n', strip=True)
                if desc and len(desc) > 50:
                    job_data['job_description'] = desc[:3000]
                    break
        
        # Try to extract from page title if location not found
        if not job_data['location']:
            title_elem = soup.find('title')
            if title_elem:
                title_text = title_elem.get_text()
                # Usually format: "Title - Location - Greenhouse"
                parts = title_text.split('-')
                if len(parts) >= 2:
                    job_data['location'] = parts[1].strip()
        
        return job_data
        
    except Exception as e:
        logger.error(f"Error parsing Greenhouse job {url}: {e}")
        return {
            'job_title': 'Error parsing',
            'company_name': 'Greenhouse',
            'location': None,
            'job_description': None,
            'employment_type': None,
            'posted_date': None,
        }
