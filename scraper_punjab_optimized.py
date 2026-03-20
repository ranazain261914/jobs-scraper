"""
Punjab Jobs Portal Scraper - OPTIMIZED VERSION

Extracts ALL 53 job listings using the "Show 100 rows" dropdown option
This avoids pagination by displaying all jobs on a single page.

Optimization: Instead of navigating 6 pages, we change the display settings
to show 100 rows per page, which loads all 53 jobs at once.
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
LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'job_links.csv')
JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'jobs.csv')


def scrape_all_punjab_jobs_optimized():
    """
    Scrape all Punjab jobs by using the 'Show 100 rows' dropdown.
    This displays all 53 jobs on a single page instead of pagination.
    """
    
    logger.info("\n" + "="*80)
    logger.info("PUNJAB JOBS PORTAL - OPTIMIZED SCRAPER (All 53+ jobs in one page)")
    logger.info("="*80)
    
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    all_job_links = []
    
    try:
        url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
        logger.info(f"Loading: {url}")
        driver.get(url)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
        
        time.sleep(2)
        
        # STEP 1: Find and click the dropdown to show 100 rows
        logger.info("\n[STEP 1] Changing table display to show 100 rows per page...")
        
        try:
            # Look for the dropdown that controls rows per page
            # Usually in format like: "Show X entries" or similar
            # The dropdown options are typically: 10, 25, 50, 100
            
            # Try to find the select element for rows display
            select_elements = driver.find_elements(By.TAG_NAME, "select")
            
            rows_dropdown_found = False
            for select_elem in select_elements:
                options_in_select = select_elem.find_elements(By.TAG_NAME, "option")
                # Look for an option with value "100" or text "100"
                for option in options_in_select:
                    if "100" in option.text or option.get_attribute("value") == "100":
                        logger.info(f"  Found rows dropdown, selecting 100 rows...")
                        option.click()
                        rows_dropdown_found = True
                        time.sleep(3)  # Wait for table to reload with 100 rows
                        break
                if rows_dropdown_found:
                    break
            
            if not rows_dropdown_found:
                logger.warning("  Could not find rows per page dropdown, continuing with current view...")
        
        except Exception as e:
            logger.warning(f"  Error interacting with dropdown: {e}")
            logger.info("  Continuing with current page view...")
        
        # STEP 2: Extract all job links from the table
        logger.info("\n[STEP 2] Extracting job links from table...")
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_table = soup.find('table', class_='table')
        
        if not job_table:
            logger.error("Could not find job table")
            return []
        
        rows = job_table.find_all('tr')[1:]  # Skip header row
        logger.info(f"Found {len(rows)} job rows in table")
        
        for idx, row in enumerate(rows, 1):
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
                        
                        if idx % 10 == 0:
                            logger.info(f"  Extracted {idx} jobs...")
        
        logger.info(f"\n✓ TOTAL JOBS EXTRACTED: {len(all_job_links)}")
        
        if len(all_job_links) < 50:
            logger.warning(f"⚠ WARNING: Only extracted {len(all_job_links)} jobs. Expected ~53.")
            logger.warning("  This may mean the dropdown didn't work. Check website structure.")
        
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
        
        time.sleep(0.5)  # Reduced wait time since we're parsing many jobs
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
        
        # Parse table structure for job details
        all_tds = soup.find_all('td')
        
        for i in range(0, len(all_tds)-1, 2):
            try:
                label = all_tds[i].get_text(strip=True).lower()
                value = all_tds[i+1].get_text(strip=True)
                
                if 'role' in label or 'position' in label:
                    if not job_data['job_title'] and value not in ['1', '2', '3', '4', '5']:
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
            
            # Stop at common markers
            for marker in ['Job Responsibilities', 'Apply for', 'Sitemap', 'Important Note', 'Degree Level', 'Requirement']:
                if marker in description_text:
                    description_text = description_text[:description_text.index(marker)]
            
            description_text = re.sub(r'\s+', ' ', description_text).strip()
            if description_text and len(description_text) > 20:
                job_data['job_description'] = description_text[:2000]
        
        # Get proper title if not extracted from table
        if not job_data['job_title']:
            page_title = soup.find('h1') or soup.find('h2')
            if page_title:
                title_text = page_title.get_text(strip=True)
                title_text = re.sub(r'Punjab.*Authority|PAKISTAN|PLRA', '', title_text, flags=re.IGNORECASE).strip()
                title_text = re.sub(r'^[\d\s\-]+', '', title_text).strip()
                title_text = re.sub(r'\s*-\s*,\s*$', '', title_text).strip()  # Remove trailing " - ,"
                if title_text and len(title_text) > 3:
                    job_data['job_title'] = title_text
        
        # Clean up title
        if job_data['job_title']:
            job_data['job_title'] = re.sub(r'\s*-\s*,\s*$', '', job_data['job_title']).strip()
        
        return job_data if job_data['job_title'] else None
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None


def main():
    """Extract and parse all Punjab jobs"""
    
    # STEP 1: Extract all job links (using dropdown to show 100 rows)
    logger.info("\n[PHASE 1/2] EXTRACTING ALL JOB LINKS")
    job_links = scrape_all_punjab_jobs_optimized()
    
    if not job_links:
        logger.error("No job links extracted!")
        return
    
    # STEP 2: Parse job details
    logger.info("\n[PHASE 2/2] PARSING JOB DETAILS FROM LINKS")
    logger.info(f"Will parse {len(job_links)} job postings...")
    
    jobs_data = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        for idx, link_data in enumerate(job_links, 1):
            if idx % 10 == 0 or idx == 1:
                logger.info(f"  Parsing: [{idx}/{len(job_links)}] jobs...")
            
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
    
    # SUMMARY
    logger.info("\n" + "="*80)
    logger.info(f"FINAL RESULTS: {len(jobs_data)} JOBS EXTRACTED FROM PUNJAB")
    logger.info("="*80)
    logger.info(f"  Job links extracted: {len(job_links)}")
    logger.info(f"  Jobs successfully parsed: {len(jobs_data)}")
    logger.info(f"  Success rate: {100*len(jobs_data)/len(job_links):.1f}%")
    logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
