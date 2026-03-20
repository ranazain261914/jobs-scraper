"""
CORRECTED Job Scraper - Properly extracts job details from Punjab portal

Issues fixed:
1. Previous scraper grabbed raw HTML including JavaScript error messages
2. Job title and company name were being concatenated
3. Job description contained entire page text with navigation menus

Solution:
- Use CSS/XPath to target specific job detail elements
- Wait for JavaScript to render
- Parse structured HTML properly instead of raw text extraction
"""

import logging
import csv
import os
import time
import re
import sys
from datetime import datetime

# Remove local selenium folder from path to avoid shadowing the real selenium package
sys.path = [p for p in sys.path if 'selenium' not in p.lower() or 'site-packages' in p.lower()]

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs.csv')


def extract_job_links():
    """Extract individual job posting URLs from Punjab portal."""
    logger.info("\n[STEP 1] Extracting job posting URLs from Punjab portal...")
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    job_links = []
    
    try:
        url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
        logger.info(f"Loading: {url}")
        driver.get(url)
        
        # Wait for table to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find job table
        job_table = soup.find('table', class_='table')
        if not job_table:
            logger.error("Could not find job table")
            return []
        
        rows = job_table.find_all('tr')[1:]  # Skip header
        logger.info(f"Found {len(rows)} job rows")
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 1:
                title_elem = cols[0].find('a')
                if title_elem and title_elem.get('href'):
                    href = title_elem.get('href', '')
                    if '/job_detail/' in href:
                        full_url = 'https://jobs.punjab.gov.pk' + href if not href.startswith('http') else href
                        job_links.append({
                            'url': full_url,
                            'source': 'punjab',
                            'extracted_at': datetime.now().isoformat()
                        })
        
        logger.info(f"[SUCCESS] Extracted {len(job_links)} job URLs")
        
    finally:
        driver.quit()
    
    return job_links


def parse_single_job(url: str) -> dict:
    """Parse a single job posting page - CORRECTED VERSION"""
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        logger.info(f"Parsing: {url}")
        driver.get(url)
        
        # Wait for content to load
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "td")))
        except:
            pass
        
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
        
        # PROPER PARSING: Look for table-based job details structure
        # The Punjab portal uses tables with labels and values
        
        # Method 1: Extract from table rows (label: value format)
        job_details = {}
        all_tds = soup.find_all('td')
        
        # Process td elements - every other pair is label:value
        for i in range(0, len(all_tds)-1, 2):
            label_elem = all_tds[i]
            value_elem = all_tds[i+1]
            
            label = label_elem.get_text(strip=True).lower()
            value = value_elem.get_text(strip=True)
            
            # Store extracted values
            job_details[label] = value
            
            # Map to job_data fields
            if 'role' in label or 'position' in label:
                if not job_data['job_title']:
                    job_data['job_title'] = value
            
            if 'district' in label:
                if value and value != 'Punjab, Pakistan':
                    job_data['location'] = f"{value}, Punjab, Pakistan"
            
            if 'employment' in label or 'status' in label:
                job_data['employment_type'] = value
            
            if 'date' in label or 'posted' in label:
                job_data['posted_date'] = value
        
        # If no title found, try to get from page heading
        if not job_data['job_title']:
            page_title = soup.find('h1') or soup.find('h2')
            if page_title:
                title_text = page_title.get_text(strip=True)
                # Clean up - might have extra text
                job_data['job_title'] = re.sub(r'[^a-zA-Z0-9\s\(\)\-]', '', title_text).strip()
        
        # Extract job description from job details dict
        description_parts = []
        for key, val in job_details.items():
            if key not in ['role', 'position', 'salary', 'monthly salary']:
                description_parts.append(f"{key}: {val}")
        
        if description_parts:
            job_data['job_description'] = '\n'.join(description_parts)[:2000]
        
        # Fallback: if still no description, get from paragraphs
        if not job_data['job_description']:
            paras = soup.find_all('p')
            if paras:
                text_parts = [p.get_text(strip=True) for p in paras if p.get_text(strip=True)]
                job_data['job_description'] = '\n'.join(text_parts)[:2000]
        
        return job_data
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None
    finally:
        driver.quit()


def main():
    """Extract all job links, then parse each job."""
    # Step 1: Get job URLs
    job_links = extract_job_links()
    
    # Step 2: Parse each job
    jobs_data = []
    logger.info(f"\n[STEP 2] Parsing details from {len(job_links)} job postings...")
    
    for idx, job_link_data in enumerate(job_links, 1):
        job_data = parse_single_job(job_link_data['url'])
        if job_data:
            jobs_data.append(job_data)
            logger.info(f"  [{idx}/{len(job_links)}] {job_data.get('job_title', 'Unknown')}")
    
    logger.info(f"\n[SUCCESS] Extracted {len(jobs_data)} job records")
    
    # Step 3: Save to CSV
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
            
            logger.info(f"Saved {len(jobs_data)} jobs to {JOBS_OUTPUT}")
        
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")


if __name__ == '__main__':
    main()
