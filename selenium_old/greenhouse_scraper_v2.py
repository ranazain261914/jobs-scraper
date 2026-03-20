"""
Fixed Greenhouse Scraper - Extracts ACTUAL individual job postings

Greenhouse job posting URLs follow pattern:
- /job/<job-id>
- /careers/job/<job-id>
- /careers/<company>/job/<job-id>

This scraper:
1. Navigates to careers page
2. Looks for job listing links (not homepage)
3. Extracts actual job posting URLs
"""

import logging
import time
from typing import List, Set
from bs4 import BeautifulSoup
import json
import re

logger = logging.getLogger(__name__)

GREENHOUSE_CAREERS_URL = "https://www.greenhouse.com/careers/opportunities"


class GreenhouseJobScraper:
    """Scrapes REAL individual job listings from Greenhouse."""
    
    def __init__(self, driver):
        """Initialize with Selenium WebDriver."""
        self.driver = driver
        self.base_url = "https://www.greenhouse.com"
        self.job_urls = set()
    
    def scrape(self) -> List[str]:
        """
        Scrape actual job posting URLs from Greenhouse.
        
        Returns:
            List of real job posting URLs (not homepage URLs)
        """
        try:
            logger.info(f"Scraping Greenhouse: {GREENHOUSE_CAREERS_URL}")
            self.driver.get(GREENHOUSE_CAREERS_URL)
            time.sleep(4)
            
            # Scroll down to load job listings
            for i in range(10):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for actual job posting links
            # Real Greenhouse job links have /job/ in the path
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '').strip()
                
                # Skip if empty or non-job URLs
                if not href or 'mailto:' in href or 'javascript:' in href:
                    continue
                
                # Filter for ACTUAL job postings (must have /job/ or /opening/)
                if '/job/' in href or '/opening/' in href:
                    # Convert to absolute URL
                    if not href.startswith('http'):
                        if href.startswith('/'):
                            url = self.base_url + href
                        else:
                            url = self.base_url + '/' + href
                    else:
                        url = href
                    
                    # Only keep Greenhouse URLs
                    if 'greenhouse.com' in url.lower():
                        self.job_urls.add(url)
            
            # Try to extract from embedded API/JSON if any
            self._extract_from_embedded_json(page_source)
            
            # Filter out non-job URLs (remove homepages, career pages, etc.)
            real_job_urls = self._filter_real_jobs(list(self.job_urls))
            
            logger.info(f"Found {len(real_job_urls)} REAL Greenhouse job URLs")
            return real_job_urls
            
        except Exception as e:
            logger.error(f"Error scraping Greenhouse: {e}")
            return []
    
    def _filter_real_jobs(self, urls: List[str]) -> List[str]:
        """Filter to keep only real job posting URLs."""
        real_jobs = []
        for url in urls:
            # Remove portal/home pages
            if any(skip in url.lower() for skip in ['opportunities', '/careers', 'careers/', 'home', 'faq', 'apply']):
                continue
            
            # Keep URLs with /job/ or /opening/
            if '/job/' in url or '/opening/' in url:
                real_jobs.append(url)
        
        return real_jobs
    
    def _extract_from_embedded_json(self, page_source: str):
        """Try to extract job URLs from embedded JSON."""
        try:
            # Look for job data in script tags
            json_pattern = r'"url"\s*:\s*"([^"]*job[^"]*)"'
            matches = re.findall(json_pattern, page_source, re.IGNORECASE)
            
            for match in matches:
                if 'greenhouse.com' in match:
                    self.job_urls.add(match)
        except:
            pass


def parse_greenhouse_job(driver, url: str) -> dict:
    """Parse job details from a real Greenhouse job posting."""
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
        
        # Get job title
        title_elem = soup.find('h1')
        if title_elem:
            job_data['job_title'] = title_elem.get_text(strip=True)
        
        # Get location and other meta info
        meta_elems = soup.find_all('span', class_='meta')
        if meta_elems:
            for meta in meta_elems:
                text = meta.get_text(strip=True).lower()
                if any(loc in text for loc in ['location', 'remote', 'hybrid', 'onsite']):
                    job_data['location'] = meta.get_text(strip=True)
                    break
        
        # Get description
        desc_elem = soup.find('div', class_='content')
        if desc_elem:
            job_data['job_description'] = desc_elem.get_text(separator='\n', strip=True)[:2000]
        
        return job_data
        
    except Exception as e:
        logger.error(f"Error parsing Greenhouse job {url}: {e}")
        return {
            'job_title': None,
            'company_name': 'Greenhouse',
            'location': None,
            'job_description': None,
            'employment_type': None,
            'posted_date': None,
        }
