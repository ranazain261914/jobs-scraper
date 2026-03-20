"""
Greenhouse Jobs Portal Scraper

Scrapes job listings from https://job-boards.greenhouse.io/remotecom
Extracts job links and parses individual job posting details.

Data fields extracted:
- job_title: Position name
- company_name: Company name
- location: Job location
- job_description: Full job description
- employment_type: Full-time, Part-time, etc.
- posted_date: When job was posted
- job_url: Direct link to job posting
"""

import logging
import csv
import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'job_links_greenhouse.csv')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs_greenhouse.csv')


def extract_greenhouse_jobs():
    """
    Extract all job links from Greenhouse board for Remote.com
    """
    
    logger.info("\n" + "="*80)
    logger.info("GREENHOUSE JOBS PORTAL - REMOTE.COM")
    logger.info("="*80)
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    all_job_links = []
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)
        
        url = "https://job-boards.greenhouse.io/remotecom"
        logger.info(f"Loading: {url}")
        
        try:
            driver.get(url)
        except Exception as e:
            logger.warning(f"Page load timeout (expected for heavy JS sites): {e}")
        
        wait = WebDriverWait(driver, 10)
        
        # Wait for job listings to load
        logger.info("[STEP 1] Waiting for job listings to load...")
        time.sleep(4)  # Let JS render
        
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            logger.info("  ✓ Page loaded")
        except:
            logger.warning("  Page load wait timeout, continuing...")
        
        # STEP 2: Extract all job links
        logger.info("\n[STEP 2] Extracting job links...")
        
        try:
            page_source = driver.page_source
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return []
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Greenhouse typically uses specific job link patterns
        # Look for links that go to job pages
        job_links = []
        
        # Pattern 1: Look for job div containers with links
        # Greenhouse uses data-job-id attributes often
        job_containers = soup.find_all('div', {'data-job-id': True})
        logger.info(f"Found {len(job_containers)} job containers with data-job-id")
        
        for container in job_containers:
            link = container.find('a')
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('/'):
                    href = 'https://job-boards.greenhouse.io' + href
                elif not href.startswith('http'):
                    href = 'https://job-boards.greenhouse.io/remotecom' + href
                
                job_title = link.get_text(strip=True)
                job_links.append({
                    'url': href,
                    'source': 'greenhouse',
                    'job_title': job_title,
                    'extracted_at': datetime.now().isoformat()
                })
        
        # Pattern 2: If no containers found, look for all job-related links
        if not job_links:
            logger.info("No containers found, searching for job links...")
            all_links = soup.find_all('a')
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True).lower()
                
                # Look for job-related links
                if 'job' in href.lower() or ('/remotecom/' in href and len(text) > 3):
                    if href.startswith('/'):
                        href = 'https://job-boards.greenhouse.io' + href
                    elif not href.startswith('http'):
                        continue
                    
                    job_title = link.get_text(strip=True)
                    if job_title and len(job_title) > 3:
                        job_links.append({
                            'url': href,
                            'source': 'greenhouse',
                            'job_title': job_title,
                            'extracted_at': datetime.now().isoformat()
                        })
        
        # Remove duplicates
        seen_urls = set()
        unique_links = []
        for link in job_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        all_job_links = unique_links
        
        logger.info(f"\n✓ TOTAL JOBS EXTRACTED: {len(all_job_links)}")
        
        if len(all_job_links) == 0:
            logger.warning("⚠ No jobs extracted. Checking page structure...")
            logger.info(f"Page source length: {len(page_source)} characters")
        
        # STEP 3: Save job links
        logger.info("\n[STEP 3] Saving job links...")
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
        
    except Exception as e:
        logger.error(f"Error in extract_greenhouse_jobs: {e}")
        return all_job_links
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def parse_greenhouse_job(driver, url):
    """Parse individual Greenhouse job posting"""
    try:
        driver.get(url)
        
        wait = WebDriverWait(driver, 8)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            pass
        
        time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_data = {
            'job_title': None,
            'company_name': 'Remote.com',
            'location': None,
            'job_description': None,
            'employment_type': None,
            'posted_date': None,
            'source': 'greenhouse',
            'job_url': url,
            'extracted_at': datetime.now().isoformat()
        }
        
        # Extract job title - usually in h1 or main heading
        title_elem = soup.find('h1')
        if title_elem:
            job_data['job_title'] = title_elem.get_text(strip=True)
        
        # Extract location - look for location section
        location_section = soup.find(text=re.compile(r'Location|location'))
        if location_section:
            parent = location_section.parent
            if parent and parent.next_sibling:
                job_data['location'] = parent.next_sibling.get_text(strip=True)
        
        # Extract job description - main content
        main_content = soup.find('main') or soup.find('article') or soup.find(class_=re.compile('content|description', re.I))
        
        if main_content:
            job_data['job_description'] = main_content.get_text(strip=True)[:2000]
        else:
            # Get all text content
            body = soup.find('body')
            if body:
                text = body.get_text(strip=True)
                text = re.sub(r'\s+', ' ', text)
                job_data['job_description'] = text[:2000] if len(text) > 100 else None
        
        return job_data if job_data['job_title'] else None
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None


def main():
    """Extract and parse all Greenhouse jobs"""
    
    # PHASE 1: Extract all job links
    logger.info("\n[PHASE 1/2] EXTRACTING ALL JOB LINKS")
    job_links = extract_greenhouse_jobs()
    
    if not job_links:
        logger.error("No job links extracted!")
        return
    
    # PHASE 2: Parse job details
    logger.info("\n[PHASE 2/2] PARSING JOB DETAILS FROM LINKS")
    logger.info(f"Will parse {len(job_links)} job postings...")
    
    jobs_data = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    try:
        for idx, link_data in enumerate(job_links, 1):
            if idx % 5 == 0 or idx == 1:
                logger.info(f"  Parsing: [{idx}/{len(job_links)}] jobs...")
            
            job_data = parse_greenhouse_job(driver, link_data['url'])
            if job_data:
                jobs_data.append(job_data)
            
            time.sleep(0.5)  # Be respectful with requests
    finally:
        driver.quit()
    
    logger.info(f"\n✓ Successfully parsed {len(jobs_data)} jobs")
    
    # PHASE 3: Save results
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
    
    # SUMMARY
    logger.info("\n" + "="*80)
    logger.info(f"FINAL RESULTS: {len(jobs_data)} JOBS EXTRACTED FROM GREENHOUSE")
    logger.info("="*80)
    logger.info(f"  Job links extracted: {len(job_links)}")
    logger.info(f"  Jobs successfully parsed: {len(jobs_data)}")
    if len(job_links) > 0:
        logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
