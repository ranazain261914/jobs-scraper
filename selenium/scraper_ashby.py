"""
Ashby Kraken Jobs Scraper

Scrapes job listings from https://jobs.ashbyhq.com/kraken.com
Simple and effective approach based on selenium and BeautifulSoup
"""

import logging
import re
import time
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

try:
    from base_scraper import BaseScraper
    from config import WEBSITES, OUTPUT_FILES, TIMEOUTS
except ImportError:
    from selenium.base_scraper import BaseScraper
    from selenium.config import WEBSITES, OUTPUT_FILES, TIMEOUTS


class AshbyScraper(BaseScraper):
    """Scraper for Ashby Kraken Jobs"""
    
    def __init__(self):
        super().__init__(
            source_name='ashby',
            target_url=WEBSITES['ashby']['url']
        )
    
    def extract_job_links(self) -> list:
        """
        Extract job links from Ashby Kraken page
        
        Returns:
            List of job link dictionaries
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("ASHBY KRAKEN JOBS - LINK EXTRACTION")
        self.logger.info("="*80)
        
        job_links = []
        
        try:
            self.driver = self._setup_driver()
            self.logger.info(f"Loading: {self.target_url}")
            self.driver.get(self.target_url)
            
            # Wait for links to appear - up to 15 seconds for JavaScript to render
            self.logger.info("Waiting for job links to load...")
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "a")))
            
            # Pause briefly for animations to settle
            time.sleep(3)
            
            # Find all links on the page
            self.logger.info("Extracting all links...")
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            seen_urls = set()
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    
                    # Only grab links from ashbyhq.com
                    if href and "ashbyhq.com" in href:
                        if href not in seen_urls:
                            seen_urls.add(href)
                            job_links.append({
                                'url': href,
                                'source': 'ashby',
                                'extracted_at': datetime.now().isoformat()
                            })
                except Exception as e:
                    self.logger.debug(f"Error extracting link: {e}")
                    continue
            
            self.logger.info(f"✓ Extracted {len(job_links)} unique job links")
            
        except Exception as e:
            self.logger.error(f"Error extracting Ashby jobs: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        finally:
            self.cleanup()
        
        return job_links
    
    def parse_job_details(self, job_url: str) -> dict:
        """
        Parse job details from individual job page
        
        Args:
            job_url: URL of job posting
            
        Returns:
            Dictionary of job data
        """
        try:
            self.driver.get(job_url)
            time.sleep(1)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            job_data = {
                'job_title': None,
                'company_name': 'Ashby',
                'location': None,
                'job_description': None,
                'employment_type': None,
                'posted_date': None,
                'source': 'ashby',
                'job_url': job_url,
                'department': None,
                'skills': None,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract title
            title_elem = soup.find(['h1', 'h2'])
            if title_elem:
                job_data['job_title'] = title_elem.get_text(strip=True)
            
            # Extract job details from sections
            sections = soup.find_all(['div', 'section'], class_=re.compile('detail|info|meta', re.I))
            
            for section in sections:
                text = section.get_text(strip=True)
                
                # Location
                if 'location' in text.lower() and not job_data['location']:
                    parts = text.split(':')
                    if len(parts) > 1:
                        job_data['location'] = parts[1].strip()[:100]
                
                # Employment type
                if 'employment' in text.lower() or 'type' in text.lower():
                    if not job_data['employment_type']:
                        parts = text.split(':')
                        if len(parts) > 1:
                            job_data['employment_type'] = parts[1].strip()[:100]
            
            # Extract description
            main_content = soup.find('main') or soup.find('article') or soup.find(class_=re.compile('content|description', re.I))
            if main_content:
                # Remove scripts and styles
                for tag in main_content.find_all(['script', 'style']):
                    tag.decompose()
                
                job_data['job_description'] = main_content.get_text(separator=' ', strip=True)[:3000]
            
            return job_data if job_data['job_title'] else None
        
        except Exception as e:
            self.logger.error(f"Error parsing {job_url}: {e}")
            return None


def main():
    """Main entry point for Ashby scraper"""
    scraper = AshbyScraper()
    
    # Phase 1: Extract links
    job_links = scraper.extract_job_links()
    if not job_links:
        scraper.logger.error("Failed to extract job links from Ashby")
        return
    
    # Save links
    links_output = OUTPUT_FILES['ashby']['links']
    scraper.save_links_to_csv(job_links, links_output)
    
    # Phase 2: Parse job details
    scraper.logger.info("\n[PHASE 2/2] PARSING JOB DETAILS")
    scraper.logger.info(f"Will parse {len(job_links)} jobs...")
    
    jobs_data = []
    try:
        scraper.driver = scraper._setup_driver()
        
        for idx, link_data in enumerate(job_links, 1):
            if idx % 5 == 0 or idx == 1:
                scraper.logger.info(f"  Parsing: [{idx}/{len(job_links)}] jobs...")
            
            job_data = scraper.parse_job_details(link_data['url'])
            if job_data:
                jobs_data.append(job_data)
            
            scraper.sleep(TIMEOUTS['between_jobs'])
    finally:
        scraper.cleanup()
    
    # Save jobs
    scraper.logger.info(f"\n✓ Successfully parsed {len(jobs_data)} jobs")
    jobs_output = OUTPUT_FILES['ashby']['jobs']
    scraper.save_jobs_to_csv(jobs_data, jobs_output)
    
    # Summary
    scraper.logger.info("\n" + "="*80)
    scraper.logger.info(f"ASHBY SCRAPER COMPLETE")
    scraper.logger.info("="*80)
    scraper.logger.info(f"  Links extracted: {len(job_links)}")
    scraper.logger.info(f"  Jobs parsed: {len(jobs_data)}")
    if job_links:
        scraper.logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    scraper.logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
