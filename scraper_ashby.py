"""
Ashby Jobs Portal Scraper

Scrapes job listings from https://www.ashbyhq.com/careers
Extracts job links and parses individual job posting details.

Ashby is a recruiting platform that Ashby Inc. uses for their own careers page.

Data fields extracted:
- job_title: Position name
- company_name: Company (Ashby)
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
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'job_links_ashby.csv')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs_ashby.csv')


def extract_ashby_jobs():
    """
    Extract all job links from Ashby careers page.
    Ashby uses React with dynamic loading.
    """
    
    logger.info("\n" + "="*80)
    logger.info("ASHBY CAREERS - JOB SCRAPER")
    logger.info("="*80)
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    driver = None
    all_job_links = []
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)
        
        url = "https://www.ashbyhq.com/careers"
        logger.info(f"Loading: {url}")
        
        try:
            driver.get(url)
        except Exception as e:
            logger.warning(f"Page load timeout (expected for heavy JS sites): {e}")
        
        wait = WebDriverWait(driver, 10)
        
        # Wait for job listings to load
        logger.info("[STEP 1] Waiting for job listings to load...")
        
        # Try multiple wait conditions
        try:
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        except:
            pass
        
        time.sleep(6)  # Give time for React to fully render
        
        # Try scrolling to trigger infinite scroll if present
        logger.info("  Scrolling to load more content...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        for scroll_attempt in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        logger.info("  ✓ Page loaded and scrolled")
        
        # STEP 2: Extract all job links
        logger.info("\n[STEP 2] Extracting job links...")
        
        try:
            page_source = driver.page_source
        except Exception as e:
            logger.error(f"Failed to get page source: {e}")
            return []
        
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Look for job posting links and divs
        # Ashby often uses /careers/job/... URLs
        potential_links = []
        
        # Strategy 1: Find all links with href containing /careers
        all_links = soup.find_all('a', href=True)
        logger.info(f"Found {len(all_links)} total links on page")
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Look for career-related links
            if '/careers/' in href and 'job' in href.lower():
                if href.startswith('/'):
                    href = 'https://www.ashbyhq.com' + href
                elif not href.startswith('http'):
                    href = 'https://www.ashbyhq.com/careers/' + href
                
                if text and len(text) > 2:
                    potential_links.append((href, text))
        
        logger.info(f"Found {len(potential_links)} career-related links")
        
        # Remove duplicates and create job objects
        seen_urls = set()
        for href, text in potential_links:
            if href not in seen_urls:
                seen_urls.add(href)
                all_job_links.append({
                    'url': href,
                    'source': 'ashby',
                    'job_title': text,
                    'extracted_at': datetime.now().isoformat()
                })
        
        logger.info(f"\n✓ TOTAL JOBS EXTRACTED: {len(all_job_links)}")
        
        if len(all_job_links) == 0:
            logger.warning("⚠ No jobs extracted. Checking page structure...")
            logger.info(f"Page source length: {len(page_source)} characters")
            # Show first few links for debugging
            for i, link in enumerate(all_links[:10]):
                logger.info(f"  Link {i}: {link.get('href', 'NO HREF')[:60]}")
        
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
        logger.error(f"Error in extract_ashby_jobs: {e}")
        return all_job_links
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def parse_ashby_job(driver, url):
    """Parse individual Ashby job posting"""
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
            'company_name': 'Ashby',
            'location': None,
            'job_description': None,
            'employment_type': None,
            'posted_date': None,
            'source': 'ashby',
            'job_url': url,
            'extracted_at': datetime.now().isoformat()
        }
        
        # Extract job title - usually in h1 or main heading
        title_elem = soup.find('h1')
        if title_elem:
            job_data['job_title'] = title_elem.get_text(strip=True)
        
        # Extract location - look for location info
        location_patterns = ['location', 'office', 'remote', 'san francisco', 'new york', 'los angeles']
        for text in soup.find_all(text=True):
            text_lower = text.lower().strip()
            for pattern in location_patterns:
                if pattern in text_lower:
                    job_data['location'] = text.strip()
                    break
            if job_data['location']:
                break
        
        # Extract job description - usually main body content
        main_content = soup.find('main') or soup.find('article') or soup.find(class_=re.compile('content|description', re.I))
        if main_content:
            job_data['job_description'] = main_content.get_text(strip=True)[:2000]
        
        # If no main content found, try to extract from body
        if not job_data['job_description']:
            body_text = soup.find('body')
            if body_text:
                all_text = body_text.get_text(strip=True)
                # Remove common noise
                all_text = re.sub(r'\s+', ' ', all_text)
                job_data['job_description'] = all_text[:2000] if len(all_text) > 100 else None
        
        return job_data if job_data['job_title'] else None
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None


def main():
    """Extract and parse all Ashby jobs"""
    
    # PHASE 1: Extract all job links
    logger.info("\n[PHASE 1/2] EXTRACTING ALL JOB LINKS")
    job_links = extract_ashby_jobs()
    
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
            
            job_data = parse_ashby_job(driver, link_data['url'])
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
    logger.info(f"FINAL RESULTS: {len(jobs_data)} JOBS EXTRACTED FROM ASHBY")
    logger.info("="*80)
    logger.info(f"  Job links extracted: {len(job_links)}")
    logger.info(f"  Jobs successfully parsed: {len(jobs_data)}")
    if len(job_links) > 0:
        logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
