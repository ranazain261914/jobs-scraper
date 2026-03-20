# Job Scraping System - Implementation Guide

## Overview

A professional, modular Python-based job scraping system that extracts job listings from:
1. **Greenhouse** - https://www.greenhouse.com/careers/opportunities
2. **Punjab** - https://jobs.punjab.gov.pk/new_recruit/jobs
3. **Ashby** - https://www.ashbyhq.com/careers

## Architecture

```
├── config.py                      # Configuration and constants
├── scrapers/
│   ├── base_scraper.py           # Base class for all scrapers
│   ├── scraper_greenhouse.py     # Greenhouse-specific implementation
│   ├── scraper_punjab.py         # Punjab-specific implementation
│   └── scraper_ashby.py          # Ashby-specific implementation
├── utilities/
│   ├── consolidator.py           # Consolidates data from all sources
│   └── verifier.py               # Verifies scraping accuracy
└── data/
    ├── raw/                      # Raw extracted links
    └── final/                    # Processed job data
```

## Installation

```bash
pip install -r requirements.txt
```

## Running the Scraping Pipeline

### Option 1: Run All Sources (Recommended)

```bash
# Run Greenhouse
python -m scrapers.scraper_greenhouse

# Run Punjab
python -m scrapers.scraper_punjab

# Run Ashby
python -m scrapers.scraper_ashby

# Consolidate data
python -m utilities.consolidator

# Verify results
python -m utilities.verifier
```

### Option 2: Run Individual Scraper

```bash
# Just Greenhouse
python scrapers/scraper_greenhouse.py

# Just Punjab
python scrapers/scraper_punjab.py

# Just Ashby
python scrapers/scraper_ashby.py
```

## Output Files

### Raw Data (Extracted Links)
- `data/raw/job_links_greenhouse.csv`
- `data/raw/job_links_punjab.csv`
- `data/raw/job_links_ashby.csv`
- `data/raw/all_job_links.csv` (consolidated)

### Final Data (Job Details)
- `data/final/jobs_greenhouse.csv`
- `data/final/jobs_punjab.csv`
- `data/final/jobs_ashby.csv`
- `data/final/all_jobs.csv` (consolidated)

## CSV Fields

Each job record contains:
- `job_title`: Position name
- `company_name`: Company/Organization
- `location`: Job location
- `employment_type`: Full-time, Part-time, etc.
- `posted_date`: Posting date (if available)
- `job_description`: Full job description
- `job_url`: Direct link to job posting
- `source`: Source website (greenhouse, punjab, ashby)
- `department`: Department (if available)
- `skills`: Required skills (if available)
- `extracted_at`: Timestamp of extraction

## Key Features

✅ **Modular Architecture** - Easy to add new sources
✅ **Base Scraper Class** - Common functionality for all sources
✅ **Configurable Options** - Centralized config.py
✅ **Error Handling** - Graceful error handling with logging
✅ **Data Consolidation** - Automatic deduplication and merging
✅ **Verification** - Compare scraped counts with actual website counts
✅ **Professional Logging** - Detailed execution logs

## Technical Details

### Greenhouse Implementation
- Loads page with Selenium
- Clicks "Load More" buttons to get all jobs
- Extracts links from job sections
- Parses individual job pages

### Punjab Implementation
- Uses DataTables pagination controls
- Sets table to show 100 rows at once
- Extracts links from table rows
- Handles DataTables AJAX reloading

### Ashby Implementation
- Attempts API-based extraction first (preferred)
- Falls back to Selenium with JS rendering
- Scrolls to load dynamically loaded content
- Extracts job links from rendered page

## Configuration

Edit `config.py` to customize:
- Selenium options (headless mode, etc.)
- Timeouts and delays
- Output directory paths
- CSV field names

## Troubleshooting

### Chrome Driver Issues
```bash
pip install --upgrade webdriver-manager
```

### API Extraction Not Working
The Ashby scraper will automatically fall back to Selenium rendering.

### Timeout Issues
Increase values in `config.py`:
```python
TIMEOUTS = {
    'page_load': 20,        # Increased from 15
    'element_wait': 15,     # Increased from 10
    ...
}
```

## Git Workflow

```bash
# Create develop branch
git checkout -b develop

# Create feature branch
git checkout -b feature/link-extractor

# Work on feature, then
git add .
git commit -m "feat: extract job links from greenhouse"

# Create pull request to develop
# After review, merge to develop

# When ready for release, merge develop to main
git checkout main
git merge develop
git tag v1.0
```

## Performance

Typical execution times:
- Greenhouse: 2-4 minutes
- Punjab: 1-2 minutes  
- Ashby: 2-3 minutes
- Consolidation: <1 second
- Verification: 3-5 minutes

**Total Pipeline: 10-15 minutes**

## Version History

- **v1.0** (2026-03-20): Initial production release
  - Greenhouse scraper working
  - Punjab scraper working (all 53 jobs)
  - Ashby scraper with API fallback
  - Data consolidation
  - Automated verification

## Support

For issues:
1. Check logs in console output
2. Review extracted CSV files manually
3. Verify Chrome browser is installed
4. Check internet connection
5. Try running individual scrapers in isolation

## License

MIT License - See LICENSE file
