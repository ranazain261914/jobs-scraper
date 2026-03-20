"""
Master Job Scraper - Unified Scraper

Combines job scraping from multiple sources:
1. Punjab Jobs Portal (scraper_punjab.py)
2. Greenhouse / Remote.com (scraper_greenhouse.py)

Creates unified CSV outputs combining data from all sources.
"""

import logging
import csv
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
MASTER_LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'all_job_links.csv')
MASTER_JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'all_jobs.csv')


def run_scraper(script_name: str, description: str) -> bool:
    """Run an individual scraper script"""
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"RUNNING: {description}")
        logger.info(f"{'='*80}")
        
        script_path = os.path.join(PROJECT_ROOT, script_name)
        
        if not os.path.exists(script_path):
            logger.warning(f"✗ Script not found: {script_path}")
            return False
        
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            check=False,
            capture_output=False
        )
        
        if result.returncode == 0:
            logger.info(f"✓ {description} completed successfully")
            return True
        else:
            logger.warning(f"⚠ {description} exited with code {result.returncode}")
            return True  # Still continue, data might have been saved
        
    except Exception as e:
        logger.error(f"✗ Error running {description}: {e}")
        return False


def consolidate_job_links():
    """Combine all job links from different sources"""
    logger.info("\n" + "="*80)
    logger.info("CONSOLIDATING JOB LINKS")
    logger.info("="*80)
    
    all_links = []
    sources_found = 0
    
    # Define source files
    source_files = [
        ('data/raw/job_links.csv', 'punjab'),
        ('data/raw/job_links_greenhouse.csv', 'greenhouse'),
        ('data/raw/job_links_ashby.csv', 'ashby'),
    ]
    
    for file_path, source in source_files:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    file_links = list(reader)
                    all_links.extend(file_links)
                    logger.info(f"✓ Loaded {len(file_links)} links from {source}")
                    sources_found += 1
            except Exception as e:
                logger.warning(f"⚠ Error reading {file_path}: {e}")
        else:
            logger.warning(f"⚠ File not found: {file_path}")
    
    logger.info(f"\n✓ Total links consolidated: {len(all_links)} from {sources_found} source(s)")
    
    # Save consolidated links
    os.makedirs(os.path.dirname(MASTER_LINKS_OUTPUT), exist_ok=True)
    
    with open(MASTER_LINKS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        if all_links:
            writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at', 'job_title'])
            writer.writeheader()
            writer.writerows(all_links)
    
    logger.info(f"✓ Saved {len(all_links)} consolidated job links to {MASTER_LINKS_OUTPUT}")
    
    return len(all_links)


def consolidate_jobs():
    """Combine all job data from different sources"""
    logger.info("\n" + "="*80)
    logger.info("CONSOLIDATING JOB DATA")
    logger.info("="*80)
    
    all_jobs = []
    sources_found = 0
    
    # Define source files
    source_files = [
        ('data/final/jobs.csv', 'punjab'),
        ('data/final/jobs_greenhouse.csv', 'greenhouse'),
        ('data/final/jobs_ashby.csv', 'ashby'),
    ]
    
    for file_path, source in source_files:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    file_jobs = list(reader)
                    all_jobs.extend(file_jobs)
                    logger.info(f"✓ Loaded {len(file_jobs)} jobs from {source}")
                    sources_found += 1
            except Exception as e:
                logger.warning(f"⚠ Error reading {file_path}: {e}")
        else:
            logger.warning(f"⚠ File not found: {file_path}")
    
    logger.info(f"\n✓ Total jobs consolidated: {len(all_jobs)} from {sources_found} source(s)")
    
    # Save consolidated jobs
    os.makedirs(os.path.dirname(MASTER_JOBS_OUTPUT), exist_ok=True)
    
    # Define CSV fields
    fieldnames = [
        'job_title', 'company_name', 'location', 'job_description',
        'employment_type', 'posted_date', 'source', 'job_url', 'extracted_at'
    ]
    
    with open(MASTER_JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_jobs)
    
    logger.info(f"✓ Saved {len(all_jobs)} consolidated jobs to {MASTER_JOBS_OUTPUT}")
    
    # Calculate statistics
    logger.info("\n" + "="*80)
    logger.info("CONSOLIDATION SUMMARY")
    logger.info("="*80)
    
    # Jobs per source
    source_counts = {}
    for job in all_jobs:
        source = job.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    logger.info("\nJobs per source:")
    for source, count in sorted(source_counts.items()):
        logger.info(f"  {source.upper()}: {count} jobs")
    
    # Unique companies
    companies = set()
    for job in all_jobs:
        company = job.get('company_name', 'Unknown')
        if company and company.strip():
            companies.add(company.strip())
    
    logger.info(f"\nUnique companies: {len(companies)}")
    
    # Unique locations
    locations = set()
    for job in all_jobs:
        location = job.get('location', 'Unknown')
        if location and location.strip():
            locations.add(location.strip())
    
    logger.info(f"Unique locations: {len(locations)}")
    
    logger.info("\n" + "="*80)
    
    return len(all_jobs)


def main():
    """Main orchestration function"""
    logger.info("\n" + "="*80)
    logger.info("MASTER JOB SCRAPER - UNIFIED DATA EXTRACTION")
    logger.info("="*80)
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # PHASE 1: Run individual scrapers
    logger.info("\n[PHASE 1/3] RUNNING INDIVIDUAL SCRAPERS")
    
    scrapers = [
        ('scraper_punjab.py', 'Punjab Jobs Portal Scraper'),
        ('scraper_greenhouse.py', 'Greenhouse / Remote.com Scraper'),
    ]
    
    completed = 0
    for script_name, description in scrapers:
        if run_scraper(script_name, description):
            completed += 1
    
    logger.info(f"\n✓ Completed {completed}/{len(scrapers)} scrapers")
    
    # PHASE 2: Consolidate job links
    logger.info("\n[PHASE 2/3] CONSOLIDATING JOB LINKS")
    total_links = consolidate_job_links()
    
    # PHASE 3: Consolidate job data
    logger.info("\n[PHASE 3/3] CONSOLIDATING JOB DATA")
    total_jobs = consolidate_jobs()
    
    # FINAL SUMMARY
    logger.info("\n" + "="*80)
    logger.info("FINAL SUMMARY")
    logger.info("="*80)
    logger.info(f"Total job links consolidated: {total_links}")
    logger.info(f"Total jobs consolidated: {total_jobs}")
    logger.info(f"\nOutput files:")
    logger.info(f"  ✓ All job links: {MASTER_LINKS_OUTPUT}")
    logger.info(f"  ✓ All jobs: {MASTER_JOBS_OUTPUT}")
    logger.info("="*80 + "\n")


if __name__ == '__main__':
    main()
