#!/usr/bin/env python3
"""
Master Job Scraping Orchestration Script

Runs the complete job scraping pipeline:
1. Extract job links
2. Extract job data
3. Clean and normalize data
4. Analyze results
"""

import logging
import os
import sys
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get project root
PROJECT_ROOT = Path(__file__).parent.resolve()


def run_script(script_path: str, description: str) -> bool:
    """
    Run a Python script and return success status.
    
    Args:
        script_path: Path to Python script
        description: Description of what the script does
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("\n" + "=" * 70)
        logger.info(f"STEP: {description}")
        logger.info("=" * 70)
        
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=False
        )
        
        logger.info(f"✓ {description} completed successfully\n")
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {description} failed with error code {e.returncode}\n")
        return False
    
    except Exception as e:
        logger.error(f"✗ Error running {description}: {e}\n")
        return False


def main():
    """Main orchestration function."""
    logger.info("\n" + "=" * 70)
    logger.info("JOB SCRAPING PIPELINE")
    logger.info("=" * 70)
    
    steps = [
        (
            os.path.join(PROJECT_ROOT, 'selenium', 'extract_links.py'),
            "Extract job links from all websites"
        ),
        (
            os.path.join(PROJECT_ROOT, 'selenium', 'extract_job_data.py'),
            "Extract job data from links"
        ),
        (
            os.path.join(PROJECT_ROOT, 'data_cleaning.py'),
            "Clean and normalize data"
        ),
        (
            os.path.join(PROJECT_ROOT, 'analysis', 'analysis.py'),
            "Analyze job market data"
        ),
    ]
    
    completed = 0
    failed = 0
    
    for script_path, description in steps:
        if not os.path.exists(script_path):
            logger.warning(f"✗ Script not found: {script_path}")
            failed += 1
            continue
        
        if run_script(script_path, description):
            completed += 1
        else:
            failed += 1
            # Continue with next step even if one fails
    
    # Print final summary
    logger.info("\n" + "=" * 70)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Completed:  {completed}/{len(steps)} steps")
    logger.info(f"Failed:     {failed}/{len(steps)} steps")
    
    if failed == 0:
        logger.info("✓ Pipeline completed successfully!")
        
        # Show output files
        logger.info("\nOutput files:")
        output_files = [
            os.path.join(PROJECT_ROOT, 'data', 'raw', 'job_links.csv'),
            os.path.join(PROJECT_ROOT, 'data', 'final', 'jobs.csv'),
            os.path.join(PROJECT_ROOT, 'data', 'final', 'jobs_cleaned.csv'),
            os.path.join(PROJECT_ROOT, 'analysis', 'analysis_results.json'),
        ]
        
        for file_path in output_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path) / 1024  # KB
                logger.info(f"  ✓ {file_path} ({file_size:.1f} KB)")
        
        return 0
    else:
        logger.error(f"✗ Pipeline failed: {failed} step(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
