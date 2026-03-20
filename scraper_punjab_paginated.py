"""
Punjab Jobs Portal Scraper with Proper Pagination

Extracts ALL available job listings from Punjab government jobs portal
with pagination support.

The Punjab portal uses table-based listings with page navigation.
"""

import logging
import csv
import os
import time
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
LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'job_links.csv')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs.csv')


def scrape_punjab_all_jobs():
    """Scrape ALL Punjab jobs with pagination"""
    
    logger.info("\n" + "="*80)
    logger.info("PUNJAB JOBS PORTAL - COMPREHENSIVE SCRAPER WITH PAGINATION")
    logger.info("="*80)
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    all_job_links = []
    
    try:
        base_url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
        page_num = 1
        
        while True:
            logger.info(f"\n[PAGE {page_num}] Loading job listings...")
            
            # Build URL with page parameter
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}?page={page_num}"
            
            logger.info(f"URL: {url}")
            driver.get(url)
            
            # Wait for table to load
            wait = WebDriverWait(driver, 10)
            try:
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
            except:
                logger.warning("Timeout waiting for table - pagination may be complete")
                break
            
            time.sleep(2)
            
            # Parse page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_table = soup.find('table', class_='table')
            
            if not job_table:
                logger.info("No job table found - pagination complete")
                break
            
            # Extract jobs from this page
            rows = job_table.find_all('tr')[1:]  # Skip header
            
            if not rows:
                logger.info("No job rows found - pagination complete")
                break
            
            page_count = 0
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 1:
                    link_elem = cols[0].find('a')
                    if link_elem and link_elem.get('href'):
                        href = link_elem.get('href', '')
                        if '/job_detail/' in href:
                            full_url = 'https://jobs.punjab.gov.pk' + href if not href.startswith('http') else href
                            job_title = link_elem.get_text(strip=True)
                            
                            all_job_links.append({
                                'url': full_url,
                                'source': 'punjab',
                                'job_title': job_title,
                                'extracted_at': datetime.now().isoformat()
                            })
                            page_count += 1
            
            logger.info(f"✓ Extracted {page_count} jobs from page {page_num} (Total: {len(all_job_links)})")
            
            # Check for next page button
            pagination = soup.find('nav', class_='pagination') or soup.find('ul', class_='pagination')
            if pagination:
                next_btn = pagination.find('a', string=lambda x: x and ('Next' in x or 'next' in x or '>' in x))
                if next_btn:
                    logger.info("  → Found next page button, continuing...")
                    page_num += 1
                else:
                    logger.info("  → No next page button found - pagination complete")
                    break
            else:
                # Try alternative pagination methods
                next_links = soup.find_all('a', href=lambda x: x and 'page=' in str(x) if x else False)
                page_numbers = []
                for link in next_links:
                    try:
                        # Extract page number from href
                        page_str = link.get('href', '')
                        if '?page=' in page_str:
                            page_str = page_str.split('?page=')[-1].split('&')[0]
                            page_numbers.append(int(page_str))
                    except:
                        pass
                
                if page_numbers:
                    max_page = max(page_numbers)
                    if page_num < max_page:
                        logger.info(f"  → Found pagination links, moving to page {page_num + 1}...")
                        page_num += 1
                    else:
                        logger.info("  → At last page - pagination complete")
                        break
                else:
                    logger.info("  → No pagination links found - assuming single page")
                    break
            
            # Safety check
            if page_num > 100:
                logger.warning("Reached page limit of 100 - stopping")
                break
        
        logger.info(f"\n✓ TOTAL JOBS EXTRACTED: {len(all_job_links)}")
        
        # Save job links
        os.makedirs(os.path.dirname(LINKS_OUTPUT), exist_ok=True)
        with open(LINKS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at', 'job_title'])
            writer.writeheader()
            for link in all_job_links:
                writer.writerow({
                    'url': link['url'],
                    'source': link['source'],
                    'extracted_at': link['extracted_at'],
                    'job_title': link.get('job_title', '')
                })
        
        logger.info(f"✓ Saved {len(all_job_links)} job links to {LINKS_OUTPUT}")
        
        return all_job_links
        
    finally:
        driver.quit()


def parse_punjab_job(driver, url):
    """Parse individual Punjab job posting"""
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 8)
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
            'job_url': url,
            'extracted_at': datetime.now().isoformat()
        }
        
        # Parse table structure
        all_tds = soup.find_all('td')
        for i in range(0, len(all_tds)-1, 2):
            try:
                label = all_tds[i].get_text(strip=True).lower()
                value = all_tds[i+1].get_text(strip=True)
                
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
            import re
            desc_start = full_text.index('Job Description') + len('Job Description')
            description_text = full_text[desc_start:]
            
            for marker in ['Job Responsibilities', 'Apply for', 'Sitemap', 'Important Note', 'Degree Level']:
                if marker in description_text:
                    description_text = description_text[:description_text.index(marker)]
            
            description_text = re.sub(r'\s+', ' ', description_text).strip()
            if description_text and len(description_text) > 20:
                job_data['job_description'] = description_text[:2000]
        
        # Get proper title
        if not job_data['job_title'] or job_data['job_title'] in ['1', '2', '3']:
            import re
            page_title = soup.find('h1') or soup.find('h2')
            if page_title:
                title_text = page_title.get_text(strip=True)
                title_text = re.sub(r'Punjab.*Authority|PAKISTAN|PLRA', '', title_text, flags=re.IGNORECASE).strip()
                title_text = re.sub(r'^[\d\s\-]+', '', title_text).strip()
                if title_text and len(title_text) > 3:
                    job_data['job_title'] = title_text
        
        return job_data if job_data['job_title'] else None
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None


def main():
    """Extract and parse all Punjab jobs"""
    
    # STEP 1: Extract all job links with pagination
    logger.info("\n[STEP 1/2] EXTRACTING JOB LINKS WITH PAGINATION")
    job_links = scrape_punjab_all_jobs()
    
    # STEP 2: Parse job details
    logger.info("\n[STEP 2/2] PARSING JOB DETAILS")
    logger.info(f"Parsing {len(job_links)} job postings...")
    
    jobs_data = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        for idx, link_data in enumerate(job_links, 1):
            if idx % 20 == 0 or idx == 1:
                logger.info(f"  [{idx}/{len(job_links)}] Parsing jobs...")
            
            job_data = parse_punjab_job(driver, link_data['url'])
            if job_data:
                jobs_data.append(job_data)
    finally:
        driver.quit()
    
    logger.info(f"\n✓ Successfully parsed {len(jobs_data)} jobs")
    
    # STEP 3: Save results
    logger.info("\n[SAVING RESULTS]")
    os.makedirs(os.path.dirname(JOBS_OUTPUT), exist_ok=True)
    
    with open(JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'job_title', 'company_name', 'location', 'job_description',
            'employment_type', 'posted_date', 'source', 'job_url', 'extracted_at'
        ])
        writer.writeheader()
        writer.writerows(jobs_data)
    
    logger.info(f"✓ Saved {len(jobs_data)} jobs to {JOBS_OUTPUT}")
    
    logger.info("\n" + "="*80)
    logger.info(f"FINAL RESULTS: {len(jobs_data)} JOBS EXTRACTED FROM PUNJAB PORTAL")
    logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
