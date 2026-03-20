"""
Greenhouse Jobs Scraper

Scrapes job listings from https://www.greenhouse.com/careers/opportunities
"""

import logging
import re
import time
from datetime import datetime
from pathlib import Path

from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
from config import WEBSITES, OUTPUT_FILES, TIMEOUTS


class GreenhouseScraper(BaseScraper):
    """Scraper for Greenhouse careers page"""
    
    def __init__(self):
        super().__init__(
            source_name='greenhouse',
            target_url=WEBSITES['greenhouse']['url']
        )
    
    def extract_job_links(self) -> list:
        """
        Extract all job links from Greenhouse careers page
        
        Returns:
            List of job link dictionaries
        """
        self.logger.info("\n" + "="*80)
        self.logger.info("GREENHOUSE JOBS - LINK EXTRACTION")
        self.logger.info("="*80)
        
        try:
            self.driver = self._setup_driver()
            self.load_page()
            
            # Wait for jobs to load
            self.logger.info("[STEP 1] Waiting for jobs to load...")
            time.sleep(4)  # Let React render
            
            # Try to find a "load more" button and click it
            self.logger.info("[STEP 2] Checking for load more button...")
            self._load_all_jobs()
            
            # Get page source
            page_source = self.get_page_source()
            if not page_source:
                return []
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract job links
            self.logger.info("[STEP 3] Extracting job links...")
            job_links = self._extract_links_from_soup(soup)
            
            self.logger.info(f"\n✓ Extracted {len(job_links)} job links from Greenhouse")
            return job_links
        
        except Exception as e:
            self.logger.error(f"Error in extract_job_links: {e}")
            return []
        finally:
            self.cleanup()
    
    def _load_all_jobs(self):
        """Load all jobs by clicking load more button if present"""
        try:
            max_attempts = 5
            for attempt in range(max_attempts):
                # Look for "load more" button
                load_more_buttons = self.driver.find_elements(
                    By.XPATH,
                    "//button[contains(text(), 'Load more') or contains(text(), 'load more')]"
                )
                
                if not load_more_buttons:
                    self.logger.info("  No more jobs to load")
                    break
                
                self.logger.info(f"  Clicking load more button (attempt {attempt + 1})...")
                load_more_buttons[0].click()
                time.sleep(2)
        except Exception as e:
            self.logger.debug(f"Note: {e}")
    
    def _extract_links_from_soup(self, soup: BeautifulSoup) -> list:
        """Extract job links from parsed HTML"""
        job_links = []
        seen_urls = set()
        
        # Strategy 1: Look for job sections/cards
        # Greenhouse typically uses divs with job information
        job_sections = soup.find_all('div', class_=re.compile('job', re.I))
        self.logger.info(f"  Found {len(job_sections)} potential job sections")
        
        for section in job_sections:
            links = section.find_all('a', href=True)
            for link in links:
                href = link.get('href', '').strip()
                text = link.get_text(strip=True)
                
                # Validate link
                if not href or len(text) < 3:
                    continue
                
                # Normalize URL
                href = self._normalize_url(href)
                
                if href and href not in seen_urls:
                    seen_urls.add(href)
                    job_links.append({
                        'url': href,
                        'source': 'greenhouse',
                        'extracted_at': datetime.now().isoformat()
                    })
        
        # Strategy 2: If few links found, try broader search
        if len(job_links) < 3:
            self.logger.info("  Using fallback strategy to find job links...")
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href', '').strip()
                text = link.get_text(strip=True)
                
                # Look for job-related links
                if any(keyword in href.lower() for keyword in ['job', 'opportunity', 'position']):
                    if len(text) >= 3 and not any(skip in text.lower() for skip in ['all jobs', 'categories']):
                        href = self._normalize_url(href)
                        
                        if href and href not in seen_urls:
                            seen_urls.add(href)
                            job_links.append({
                                'url': href,
                                'source': 'greenhouse',
                                'extracted_at': datetime.now().isoformat()
                            })
        
        return job_links
    
    def _normalize_url(self, url: str) -> str:
        """Normalize job URL"""
        url = url.strip()
        
        if url.startswith('/'):
            return 'https://www.greenhouse.com' + url
        elif url.startswith('http'):
            return url
        else:
            return None
    
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
            
            # Wait for content to load
            time.sleep(1)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            job_data = {
                'job_title': None,
                'company_name': 'Greenhouse',
                'location': None,
                'job_description': None,
                'employment_type': None,
                'posted_date': None,
                'source': 'greenhouse',
                'job_url': job_url,
                'department': None,
                'skills': None,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract title
            title_elem = soup.find('h1')
            if title_elem:
                job_data['job_title'] = title_elem.get_text(strip=True)
            
            # Extract job details from meta sections
            sections = soup.find_all('div', class_=re.compile('detail|section', re.I))
            for section in sections:
                text = section.get_text(strip=True)
                
                # Location
                if 'location' in text.lower() and not job_data['location']:
                    parts = text.split(':')
                    if len(parts) > 1:
                        job_data['location'] = parts[1].strip()
                
                # Employment type
                if 'type' in text.lower() and not job_data['employment_type']:
                    parts = text.split(':')
                    if len(parts) > 1:
                        job_data['employment_type'] = parts[1].strip()
            
            # Extract job description
            main_content = soup.find('main') or soup.find('article') or soup.find(class_=re.compile('content|description', re.I))
            if main_content:
                job_data['job_description'] = main_content.get_text(strip=True)[:2000]
            
            return job_data if job_data['job_title'] else None
        
        except Exception as e:
            self.logger.error(f"Error parsing {job_url}: {e}")
            return None


def main():
    """Main entry point for Greenhouse scraper"""
    scraper = GreenhouseScraper()
    
    # Phase 1: Extract links
    job_links = scraper.extract_job_links()
    if not job_links:
        scraper.logger.error("Failed to extract job links")
        return
    
    # Save links
    links_output = OUTPUT_FILES['greenhouse']['links']
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
    jobs_output = OUTPUT_FILES['greenhouse']['jobs']
    scraper.save_jobs_to_csv(jobs_data, jobs_output)
    
    # Summary
    scraper.logger.info("\n" + "="*80)
    scraper.logger.info(f"GREENHOUSE SCRAPER COMPLETE")
    scraper.logger.info("="*80)
    scraper.logger.info(f"  Links extracted: {len(job_links)}")
    scraper.logger.info(f"  Jobs parsed: {len(jobs_data)}")
    if job_links:
        scraper.logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    scraper.logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
