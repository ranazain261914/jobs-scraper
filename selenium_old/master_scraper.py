"""
Master Job Scraper - Fixed End-to-End Pipeline

This script properly scrapes jobs from all 3 sites:
1. Extract links from each site's job listings
2. Parse job details from each individual job URL
3. Save to CSV

Usage:
    python master_scraper.py
"""

import logging
import csv
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

# Add selenium package to path
sys.path.insert(0, os.path.dirname(__file__))

from selenium_utils import SeleniumDriver
from greenhouse_scraper_fixed import GreenhouseJobScraper, parse_greenhouse_job
from ashby_scraper_fixed import AshbyJobScraper, parse_ashby_job
from punjab_scraper_fixed import PunjabJobScraper, parse_punjab_job

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'master_scraper.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Output paths
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'job_links_scraped.csv')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs_scraped.csv')


class MasterJobScraper:
    """Master scraper for all job sites."""
    
    def __init__(self):
        """Initialize the scraper."""
        self.all_job_urls = {}
        self.all_jobs = []
        self.failed_urls = []
    
    def scrape_all_links(self):
        """Scrape job listing links from all sites."""
        logger.info("=" * 80)
        logger.info("PHASE 1: EXTRACTING JOB LINKS FROM ALL SITES")
        logger.info("=" * 80)
        
        # 1. Greenhouse
        logger.info("\n[1/3] Scraping Greenhouse...")
        logger.info("-" * 80)
        driver = None
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            scraper = GreenhouseJobScraper(driver)
            greenhouse_links = scraper.scrape()
            self.all_job_urls['greenhouse'] = greenhouse_links
            logger.info(f"[SUCCESS] Greenhouse: Extracted {len(greenhouse_links)} job URLs")
        except Exception as e:
            logger.error(f"[FAILED] Greenhouse scraping: {e}")
            self.all_job_urls['greenhouse'] = []
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            time.sleep(1)
        
        # 2. Ashby
        logger.info("\n[2/3] Scraping Ashby...")
        logger.info("-" * 80)
        driver = None
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            scraper = AshbyJobScraper(driver)
            ashby_links = scraper.scrape()
            self.all_job_urls['ashby'] = ashby_links
            logger.info(f"[SUCCESS] Ashby: Extracted {len(ashby_links)} job URLs")
        except Exception as e:
            logger.error(f"[FAILED] Ashby scraping: {e}")
            self.all_job_urls['ashby'] = []
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            time.sleep(1)
        
        # 3. Punjab Jobs
        logger.info("\n[3/3] Scraping Punjab Jobs Portal...")
        logger.info("-" * 80)
        driver = None
        try:
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            scraper = PunjabJobScraper(driver)
            punjab_links = scraper.scrape()
            self.all_job_urls['punjab'] = punjab_links
            logger.info(f"[SUCCESS] Punjab Jobs: Extracted {len(punjab_links)} job URLs")
        except Exception as e:
            logger.error(f"[FAILED] Punjab Jobs scraping: {e}")
            self.all_job_urls['punjab'] = []
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            time.sleep(1)
        
        # Summary
        total = sum(len(urls) for urls in self.all_job_urls.values())
        logger.info("\n" + "=" * 80)
        logger.info("LINK EXTRACTION SUMMARY")
        logger.info("=" * 80)
        for site, urls in self.all_job_urls.items():
            logger.info(f"{site.upper():20} {len(urls):5} URLs")
        logger.info("-" * 80)
        logger.info(f"{'TOTAL':20} {total:5} URLs")
        logger.info("=" * 80)
        
        return total > 0
    
    def scrape_job_details(self):
        """Scrape job details from all extracted URLs."""
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: EXTRACTING JOB DETAILS FROM URLs")
        logger.info("=" * 80)
        
        # Collect all URLs with their source
        all_urls_list = []
        for site, urls in self.all_job_urls.items():
            for url in urls:
                all_urls_list.append({'url': url, 'source': site})
        
        if not all_urls_list:
            logger.error("No URLs to process!")
            return False
        
        logger.info(f"Processing {len(all_urls_list)} job URLs...\n")
        
        # Create Chrome options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Initialize driver for job detail extraction
        driver = webdriver.Chrome(options=options)
        
        try:
            for idx, item in enumerate(all_urls_list, 1):
                url = item['url']
                source = item['source']
                
                logger.info(f"[{idx}/{len(all_urls_list)}] {source.upper()}: {url[:60]}...")
                
                try:
                    # Parse based on source
                    if source == 'greenhouse':
                        job_data = parse_greenhouse_job(driver, url)
                    elif source == 'ashby':
                        job_data = parse_ashby_job(driver, url)
                    elif source == 'punjab':
                        job_data = parse_punjab_job(driver, url)
                    else:
                        job_data = None
                    
                    if job_data and job_data.get('job_title'):
                        # Add metadata
                        job_data['source'] = source
                        job_data['job_url'] = url
                        job_data['extracted_at'] = datetime.now().isoformat()
                        
                        self.all_jobs.append(job_data)
                        logger.info(f"  [OK] {job_data.get('job_title', 'No title')[:50]}")
                    else:
                        logger.warning(f"  [WARN] Could not extract job title")
                        self.failed_urls.append(url)
                    
                    # Polite delay
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"  [ERROR] {str(e)[:100]}")
                    self.failed_urls.append(url)
                    # Create new driver if one dies
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = webdriver.Chrome(options=options)
                    time.sleep(3)
                    continue
        
        finally:
            try:
                driver.quit()
            except:
                pass
        
        logger.info("\n" + "=" * 80)
        logger.info("JOB DETAIL EXTRACTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total jobs extracted: {len(self.all_jobs)}")
        logger.info(f"Failed extractions:   {len(self.failed_urls)}")
        logger.info("=" * 80)
        
        return len(self.all_jobs) > 0
    
    def save_links_to_csv(self):
        """Save extracted links to CSV."""
        try:
            os.makedirs(os.path.dirname(LINKS_OUTPUT), exist_ok=True)
            
            with open(LINKS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at'])
                writer.writeheader()
                
                for site, urls in self.all_job_urls.items():
                    for url in urls:
                        writer.writerow({
                            'url': url,
                            'source': site,
                            'extracted_at': datetime.now().isoformat()
                        })
            
            logger.info(f"[OK] Saved links to: {LINKS_OUTPUT}")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to save links: {e}")
            return False
    
    def save_jobs_to_csv(self):
        """Save job details to CSV."""
        try:
            os.makedirs(os.path.dirname(JOBS_OUTPUT), exist_ok=True)
            
            fieldnames = [
                'job_title', 'company_name', 'location', 'job_description',
                'employment_type', 'posted_date', 'source', 'job_url', 'extracted_at'
            ]
            
            with open(JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for job in self.all_jobs:
                    # Ensure all fields exist
                    row = {}
                    for field in fieldnames:
                        row[field] = job.get(field, None)
                    writer.writerow(row)
            
            logger.info(f"[OK] Saved {len(self.all_jobs)} jobs to: {JOBS_OUTPUT}")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to save jobs: {e}")
            return False


def main():
    """Main execution."""
    logger.info("Starting Master Job Scraper")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    scraper = MasterJobScraper()
    
    # Phase 1: Extract links
    if scraper.scrape_all_links():
        scraper.save_links_to_csv()
        
        # Phase 2: Extract job details
        if scraper.scrape_job_details():
            scraper.save_jobs_to_csv()
            logger.info("\n[SUCCESS] All phases completed!")
        else:
            logger.error("[ERROR] Job detail extraction failed")
    else:
        logger.error("[ERROR] Link extraction failed")


if __name__ == '__main__':
    main()
