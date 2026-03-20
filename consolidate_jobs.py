"""
Master Job Consolidation - Combines data from all scrapers

Takes existing output files from individual scrapers and consolidates them
into unified master CSV files.

No scraping is performed - this script only consolidates existing data.
"""

import logging
import csv
import os
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
MASTER_LINKS_OUTPUT = os.path.join(DATA_DIR, 'raw', 'all_job_links.csv')
MASTER_JOBS_OUTPUT = os.path.join(DATA_DIR, 'final', 'all_jobs.csv')


def consolidate_job_links():
    """Combine all job links from different sources"""
    logger.info("\n" + "="*80)
    logger.info("CONSOLIDATING JOB LINKS FROM ALL SOURCES")
    logger.info("="*80)
    
    all_links = []
    sources_info = {}
    
    # Define source files (in priority order)
    source_files = [
        ('data/raw/job_links.csv', 'punjab'),
        ('data/raw/job_links_greenhouse.csv', 'greenhouse'),
        ('data/raw/job_links_ashby.csv', 'ashby'),
    ]
    
    for file_path, source_name in source_files:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    file_links = list(reader)
                    
                    if file_links:
                        all_links.extend(file_links)
                        count = len(file_links)
                        sources_info[source_name] = count
                        logger.info(f"✓ {source_name.upper()}: Loaded {count} job links")
                    else:
                        logger.warning(f"⚠ {source_name.upper()}: No data in file")
            except Exception as e:
                logger.warning(f"✗ Error reading {file_path}: {e}")
        else:
            logger.info(f"⚠ {source_name.upper()}: File not found: {file_path}")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"TOTAL JOB LINKS: {len(all_links)}")
    logger.info(f"{'='*80}")
    
    # Save consolidated links
    os.makedirs(os.path.dirname(MASTER_LINKS_OUTPUT), exist_ok=True)
    
    if all_links:
        with open(MASTER_LINKS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['url', 'source', 'extracted_at', 'job_title'])
            writer.writeheader()
            writer.writerows(all_links)
        
        logger.info(f"✓ Saved consolidated job links to:")
        logger.info(f"  {MASTER_LINKS_OUTPUT}")
    else:
        logger.warning("⚠ No job links to consolidate")
    
    return len(all_links), sources_info


def consolidate_jobs():
    """Combine all job data from different sources"""
    logger.info("\n" + "="*80)
    logger.info("CONSOLIDATING JOB DATA FROM ALL SOURCES")
    logger.info("="*80)
    
    all_jobs = []
    sources_info = {}
    
    # Define source files (in priority order)
    source_files = [
        ('data/final/jobs.csv', 'punjab'),
        ('data/final/jobs_greenhouse.csv', 'greenhouse'),
        ('data/final/jobs_ashby.csv', 'ashby'),
    ]
    
    for file_path, source_name in source_files:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        
        if os.path.exists(full_path):
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    file_jobs = list(reader)
                    
                    if file_jobs:
                        all_jobs.extend(file_jobs)
                        count = len(file_jobs)
                        sources_info[source_name] = count
                        logger.info(f"✓ {source_name.upper()}: Loaded {count} jobs")
                    else:
                        logger.warning(f"⚠ {source_name.upper()}: No data in file")
            except Exception as e:
                logger.warning(f"✗ Error reading {file_path}: {e}")
        else:
            logger.info(f"⚠ {source_name.upper()}: File not found: {file_path}")
    
    logger.info(f"\n{'='*80}")
    logger.info(f"TOTAL JOBS: {len(all_jobs)}")
    logger.info(f"{'='*80}")
    
    # Save consolidated jobs
    os.makedirs(os.path.dirname(MASTER_JOBS_OUTPUT), exist_ok=True)
    
    # Define CSV fields
    fieldnames = [
        'job_title', 'company_name', 'location', 'job_description',
        'employment_type', 'posted_date', 'source', 'job_url', 'extracted_at'
    ]
    
    if all_jobs:
        with open(MASTER_JOBS_OUTPUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_jobs)
        
        logger.info(f"✓ Saved consolidated jobs to:")
        logger.info(f"  {MASTER_JOBS_OUTPUT}")
    else:
        logger.warning("⚠ No jobs to consolidate")
    
    return len(all_jobs), sources_info


def print_summary(total_links, link_sources, total_jobs, job_sources):
    """Print summary statistics"""
    logger.info("\n" + "="*80)
    logger.info("CONSOLIDATION SUMMARY")
    logger.info("="*80)
    
    logger.info("\nJob Links by Source:")
    for source, count in sorted(link_sources.items()):
        logger.info(f"  • {source.upper()}: {count:,} links")
    logger.info(f"  TOTAL: {total_links:,} job links")
    
    logger.info("\nJobs by Source:")
    for source, count in sorted(job_sources.items()):
        logger.info(f"  • {source.upper()}: {count:,} jobs")
    logger.info(f"  TOTAL: {total_jobs:,} jobs")
    
    # Calculate statistics from consolidated jobs if available
    if os.path.exists(MASTER_JOBS_OUTPUT):
        try:
            with open(MASTER_JOBS_OUTPUT, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                jobs = list(reader)
            
            # Unique companies
            companies = set()
            for job in jobs:
                company = job.get('company_name', '').strip()
                if company:
                    companies.add(company)
            
            # Unique locations
            locations = set()
            for job in jobs:
                location = job.get('location', '').strip()
                if location:
                    locations.add(location)
            
            logger.info(f"\nAdditional Statistics:")
            logger.info(f"  • Unique companies: {len(companies)}")
            logger.info(f"  • Unique locations: {len(locations)}")
        except:
            pass
    
    logger.info("\n" + "="*80)
    logger.info("OUTPUT FILES:")
    logger.info("="*80)
    logger.info(f"  Job Links: {MASTER_LINKS_OUTPUT}")
    logger.info(f"  Jobs:      {MASTER_JOBS_OUTPUT}")
    logger.info("="*80 + "\n")


def main():
    """Main consolidation function"""
    logger.info("\n" + "="*80)
    logger.info("MASTER JOB CONSOLIDATION")
    logger.info("Combining data from all job scraping sources")
    logger.info("="*80)
    logger.info(f"Project root: {PROJECT_ROOT}")
    
    # Consolidate links
    total_links, link_sources = consolidate_job_links()
    
    # Consolidate jobs
    total_jobs, job_sources = consolidate_jobs()
    
    # Print summary
    print_summary(total_links, link_sources, total_jobs, job_sources)


if __name__ == '__main__':
    main()
