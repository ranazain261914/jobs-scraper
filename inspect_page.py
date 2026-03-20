#!/usr/bin/env python3
"""Test script to inspect actual page structure of a job posting."""

import sys
import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = Chrome(options=options)

try:
    url = 'https://jobs.punjab.gov.pk/new_recruit/job_detail/assistant-director-accounts-1'
    print(f'Loading: {url}')
    driver.get(url)
    time.sleep(5)
    
    source = driver.page_source
    print(f'Page length: {len(source)} chars')
    print('\n=== FIRST 2000 CHARS ===')
    print(source[:2000])
    
    print('\n\n=== PARSED STRUCTURE ===')
    soup = BeautifulSoup(source, 'html.parser')
    
    # Look for job title
    print('\nLooking for h1/h2 tags:')
    for elem in soup.find_all(['h1', 'h2', 'h3'])[:5]:
        print(f"  {elem.name}: '{elem.get_text(strip=True)[:100]}'")
    
    # Look for divs with job info
    print('\nLooking for divs with "job" in class:')
    for div in soup.find_all('div'):
        if div.get('class'):
            classes = ' '.join(div.get('class', []))
            if 'job' in classes.lower() or 'detail' in classes.lower():
                text = div.get_text(strip=True)[:100]
                print(f"  {classes}: '{text}'")
    
    # Show all text content (first 3000 chars)
    print('\n\n=== ALL TEXT CONTENT ===')
    all_text = soup.get_text(separator='\n', strip=True)
    print(all_text[:3000])
    
finally:
    driver.quit()
