"""
Simple Job Scraper - Extract REAL job postings from actual job boards

Strategy:
1. Use direct URLs to job boards with actual job listings
2. Extract individual job posting URLs (not portal URLs)
3. Parse job details from each posting

This is a CORRECTED version that targets REAL job postings, not homepages.
"""

import logging
import csv
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Output paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'job_links.csv')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs.csv')


class SimpleJobScraper:
    """Simple scraper for real job postings."""
    
    def __init__(self):
        self.jobs_data = []
        self.job_links = []
    
    def scrape_greenhouse_jobs(self) -> list:
        """
        Scrape REAL job postings from LinkedIn or Indeed (Greenhouse jobs aggregators)
        
        Since Greenhouse shows jobs dynamically, we'll use a different approach:
        Search for actual job posting pages on Greenhouse partner sites.
        """
        logger.info("\n[1/3] Searching for Greenhouse jobs...")
        logger.info("-" * 70)
        
        # Common Greenhouse partner job boards with actual postings
        greenhouse_sources = [
            "https://www.greenhouse.com/jobs",  # If this page lists actual jobs
        ]
        
        jobs_found = []
        
        for url in greenhouse_sources:
            try:
                # Note: Real scraping would require checking actual job boards
                # For now, use hardcoded known Greenhouse job URLs as example
                logger.info(f"Checking {url}...")
                # In real scenario, would parse page for job links here
                
            except Exception as e:
                logger.error(f"Error scraping Greenhouse: {e}")
        
        # Return known example Greenhouse jobs if automatic scraping fails
        # (In production, these would be discovered from the job board)
        logger.info("[WARN] Greenhouse portal doesn't list individual jobs in accessible format")
        logger.info("[INFO] Would need direct access to LinkedIn/Indeed listings or direct URLs")
        
        return []
    
    def scrape_punjab_real_jobs(self) -> list:
        """
        Scrape REAL job postings from Punjab Jobs portal.
        
        Punjab portal has actual job posting URLs:
        https://jobs.punjab.gov.pk/new_recruit/job_detail/<job-slug>
        """
        logger.info("\n[2/3] Scraping REAL Punjab government jobs...")
        logger.info("-" * 70)
        
        jobs_found = []
        
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            
            # Navigate to Punjab jobs listing page
            url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
            logger.info(f"Fetching: {url}")
            driver.get(url)
            time.sleep(3)
            
            # Get page source
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Punjab uses table-based layout for jobs
            # Look for job rows in tables
            job_table = soup.find('table', class_='table')
            
            if job_table:
                rows = job_table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        # Job title is usually in first column
                        title_elem = cols[0].find('a')
                        
                        if title_elem:
                            job_title = title_elem.get_text(strip=True)
                            job_url = title_elem.get('href', '')
                            
                            # Convert relative to absolute URL
                            if job_url and not job_url.startswith('http'):
                                job_url = 'https://jobs.punjab.gov.pk' + job_url
                            
                            if job_url and '/job_detail/' in job_url:
                                jobs_found.append({
                                    'url': job_url,
                                    'source': 'punjab'
                                })
                                logger.info(f"  Found: {job_title[:50]}")
            
            driver.quit()
            logger.info(f"[SUCCESS] Found {len(jobs_found)} Punjab job URLs")
            
        except Exception as e:
            logger.error(f"Error scraping Punjab jobs: {e}")
        
        return jobs_found
    
    def parse_punjab_job(self, driver, url: str) -> dict:
        """Parse details from a Punjab job posting."""
        try:
            driver.get(url)
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            job_data = {
                'job_title': None,
                'company_name': 'Punjab Government',
                'location': 'Punjab, Pakistan',
                'job_description': None,
                'employment_type': 'Full-time',
                'posted_date': None,
                'source': 'punjab',
                'job_url': url,
                'extracted_at': datetime.now().isoformat()
            }
            
            # Extract job title (usually in h1 or h2)
            title_elem = soup.find('h1') or soup.find('h2')
            if title_elem:
                job_data['job_title'] = title_elem.get_text(strip=True)
            
            # Extract description from main content area
            content_area = soup.find('div', class_='content') or soup.find('article') or soup.find('main')
            if content_area:
                job_data['job_description'] = content_area.get_text(separator='\n', strip=True)[:2000]
            
            # If no proper structure found, get body text
            if not job_data['job_description']:
                body = soup.find('body')
                if body:
                    # Remove script and style elements
                    for script in body(['script', 'style']):
                        script.decompose()
                    
                    text = body.get_text(separator='\n', strip=True)
                    if text:
                        job_data['job_description'] = text[:2000]
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing Punjab job {url}: {e}")
            return None
    
    def scrape_all_jobs(self):
        """Scrape all real job postings."""
        logger.info("=" * 70)
        logger.info("REAL JOB SCRAPING - CORRECTED VERSION")
        logger.info("=" * 70)
        
        # Scrape from Punjab (has real individual job URLs)
        punjab_jobs = self.scrape_punjab_real_jobs()
        
        # Extract job details
        if punjab_jobs:
            self._extract_job_details(punjab_jobs)
        
        # Save results
        self.save_to_csv()
        
        # Print summary
        self.print_summary()
    
    def _extract_job_details(self, job_list: list):
        """Extract details from each job URL."""
        logger.info("\n" + "=" * 70)
        logger.info(f"Extracting details from {len(job_list)} jobs...")
        logger.info("=" * 70)
        
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        
        try:
            for idx, job_item in enumerate(job_list, 1):
                url = job_item['url']
                logger.info(f"\n[{idx}/{len(job_list)}] {url[:60]}...")
                
                try:
                    job_data = self.parse_punjab_job(driver, url)
                    
                    if job_data and job_data.get('job_title'):
                        self.jobs_data.append(job_data)
                        logger.info(f"  ✓ {job_data['job_title'][:50]}")
                    else:
                        logger.warning(f"  ✗ Could not extract job title")
                    
                    time.sleep(1)  # Polite delay
                    
                except Exception as e:
                    logger.error(f"  ✗ Error: {str(e)[:100]}")
        
        finally:
            driver.quit()
    
    def save_to_csv(self):
        """Save extracted jobs to CSV."""
        try:
            os.makedirs(os.path.dirname(JOBS_OUTPUT), exist_ok=True)
            
            fieldnames = [
                'job_title', 'company_name', 'location',
                'job_description', 'employment_type', 'posted_date',
                'source', 'job_url', 'extracted_at'
            ]
            
            with open(JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for job in self.jobs_data:
                    row = {field: job.get(field) for field in fieldnames}
                    writer.writerow(row)
            
            logger.info(f"\n[SUCCESS] Saved {len(self.jobs_data)} jobs to {JOBS_OUTPUT}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save: {e}")
    
    def print_summary(self):
        """Print summary."""
        logger.info("\n" + "=" * 70)
        logger.info("SCRAPING SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total jobs extracted: {len(self.jobs_data)}")
        logger.info(f"Output file: {JOBS_OUTPUT}")
        logger.info("=" * 70)


def main():
    """Main execution."""
    scraper = SimpleJobScraper()
    scraper.scrape_all_jobs()


if __name__ == '__main__':
    main()
