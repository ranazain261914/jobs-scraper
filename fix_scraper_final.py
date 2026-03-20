"""
FINAL CORRECTED Job Scraper - Smart parsing that extracts REAL job data

The issue: The raw page content includes JavaScript error messages and navigation.
The solution: Parse the structured data table FIRST, then extract only the Job Description section.
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
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_table = soup.find('table', class_='table')
        if not job_table:
            logger.error("Could not find job table")
            return []
        
        rows = job_table.find_all('tr')[1:]
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


def parse_single_job_FIXED(url: str) -> dict:
    """Parse a single job posting page - SMART PARSING VERSION"""
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        logger.info(f"Parsing: {url}")
        driver.get(url)
        
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
        
        # STEP 1: Parse the structured table (label: value pairs)
        all_tds = soup.find_all('td')
        job_details = {}
        
        # Parse table structure
        for i in range(0, len(all_tds)-1, 2):
            label_elem = all_tds[i]
            value_elem = all_tds[i+1]
            
            label = label_elem.get_text(strip=True).lower()
            value = value_elem.get_text(strip=True)
            
            job_details[label] = value
            
            # Map structured fields
            if 'role' in label or 'position' in label:
                if not job_data['job_title']:
                    job_data['job_title'] = value
            
            if 'district' in label:
                if value and value != 'Punjab, Pakistan':
                    job_data['location'] = f"{value}, Punjab, Pakistan"
            
            if 'employment' in label or 'status' in label:
                job_data['employment_type'] = value
            
            if 'date' in label and 'posted' in label:
                job_data['posted_date'] = value
        
        # STEP 2: Extract job description - SMART WAY
        # Look for the "Job Description" section in the page
        full_text = soup.get_text()
        
        # Find the "Job Description" marker
        if 'Job Description' in full_text:
            # Split at "Job Description" and get everything after
            desc_start = full_text.index('Job Description') + len('Job Description')
            description_text = full_text[desc_start:]
            
            # Remove common noise patterns
            # Stop at common footer markers
            for marker in ['Job Responsibilities', 'Apply for this Job', 'Sitemap', 'Important Note', 'Degree Level']:
                if marker in description_text:
                    idx = description_text.index(marker)
                    description_text = description_text[:idx]
            
            # Clean up the text
            description_text = re.sub(r'\s+', ' ', description_text).strip()
            
            if description_text and len(description_text) > 20:
                job_data['job_description'] = description_text[:2000]
        
        # Fallback: if still no description, try to get from structure
        if not job_data['job_description']:
            # Try to find descriptive text after "Role" field
            if 'role' in job_details:
                desc_parts = []
                for key, val in job_details.items():
                    if key not in ['role', 'position', 'salary', 'monthly salary', 'division', 'industry']:
                        desc_parts.append(f"{key}: {val}")
                if desc_parts:
                    job_data['job_description'] = ' | '.join(desc_parts)[:2000]
        
        # STEP 3: Extract just the job title from the page if structured one is bad
        if not job_data['job_title'] or job_data['job_title'] in ['1', '2', '3', '4', '5']:
            # Try to get title from the page h1/h2
            page_title = soup.find('h1') or soup.find('h2')
            if page_title:
                title_text = page_title.get_text(strip=True)
                # Take only the first reasonable part (stop at symbols or company name)
                title_text = re.sub(r'(Punjab.*Authority|PAKISTAN).*', '', title_text, flags=re.IGNORECASE).strip()
                # Remove leading numbers and symbols
                title_text = re.sub(r'^[\d\s\-]+', '', title_text).strip()
                if title_text and len(title_text) > 3:
                    job_data['job_title'] = title_text
        
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
        job_data = parse_single_job_FIXED(job_link_data['url'])
        if job_data:
            jobs_data.append(job_data)
            title_preview = job_data.get('job_title', 'Unknown')[:50]
            logger.info(f"  [{idx}/{len(job_links)}] {title_preview}")
    
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
