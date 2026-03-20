"""
MULTI-SOURCE Job Scraper with Pagination

Scrapes from THREE job portals:
1. Greenhouse (https://www.greenhouse.com/careers/opportunities)
2. Ashby (https://www.ashbyhq.com/careers)
3. Punjab Jobs (https://jobs.punjab.gov.pk/new_recruit/jobs) with pagination

Key features:
- Extracts ALL job listings (with pagination support)
- Proper error handling and fallbacks
- Source tracking
- Real job data (not page junk)
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


def scrape_greenhouse_jobs():
    """Scrape Greenhouse careers portal - Extract individual job posting URLs"""
    logger.info("\n" + "="*70)
    logger.info("[SOURCE 1/3] GREENHOUSE JOBS PORTAL")
    logger.info("="*70)
    
    job_links = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        url = "https://www.greenhouse.com/careers/opportunities"
        logger.info(f"Loading: {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        try:
            # Wait for job listings to load
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job")))
        except:
            logger.warning("Could not find job listings - page may have dynamic content")
        
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Look for job links - Greenhouse usually has them in .job class or similar
        job_elements = soup.find_all('a', class_='job')
        if not job_elements:
            # Try alternative selectors
            job_elements = soup.find_all('a', href=re.compile(r'/job/'))
        
        for elem in job_elements:
            href = elem.get('href', '')
            if href:
                full_url = 'https://www.greenhouse.com' + href if not href.startswith('http') else href
                if '/job/' in full_url or '/opening/' in full_url:
                    job_links.append({
                        'url': full_url,
                        'source': 'greenhouse',
                        'extracted_at': datetime.now().isoformat()
                    })
        
        logger.info(f"Found {len(job_links)} Greenhouse jobs")
        
    except Exception as e:
        logger.error(f"Error scraping Greenhouse: {e}")
    finally:
        driver.quit()
    
    return job_links


def scrape_ashby_jobs():
    """Scrape Ashby careers portal - Extract individual job posting URLs"""
    logger.info("\n" + "="*70)
    logger.info("[SOURCE 2/3] ASHBY CAREERS PORTAL")
    logger.info("="*70)
    
    job_links = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        url = "https://www.ashbyhq.com/careers"
        logger.info(f"Loading: {url}")
        driver.get(url)
        
        wait = WebDriverWait(driver, 10)
        try:
            # Ashby uses JavaScript heavy rendering - wait for content
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
        except:
            logger.warning("Timeout waiting for Ashby page content")
        
        # Scroll to load more jobs
        logger.info("Scrolling to load more jobs...")
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Look for job links in Ashby format
        job_elements = soup.find_all('a', href=re.compile(r'/jobs/'))
        
        for elem in job_elements:
            href = elem.get('href', '')
            if href and '/jobs/' in href:
                full_url = 'https://www.ashbyhq.com' + href if not href.startswith('http') else href
                job_links.append({
                    'url': full_url,
                    'source': 'ashby',
                    'extracted_at': datetime.now().isoformat()
                })
        
        # Remove duplicates
        seen_urls = set()
        unique_links = []
        for link in job_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        logger.info(f"Found {len(unique_links)} unique Ashby jobs")
        
        return unique_links
        
    except Exception as e:
        logger.error(f"Error scraping Ashby: {e}")
    finally:
        driver.quit()
    
    return job_links


def scrape_punjab_jobs_with_pagination():
    """Scrape Punjab Jobs portal - Extract job URLs with pagination support"""
    logger.info("\n" + "="*70)
    logger.info("[SOURCE 3/3] PUNJAB GOVERNMENT JOBS PORTAL (WITH PAGINATION)")
    logger.info("="*70)
    
    job_links = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        base_url = "https://jobs.punjab.gov.pk/new_recruit/jobs"
        page = 1
        
        while True:
            # Build URL with page parameter if needed
            url = f"{base_url}?page={page}" if page > 1 else base_url
            
            logger.info(f"Loading page {page}: {url}")
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            try:
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))
            except:
                logger.warning(f"Timeout on page {page}")
                break
            
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract job links from table
            job_table = soup.find('table', class_='table')
            if not job_table:
                logger.info(f"No job table found on page {page} - pagination complete")
                break
            
            rows = job_table.find_all('tr')[1:]  # Skip header
            if not rows:
                logger.info(f"No job rows found on page {page} - pagination complete")
                break
            
            page_jobs = 0
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
                            page_jobs += 1
            
            logger.info(f"  Page {page}: Extracted {page_jobs} jobs (Total so far: {len(job_links)})")
            
            # Check if there's a next page button
            next_button = soup.find('a', string=re.compile(r'Next|next|>'))
            if not next_button or not next_button.get('href'):
                logger.info("No next page found - pagination complete")
                break
            
            page += 1
            
            # Safety limit to avoid infinite loops
            if page > 50:
                logger.warning("Reached page limit of 50 - stopping pagination")
                break
        
        logger.info(f"Total Punjab jobs extracted: {len(job_links)}")
        
    except Exception as e:
        logger.error(f"Error scraping Punjab jobs: {e}")
    finally:
        driver.quit()
    
    return job_links


def parse_job_details(driver, url, source):
    """Parse job details from a job posting page"""
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 8)
        try:
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        except:
            pass
        
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_data = {
            'job_title': None,
            'company_name': None,
            'location': None,
            'job_description': None,
            'employment_type': None,
            'posted_date': None,
            'source': source,
            'job_url': url,
            'extracted_at': datetime.now().isoformat()
        }
        
        # Source-specific parsing
        if source == 'punjab':
            job_data['company_name'] = 'Punjab Government'
            job_data['location'] = 'Punjab, Pakistan'
            job_data['employment_type'] = 'Full-time'
            
            # Parse table data
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
            
            # Extract description
            full_text = soup.get_text()
            if 'Job Description' in full_text:
                desc_start = full_text.index('Job Description') + len('Job Description')
                description_text = full_text[desc_start:]
                
                for marker in ['Job Responsibilities', 'Apply for', 'Sitemap', 'Important Note']:
                    if marker in description_text:
                        description_text = description_text[:description_text.index(marker)]
                
                description_text = re.sub(r'\s+', ' ', description_text).strip()
                if description_text and len(description_text) > 20:
                    job_data['job_description'] = description_text[:2000]
            
            # Get proper title
            if not job_data['job_title'] or job_data['job_title'] in ['1', '2', '3']:
                page_title = soup.find('h1') or soup.find('h2')
                if page_title:
                    title_text = page_title.get_text(strip=True)
                    title_text = re.sub(r'Punjab.*Authority|PAKISTAN|PLRA', '', title_text, flags=re.IGNORECASE).strip()
                    title_text = re.sub(r'^[\d\s\-]+', '', title_text).strip()
                    if title_text and len(title_text) > 3:
                        job_data['job_title'] = title_text
        
        elif source == 'greenhouse':
            # Parse Greenhouse job page
            # These typically have different HTML structure
            title = soup.find('h1') or soup.find('h2')
            job_data['job_title'] = title.get_text(strip=True) if title else None
            
            # Find company/location info
            meta_info = soup.find_all('p', class_='meta')
            if meta_info:
                text = meta_info[0].get_text(strip=True)
                # Usually format is "Company - Location"
                parts = text.split('-')
                if len(parts) >= 2:
                    job_data['company_name'] = parts[0].strip()
                    job_data['location'] = parts[1].strip()
            
            # Find job description
            content = soup.find('div', class_='content') or soup.find('div', class_='job-description')
            if content:
                job_data['job_description'] = content.get_text(separator=' ', strip=True)[:2000]
        
        elif source == 'ashby':
            # Parse Ashby job page
            title = soup.find('h1')
            job_data['job_title'] = title.get_text(strip=True) if title else None
            
            # Find company name
            company = soup.find('h2', class_='company') or soup.find('span', class_='company')
            if company:
                job_data['company_name'] = company.get_text(strip=True)
            
            # Find location
            location = soup.find('span', class_='location')
            if location:
                job_data['location'] = location.get_text(strip=True)
            
            # Find description
            desc = soup.find('div', class_='description') or soup.find('div', class_='job-description')
            if desc:
                job_data['job_description'] = desc.get_text(separator=' ', strip=True)[:2000]
        
        return job_data if job_data['job_title'] else None
        
    except Exception as e:
        logger.error(f"Error parsing {url}: {e}")
        return None


def scrape_all_sources():
    """Extract from all THREE sources and save results"""
    logger.info("\n" + "#"*70)
    logger.info("# MULTI-SOURCE JOB SCRAPER")
    logger.info("#"*70)
    
    all_job_links = []
    
    # STEP 1: Extract job URLs from all sources
    logger.info("\n[STEP 1] EXTRACTING JOB URLs FROM ALL SOURCES")
    
    # Punjab (with pagination)
    punjab_links = scrape_punjab_jobs_with_pagination()
    all_job_links.extend(punjab_links)
    
    # Greenhouse
    greenhouse_links = scrape_greenhouse_jobs()
    all_job_links.extend(greenhouse_links)
    
    # Ashby
    ashby_links = scrape_ashby_jobs()
    all_job_links.extend(ashby_links)
    
    logger.info(f"\n✓ Total URLs extracted: {len(all_job_links)}")
    logger.info(f"  - Punjab: {len(punjab_links)}")
    logger.info(f"  - Greenhouse: {len(greenhouse_links)}")
    logger.info(f"  - Ashby: {len(ashby_links)}")
    
    # Save job links
    os.makedirs(os.path.dirname(LINKS_OUTPUT), exist_ok=True)
    with open(LINKS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at'])
        writer.writeheader()
        writer.writerows(all_job_links)
    logger.info(f"✓ Saved {len(all_job_links)} URLs to {LINKS_OUTPUT}\n")
    
    # STEP 2: Parse job details from URLs
    logger.info("[STEP 2] PARSING JOB DETAILS FROM URLs")
    
    jobs_data = []
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = Chrome(options=options)
    
    try:
        for idx, link_data in enumerate(all_job_links, 1):
            url = link_data['url']
            source = link_data['source']
            
            # Show progress
            if idx % 10 == 0 or idx == 1:
                logger.info(f"  [{idx}/{len(all_job_links)}] Parsing jobs...")
            
            job_data = parse_job_details(driver, url, source)
            if job_data and job_data['job_title']:
                jobs_data.append(job_data)
    
    finally:
        driver.quit()
    
    logger.info(f"\n✓ Parsed {len(jobs_data)} complete job records")
    
    # STEP 3: Save job data
    logger.info("\n[STEP 3] SAVING JOB DATA")
    
    os.makedirs(os.path.dirname(JOBS_OUTPUT), exist_ok=True)
    with open(JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'job_title', 'company_name', 'location', 'job_description',
            'employment_type', 'posted_date', 'source', 'job_url', 'extracted_at'
        ])
        writer.writeheader()
        writer.writerows(jobs_data)
    
    logger.info(f"✓ Saved {len(jobs_data)} jobs to {JOBS_OUTPUT}")
    
    # Summary
    logger.info("\n" + "="*70)
    logger.info("SCRAPING COMPLETE - SUMMARY")
    logger.info("="*70)
    source_counts = {}
    for job in jobs_data:
        source = job['source']
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in source_counts.items():
        logger.info(f"  {source.upper():15} {count:5} jobs")
    logger.info(f"  {'TOTAL':15} {len(jobs_data):5} jobs")
    logger.info("="*70 + "\n")


if __name__ == '__main__':
    scrape_all_sources()
