"""
OPTIMIZED Job Scraper - Reuses single Chrome instance for all jobs

Key improvements:
1. Single Chrome instance for all jobs (much faster, fewer connection errors)
2. Proper structured data extraction from table
3. Smart job description parsing (extracts only the description section)
4. Proper error handling and graceful fallbacks
"""

import logging
import csv
import os
import time
import re
from datetime import datetime
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs.csv')


def extract_jobs_optimized():
    """Extract job links and parse details using a SINGLE Chrome instance."""
    
    logger.info("\n[JOB SCRAPER STARTING]")
    logger.info("=" * 70)
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    jobs_data = []
    
    try:
        # STEP 1: Extract job URLs from listing page
        logger.info("\n[STEP 1] Extracting job posting URLs...")
        url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
        logger.info(f"Loading: {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_table = soup.find('table', class_='table')
        
        job_links = []
        if job_table:
            rows = job_table.find_all('tr')[1:]
            logger.info(f"Found {len(rows)} job rows in listing")
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 1:
                    title_elem = cols[0].find('a')
                    if title_elem and title_elem.get('href'):
                        href = title_elem.get('href', '')
                        if '/job_detail/' in href:
                            full_url = 'https://jobs.punjab.gov.pk' + href if not href.startswith('http') else href
                            job_links.append(full_url)
        
        logger.info(f"[SUCCESS] Extracted {len(job_links)} job URLs\n")
        
        # STEP 2: Parse each job using the SAME Chrome instance
        logger.info(f"[STEP 2] Parsing details from {len(job_links)} jobs...")
        
        for idx, job_url in enumerate(job_links, 1):
            try:
                logger.info(f"  [{idx}/{len(job_links)}] Parsing: {job_url}")
                
                driver.get(job_url)
                wait = WebDriverWait(driver, 10)
                try:
                    wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))
                except:
                    pass
                
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                job_data = {
                    'job_title': None,
                    'company_name': 'Punjab Government',
                    'location': 'Punjab, Pakistan',
                    'job_description': None,
                    'employment_type': 'Full-time',
                    'posted_date': None,
                    'source': 'punjab',
                    'job_url': job_url,
                    'extracted_at': datetime.now().isoformat()
                }
                
                # Parse structured table data
                all_tds = soup.find_all('td')
                job_details = {}
                
                for i in range(0, len(all_tds)-1, 2):
                    try:
                        label = all_tds[i].get_text(strip=True).lower()
                        value = all_tds[i+1].get_text(strip=True)
                        job_details[label] = value
                        
                        # Map to job fields
                        if 'role' in label or 'position' in label:
                            if not job_data['job_title']:
                                job_data['job_title'] = value
                        elif 'district' in label and value:
                            job_data['location'] = f"{value}, Punjab, Pakistan"
                        elif 'employment' in label or 'status' in label:
                            job_data['employment_type'] = value
                        elif 'posted' in label and 'date' in label:
                            job_data['posted_date'] = value
                    except:
                        pass
                
                # Extract job description
                full_text = soup.get_text()
                
                if 'Job Description' in full_text:
                    desc_start = full_text.index('Job Description') + len('Job Description')
                    description_text = full_text[desc_start:]
                    
                    # Remove footer sections
                    for marker in ['Job Responsibilities', 'Apply for this Job', 'Sitemap', 'Important Note', 'Degree Level', 'Requirement']:
                        if marker in description_text:
                            idx = description_text.index(marker)
                            description_text = description_text[:idx]
                    
                    description_text = re.sub(r'\s+', ' ', description_text).strip()
                    if description_text and len(description_text) > 20:
                        job_data['job_description'] = description_text[:2000]
                
                # Try to get proper title from h1/h2 if structured one is bad
                if not job_data['job_title'] or job_data['job_title'] in ['1', '2', '3', '4', '5']:
                    page_title = soup.find('h1') or soup.find('h2')
                    if page_title:
                        title_text = page_title.get_text(strip=True)
                        # Clean: remove company name and numbers
                        title_text = re.sub(r'Punjab.*Authority|PAKISTAN|PLRA', '', title_text, flags=re.IGNORECASE).strip()
                        title_text = re.sub(r'^[\d\s\-]+', '', title_text).strip()
                        title_text = re.sub(r'\s*-\s*,\s*$', '', title_text).strip()  # Remove trailing " - ,"
                        if title_text and len(title_text) > 3:
                            job_data['job_title'] = title_text
                
                # Clean up title one more time
                if job_data['job_title']:
                    job_data['job_title'] = re.sub(r'\s*-\s*,\s*$', '', job_data['job_title']).strip()
                
                jobs_data.append(job_data)
                logger.info(f"       → {job_data['job_title']}")
                
            except Exception as e:
                logger.error(f"       ERROR parsing {job_url}: {e}")
                continue
        
        logger.info(f"\n[SUCCESS] Extracted {len(jobs_data)} complete job records\n")
        
    finally:
        driver.quit()
    
    # STEP 3: Save to CSV
    if jobs_data:
        os.makedirs(os.path.dirname(JOBS_OUTPUT), exist_ok=True)
        
        try:
            with open(JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'job_title',
                    'company_name',
                    'location',
                    'job_description',
                    'employment_type',
                    'posted_date',
                    'source',
                    'job_url',
                    'extracted_at'
                ])
                writer.writeheader()
                writer.writerows(jobs_data)
            
            logger.info(f"[SAVED] {len(jobs_data)} jobs → {JOBS_OUTPUT}")
            logger.info("=" * 70 + "\n")
        
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")


if __name__ == '__main__':
    extract_jobs_optimized()
