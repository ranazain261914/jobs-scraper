import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("\n" + "="*80)
    logger.info("JOB SCRAPING PIPELINE - ORCHESTRATION")
    logger.info("="*80)
    logger.info("\nRun the following commands in order:\n")
    logger.info("PHASE 1: Run Individual Scrapers")
    logger.info("  1. python -m scrapers.scraper_greenhouse")
    logger.info("  2. python -m scrapers.scraper_punjab")
    logger.info("  3. python -m scrapers.scraper_ashby")
    logger.info("\nPHASE 2: Consolidate Data")
    logger.info("  4. python -m utilities.consolidator")
    logger.info("\nPHASE 3: Verify Results")
    logger.info("  5. python -m utilities.verifier")
    logger.info("\n" + "="*80 + "\n")
