"""
Punjab Jobs Portal Scraper - Fixed Version

Properly extracts job listings from jobs.punjab.gov.pk
This is a traditional ASP.NET portal with table-based job listings.
"""

import logging
import time
from typing import List, Set
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

PUNJAB_JOBS_URL = "https://jobs.punjab.gov.pk/new_recruit/jobs"


class PunjabJobScraper:
    """Scrapes individual job listings from Punjab Jobs portal."""
    
    def __init__(self, driver):
        """
        Initialize with Selenium WebDriver.
        
        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver
        self.base_url = "https://jobs.punjab.gov.pk"
        self.job_urls = set()
    
    def scrape(self) -> List[str]:
        """
        Scrape all job URLs from Punjab Jobs portal.
        
        Returns:
            List of unique job URLs
        """
        try:
            logger.info(f"Scraping Punjab Jobs portal: {PUNJAB_JOBS_URL}")
            self.driver.get(PUNJAB_JOBS_URL)
            
            # Wait for page to load
            time.sleep(3)
            
            # Punjab portal is traditional HTML with pagination
            # Get all pages
            self._scrape_page()
            
            # Try to find and click pagination
            for page in range(2, 10):  # Try up to 10 pages
                try:
                    # Look for next page button
                    next_button = self.driver.find_elements("link text", "Next")
                    if next_button:
                        self.driver.execute_script("arguments[0].click();", next_button[0])
                        time.sleep(2)
                        self._scrape_page()
                    else:
                        break
                except:
                    break
            
            logger.info(f"Found {len(self.job_urls)} Punjab Jobs portal URLs")
            return list(self.job_urls)
            
        except Exception as e:
            logger.error(f"Error scraping Punjab Jobs portal: {e}")
            return list(self.job_urls)
    
    def _scrape_page(self):
        """Scrape current page for job links."""
        try:
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Punjab portal uses table structure for job listings
            selectors_and_attrs = [
                ('table a[href*="job_detail"]', 'href'),
                ('table tr td a', 'href'),
                ('a[href*="/new_recruit/job_detail/"]', 'href'),
                ('.job-link a', 'href'),
                ('a[href*="job"]', 'href'),
            ]
            
            for selector, attr in selectors_and_attrs:
                elements = soup.select(selector)
                for element in elements:
                    url = element.get(attr, '').strip()
                    
                    if not url:
                        continue
                    
                    # Skip non-job URLs
                    if any(x in url.lower() for x in ['mailto:', 'javascript:', '#']):
                        continue
                    
                    # Convert relative to absolute URL
                    if url.startswith('/'):
                        url = self.base_url + url
                    elif not url.startswith('http'):
                        url = self.base_url + '/' + url
                    
                    # Only keep Punjab URLs
                    if 'punjab.gov.pk' in url:
                        self.job_urls.add(url)
                        
        except Exception as e:
            logger.error(f"Error scraping page: {e}")


def parse_punjab_job(driver, url: str) -> dict:
    """
    Parse job details from a Punjab Jobs portal job posting page.
    
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
            'company_name': 'Punjab Government',
            'location': 'Punjab, Pakistan',
            'job_description': None,
            'employment_type': 'Full-time',
            'posted_date': None,
        }
        
        # Extract job title
        title_selectors = ['h1', '.job-title', 'header h1', '.title', 'h2']
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                title = elem.get_text(strip=True)
                if title and len(title) > 5:
                    job_data['job_title'] = title
                    break
        
        # If no title found, try to extract from page content
        if not job_data['job_title']:
            # Punjab portal usually has title in specific format
            content = soup.get_text()
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            for line in lines[:10]:
                if len(line) > 10 and len(line) < 150:
                    job_data['job_title'] = line
                    break
        
        # Extract full description
        desc_selectors = [
            '[data-testid="job-description"]',
            '.job-description',
            '.description',
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
        
        # If no description found with selectors, get main content
        if not job_data['job_description']:
            body = soup.find('body')
            if body:
                # Remove script and style
                for script in body(['script', 'style']):
                    script.decompose()
                desc = body.get_text(separator='\n', strip=True)
                if desc and len(desc) > 100:
                    job_data['job_description'] = desc[:3000]
        
        # Extract posted date if available
        date_selectors = ['time', '.posted-date', '.date', '[data-date]']
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                date_text = elem.get_text(strip=True)
                if date_text:
                    job_data['posted_date'] = date_text
                    break
        
        return job_data
        
    except Exception as e:
        logger.error(f"Error parsing Punjab job {url}: {e}")
        return {
            'job_title': 'Error parsing',
            'company_name': 'Punjab Government',
            'location': 'Punjab, Pakistan',
            'job_description': None,
            'employment_type': 'Full-time',
            'posted_date': None,
        }
