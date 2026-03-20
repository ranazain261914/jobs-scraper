"""
Verification Script

Compares scraped job counts with actual website counts
Helps verify scraping accuracy
"""

import logging
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from config import WEBSITES, OUTPUT_FILES, TIMEOUTS


class JobCountVerifier:
    """Verifies scraped job counts against actual website counts"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('verifier')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def verify_all(self) -> dict:
        """Verify all sources"""
        self.logger.info("\n" + "="*80)
        self.logger.info("JOB COUNT VERIFICATION")
        self.logger.info("="*80)
        
        results = {}
        
        # Verify each source
        results['greenhouse'] = self.verify_greenhouse()
        results['punjab'] = self.verify_punjab()
        results['ashby'] = self.verify_ashby()
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def verify_greenhouse(self) -> dict:
        """Verify Greenhouse job count"""
        self.logger.info("\n[GREENHOUSE]")
        
        scraped_count = self._get_scraped_count('greenhouse')
        actual_count = self._count_greenhouse_jobs()
        
        result = {
            'source': 'greenhouse',
            'actual_count': actual_count,
            'scraped_count': scraped_count,
            'difference': actual_count - scraped_count if actual_count else 'N/A',
            'match': abs(actual_count - scraped_count) <= 2 if actual_count else False
        }
        
        self._log_result(result)
        return result
    
    def _count_greenhouse_jobs(self) -> int:
        """Count jobs on Greenhouse website"""
        try:
            self.logger.info("  Counting jobs on website...")
            
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            
            try:
                driver.get(WEBSITES['greenhouse']['url'])
                time.sleep(4)
                
                # Try to find job count indicator
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Look for "X opportunities" or similar text
                page_text = soup.get_text()
                
                # Count job listings (usually in divs with job info)
                job_sections = soup.find_all('div', class_=lambda x: x and 'job' in x.lower())
                count = len(job_sections)
                
                if count > 0:
                    self.logger.info(f"  ✓ Found {count} job listings on Greenhouse")
                    return count
                else:
                    self.logger.warning("  Could not determine job count from website")
                    return 0
            finally:
                driver.quit()
        
        except Exception as e:
            self.logger.error(f"  Error counting Greenhouse jobs: {e}")
            return 0
    
    def verify_punjab(self) -> dict:
        """Verify Punjab job count"""
        self.logger.info("\n[PUNJAB]")
        
        scraped_count = self._get_scraped_count('punjab')
        actual_count = self._count_punjab_jobs()
        
        result = {
            'source': 'punjab',
            'actual_count': actual_count,
            'scraped_count': scraped_count,
            'difference': actual_count - scraped_count if actual_count else 'N/A',
            'match': abs(actual_count - scraped_count) <= 2 if actual_count else False
        }
        
        self._log_result(result)
        return result
    
    def _count_punjab_jobs(self) -> int:
        """Count jobs on Punjab website"""
        try:
            self.logger.info("  Counting jobs on website...")
            
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            
            try:
                driver.get(WEBSITES['punjab']['url'])
                time.sleep(2)
                
                # Set DataTable to 100 rows
                length_select = driver.find_element(By.NAME, "myTable_length")
                length_select.click()
                time.sleep(0.3)
                
                option = length_select.find_element(By.CSS_SELECTOR, "option[value='100']")
                option.click()
                
                time.sleep(2)
                
                # Count table rows
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table = soup.find('table', {'id': 'myTable'})
                
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    count = len(rows)
                    
                    self.logger.info(f"  ✓ Found {count} job listings on Punjab")
                    return count
                else:
                    self.logger.warning("  Could not find job table")
                    return 0
            finally:
                driver.quit()
        
        except Exception as e:
            self.logger.error(f"  Error counting Punjab jobs: {e}")
            return 0
    
    def verify_ashby(self) -> dict:
        """Verify Ashby job count"""
        self.logger.info("\n[ASHBY]")
        
        scraped_count = self._get_scraped_count('ashby')
        actual_count = self._count_ashby_jobs()
        
        result = {
            'source': 'ashby',
            'actual_count': actual_count,
            'scraped_count': scraped_count,
            'difference': actual_count - scraped_count if actual_count else 'N/A',
            'match': abs(actual_count - scraped_count) <= 2 if actual_count else False
        }
        
        self._log_result(result)
        return result
    
    def _count_ashby_jobs(self) -> int:
        """Count jobs on Ashby website"""
        try:
            self.logger.info("  Counting jobs on website...")
            
            options = Options()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            
            try:
                driver.get(WEBSITES['ashby']['url'])
                time.sleep(3)
                
                # Scroll to load all jobs
                last_height = driver.execute_script("return document.body.scrollHeight")
                for _ in range(5):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    
                    new_height = driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                
                # Count job links
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_links = soup.find_all('a', class_=lambda x: x and 'job' in x.lower())
                count = len(job_links)
                
                if count > 0:
                    self.logger.info(f"  ✓ Found {count} job listings on Ashby")
                    return count
                else:
                    self.logger.warning("  Could not determine job count from website")
                    return 0
            finally:
                driver.quit()
        
        except Exception as e:
            self.logger.error(f"  Error counting Ashby jobs: {e}")
            return 0
    
    def _get_scraped_count(self, source: str) -> int:
        """Get count of scraped jobs for source"""
        links_file = OUTPUT_FILES[source]['links']
        
        if not links_file.exists():
            self.logger.warning(f"  ⚠ No scraped links file found for {source}")
            return 0
        
        try:
            with open(links_file, 'r', encoding='utf-8') as f:
                count = sum(1 for _ in csv.DictReader(f))
            self.logger.info(f"  Scraped: {count} jobs")
            return count
        except Exception as e:
            self.logger.error(f"  Error reading scraped count: {e}")
            return 0
    
    def _log_result(self, result: dict):
        """Log verification result"""
        actual = result['actual_count']
        scraped = result['scraped_count']
        diff = result['difference']
        
        self.logger.info(f"  Actual website count: {actual}")
        self.logger.info(f"  Scraped count: {scraped}")
        
        if isinstance(diff, int):
            if diff == 0:
                self.logger.info(f"  ✓ MATCH - Difference: 0")
            elif abs(diff) <= 2:
                self.logger.info(f"  ✓ CLOSE - Difference: {diff} (within tolerance)")
            else:
                self.logger.warning(f"  ⚠ MISMATCH - Difference: {diff}")
                if actual > 0:
                    pct = (abs(diff) / actual) * 100
                    self.logger.warning(f"  ({pct:.1f}% difference)")
        else:
            self.logger.warning(f"  ⚠ Could not determine actual count")
    
    def _print_summary(self, results: dict):
        """Print verification summary"""
        self.logger.info("\n" + "="*80)
        self.logger.info("VERIFICATION SUMMARY")
        self.logger.info("="*80)
        
        for source, result in results.items():
            status = "✓" if result.get('match') else "⚠"
            self.logger.info(f"{status} {source.upper():12} | "
                           f"Actual: {result['actual_count']:3} | "
                           f"Scraped: {result['scraped_count']:3} | "
                           f"Diff: {str(result['difference']):3}")
        
        self.logger.info("="*80 + "\n")


def main():
    """Main entry point"""
    verifier = JobCountVerifier()
    verifier.verify_all()


if __name__ == '__main__':
    main()
