"""
Ashby Careers Scraper - Fixed Version

Properly extracts individual job listings from Ashby's careers portal.
Ashby uses a React-based portal with dynamic content loading.
"""

import logging
import time
from typing import List, Set
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

ASHBY_CAREERS_URL = "https://www.ashbyhq.com/careers"


class AshbyJobScraper:
    """Scrapes individual job listings from Ashby."""
    
    def __init__(self, driver):
        """
        Initialize with Selenium WebDriver.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.base_url = "https://www.ashbyhq.com"
        self.job_urls = set()
    
    def scrape(self) -> List[str]:
        """
        Scrape all job URLs from Ashby careers page.
        
        Returns:
            List of unique job URLs
        """
        try:
            logger.info(f"Scraping Ashby careers page: {ASHBY_CAREERS_URL}")
            self.driver.get(ASHBY_CAREERS_URL)
            
            # Wait for page to load and dynamic content to render
            time.sleep(4)
            
            # Scroll to load more jobs
            for i in range(8):
                try:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                except:
                    break
            
            # Get page source
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Ashby job cards typically use these structures
            selectors_and_attrs = [
                ('a[href*="/jobs/"]', 'href'),
                ('a[data-job-id]', 'href'),
                ('[data-testid="job-card"] a', 'href'),
                ('.job-card a', 'href'),
                ('a[class*="job"]', 'href'),
                ('div[class*="job-posting"] a', 'href'),
                ('.JobCard a', 'href'),
                ('a[href*="/careers/"]', 'href'),
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
                    
                    # Only keep Ashby URLs
                    if 'ashby' in url.lower():
                        self.job_urls.add(url)
            
            logger.info(f"Found {len(self.job_urls)} Ashby job URLs")
            return list(self.job_urls)
            
        except Exception as e:
            logger.error(f"Error scraping Ashby: {e}")
            return list(self.job_urls)


def parse_ashby_job(driver, url: str) -> dict:
    """
    Parse job details from an Ashby job posting page.
    
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
            'company_name': 'Ashby',
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
        
        # Extract location
        location_selectors = [
            '[data-testid="job-location"]',
            '.location',
            '.job-location',
            'span[class*="location"]',
            '.meta',
        ]
        for selector in location_selectors:
            elem = soup.select_one(selector)
            if elem:
                loc = elem.get_text(strip=True)
                # Filter out common false positives
                if loc and len(loc) > 2 and 'remote' in loc.lower() or ',' in loc:
                    job_data['location'] = loc
                    break
        
        # Extract description
        desc_selectors = [
            '[data-testid="job-description"]',
            '.job-description',
            'article',
            '.content',
            '.description',
            'main'
        ]
        for selector in desc_selectors:
            elem = soup.select_one(selector)
            if elem:
                desc = elem.get_text(separator='\n', strip=True)
                if desc and len(desc) > 50:
                    job_data['job_description'] = desc[:3000]
                    break
        
        return job_data
        
    except Exception as e:
        logger.error(f"Error parsing Ashby job {url}: {e}")
        return {
            'job_title': 'Error parsing',
            'company_name': 'Ashby',
            'location': None,
            'job_description': None,
            'employment_type': None,
            'posted_date': None,
        }
