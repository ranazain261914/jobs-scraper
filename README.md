# Job Scraping & Analysis Pipeline

A professional, modular job scraping system using Selenium and BeautifulSoup to collect and analyze job listings from multiple sources.

## 📁 Project Structure

```
.
├── selenium/                 # Browser automation scripts and utilities
│   ├── base_scraper.py      # Abstract base class for all scrapers
│   ├── scraper_punjab.py    # Punjab government jobs scraper
│   ├── scraper_greenhouse.py # Greenhouse/Remote.com scraper
│   ├── scraper_ashby.py     # Ashby careers scraper
│   ├── consolidator.py      # Merges and deduplicates job data
│   ├── verifier.py          # Validates extracted data
│   ├── config.py            # Configuration and settings
│   └── __init__.py
│
├── analysis/                 # Analysis and reporting scripts
│   ├── analyze_jobs.py      # Job market insights extraction
│   ├── run_all.py           # Master orchestration script
│   └── __init__.py
│
├── data/
│   ├── raw/                 # Extracted links (intermediate)
│   │   ├── job_links_punjab.csv
│   │   ├── job_links_greenhouse.csv
│   │   ├── job_links_ashby.csv
│   │   └── all_job_links.csv
│   └── final/               # Final consolidated datasets ✨ Tracked in Git
│       ├── all_jobs.csv                    # Master file (252 jobs)
│       ├── jobs_punjab.csv                 # Punjab jobs (53)
│       ├── jobs_greenhouse.csv             # Greenhouse jobs (50)
│       ├── jobs_ashby.csv                  # Ashby Kraken jobs (149)
│       └── HIRING_INSIGHTS_REPORT.md       # Analysis report
│
├── docs/                    # Documentation
│   ├── PROJECT_OVERVIEW.md  # Project overview and setup
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── REFACTORING_SUMMARY.md
│   ├── RUNNING_GUIDE.md
│   ├── QUICKSTART.md
│   └── PROJECT_DESCRIPTION.md
│
├── logs/                    # Execution logs
├── .gitignore              # Git ignore patterns
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Review configuration
cat selenium/config.py
```

### 2. Run Complete Pipeline

```bash
# Full pipeline: scrape + consolidate + analyze (8 minutes)
python analysis/run_all.py

# Use existing data (skip scraping, 0.5 seconds)
python analysis/run_all.py --skip-scraping

# Skip analysis phase
python analysis/run_all.py --skip-analysis
```

### 3. View Results

```bash
# Master job file (104 jobs)
cat data/final/all_jobs.csv

# Analysis report with insights
cat data/final/HIRING_INSIGHTS_REPORT.md
```

## 📊 Data & Analysis

### Consolidated Dataset
- **Total Jobs:** 252
- **Sources:** Punjab (53), Greenhouse (50), Ashby Kraken (149)
- **Success Rate:** 100%
- **Location:** `data/final/all_jobs.csv`
- **Status:** ✨ Tracked in Git for easy sharing

### Latest Run
```
Scraping Phase:     ✅ 3/3 scrapers successful
Consolidation:      ✅ 252 unique jobs
Analysis:           ✅ Report generated
Execution Time:     755 seconds (12.6 min)
```

### Analysis Features
- Top in-demand skills extraction
- Job distribution by source and location
- Entry-level position identification
- Market trend analysis
- Company hiring patterns
- Geographic distribution analysis
- Company hiring volume ranking
- Entry-level position detection
- Job title categorization (8 families)
- Markdown report generation

## 🔧 Architecture

### Core Components

**Selenium Module** (`selenium/`)
- `BaseScraper`: Abstract class with common functionality
  - WebDriver management
  - Page loading and HTML parsing
  - CSV export
  - Logging
- Individual scrapers: Inherit from BaseScraper, implement source-specific extraction
- `consolidator.py`: Merges CSVs and deduplicates
- `verifier.py`: Validates data integrity
- `config.py`: Centralized configuration

**Analysis Module** (`analysis/`)
- `run_all.py`: Master orchestrator (CLI options, progress tracking)
- `analyze_jobs.py`: JobAnalyzer class with methods:
  - `extract_top_skills()`: Regex-based skill matching
  - `get_geographic_distribution()`: Location analysis
  - `get_top_companies()`: Hiring volume ranking
  - `count_entry_level_positions()`: Career level detection
  - `get_job_title_families()`: Role categorization
  - `generate_report()`: Markdown report generation

### Data Flow

```
Scraper 1        Scraper 2        Scraper 3
    ↓                ↓                 ↓
  Links           Links             Links
(raw/*.csv)      (raw/*.csv)       (raw/*.csv)
    ↓                ↓                 ↓
    └────────────────┴─────────────────┘
                     ↓
            Parse Job Details
            (final/jobs_*.csv)
                     ↓
            Consolidate (all_jobs.csv)
                     ↓
            Analyze & Report
            (HIRING_INSIGHTS_REPORT.md)
```

## 📋 CSV Schema

### all_jobs.csv
| Column | Type | Description |
|--------|------|-------------|
| job_title | string | Position title |
| company_name | string | Company/Organization |
| location | string | Job location |
| employment_type | string | Full-time, Part-time, Contract, etc. |
| posted_date | string | Publication date |
| job_description | text | Full job posting text |
| job_url | string | Link to original job posting |
| source | string | Data source (punjab, greenhouse, ashby) |
| department | string | Department (if available) |
| skills | string | Required/desired skills (comma-separated) |
| extracted_at | datetime | When the job was extracted |

## 🔍 Troubleshooting

### Issue: `ModuleNotFoundError` for selenium
**Solution:** Ensure you've installed dependencies:
```bash
pip install -r requirements.txt
```

### Issue: WebDriver timeout errors
**Solution:** Check website accessibility and adjust timeouts in `selenium/config.py`

### Issue: Empty results for a scraper
**Solution:** 
1. Check target URL in `selenium/config.py`
2. Verify website structure hasn't changed
3. Review logs in `logs/` directory

### Issue: CSV encoding errors on Windows
**Solution:** All files use UTF-8 encoding. Specify encoding when opening:
```python
import csv
with open('file.csv', encoding='utf-8') as f:
    reader = csv.DictReader(f)
```

## 📚 Documentation

See `docs/` directory for detailed guides:
- **PROJECT_OVERVIEW.md** - Architecture and design decisions
- **IMPLEMENTATION_GUIDE.md** - Extending the system
- **RUNNING_GUIDE.md** - Detailed execution instructions
- **QUICKSTART.md** - Quick reference

## �️ Development

### Adding a New Scraper

1. Create `selenium/scraper_newsource.py`
2. Inherit from `BaseScraper`
3. Implement `extract_links()` and `extract_job_details()` methods
4. Update `selenium/config.py` with source details
5. Update `analysis/run_all.py` if needed

### Modifying Analysis

Edit `analysis/analyze_jobs.py`:
- Adjust skill patterns in regex
- Add new metrics to JobAnalyzer class
- Update report generation in `generate_report()` method

## 📦 Dependencies

- **selenium** 4.15.2 - Browser automation
- **beautifulsoup4** 4.12.2 - HTML parsing
- **requests** 2.31.0 - HTTP requests
- **pandas** 2.0+ - Data processing
- **webdriver-manager** 4.0.1 - WebDriver management

See `requirements.txt` for all dependencies.

## 📝 License

See individual source files for license information.

## 👤 Author

Created as part of professional job market analysis project.

---

**Last Updated:** March 2026
**Status:** ✅ Production Ready
**Test Coverage:** 104 jobs across 3 sources

### ✅ Data Quality
- Duplicate removal
- Data validation
- Verification against website counts
- Structured CSV output

### ✅ Professional Practices
- Type hints throughout
- Comprehensive docstrings
- Centralized configuration
- Graceful error handling

## 🔧 Technologies

| Component | Technology |
|-----------|-----------|
| Scraping | Selenium WebDriver |
| API Calls | Requests library |
| Parsing | BeautifulSoup 4 |
| Data Processing | Pandas, CSV |
| Logging | Python logging |
| Browser | Chrome/Chromium |

## 📊 Data Output

### CSV Fields (all_jobs.csv)
```
job_title        - Position title
company_name     - Hiring organization
location         - Job location
employment_type  - Full-time, Part-time, etc.
posted_date      - Publication date
job_description  - Full job description
job_url          - Direct link to job
source           - Data source (greenhouse, punjab, ashby)
department       - Department (if available)
skills           - Required skills (if available)
extracted_at     - Extraction timestamp
```

## 🔍 How It Works

### Phase 1: Link Extraction
1. Load careers page using Selenium
2. Handle JavaScript rendering (React, Vue, etc.)
3. Extract job links from listings
4. Remove duplicates
5. Save to CSV

### Phase 2: Job Detail Extraction
1. Visit each job URL
2. Parse HTML to extract structured data
3. Handle missing fields gracefully
4. Save complete job data

### Phase 3: Consolidation
1. Merge data from all sources
2. Remove duplicate job URLs
3. Generate consolidated CSV files
4. Provide statistics

### Phase 4: Verification
1. Count jobs on each website
2. Compare with scraped counts
3. Report differences
4. Verify system accuracy

## ⚙️ Configuration

Edit `config.py` to customize:
```python
# Selenium Options
SELENIUM_OPTIONS = {
    'headless': False,              # Show browser window
    'no_sandbox': True,
    'disable_blink': True,          # Avoid detection
}

# Timeouts
TIMEOUTS = {
    'page_load': 15,                # Page load timeout
    'element_wait': 10,             # Element wait timeout
    'between_requests': 0.5,        # Delay between requests
}
```

## 📈 Performance

Typical execution times:
| Source | Time | Jobs |
|--------|------|------|
| Greenhouse | 3-4 min | 20-50 |
| Punjab | 1-2 min | 40-60 |
| Ashby | 2-3 min | 10-30 |
| Consolidation | <1 sec | N/A |
| Verification | 3-5 min | N/A |
| **TOTAL** | **10-15 min** | **70-140** |

## 🔐 Best Practices Implemented

✅ **Respect Websites**
- Reasonable delays between requests
- User-Agent headers
- No aggressive scraping

✅ **Error Handling**
- Try-catch blocks throughout
- Graceful degradation
- Detailed error logging

✅ **Code Quality**
- DRY principle (Don't Repeat Yourself)
- Type hints for clarity
- Comprehensive docstrings
- Professional naming

✅ **Git Workflow**
- Develop branch for work
- Feature branches for new features
- Clear commit messages
- Ready for GitHub

## 🐛 Troubleshooting

### Problem: Chrome driver not found
```bash
pip install --upgrade webdriver-manager
```

### Problem: "No jobs extracted"
1. Check internet connection
2. Verify the website is accessible
3. Run single scraper with logging
4. Check console output for errors

### Problem: Timeout errors
Increase timeout values in `config.py`:
```python
TIMEOUTS = {
    'page_load': 20,        # Increase from 15
    'element_wait': 15,     # Increase from 10
}
```

### Problem: Permission denied on CSV files
```bash
# Clear old data
rm -r data/raw/* data/final/*
# Try again
python -m scrapers.scraper_greenhouse
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup
- **[docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)** - Full documentation
- **[PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md)** - Technical details

## 🔄 Git Workflow

```bash
# Create develop branch
git checkout -b develop

# Create feature branch
git checkout -b feature/link-extractor

# Make changes, then
git add .
git commit -m "feat: extract job links from greenhouse"

# Create pull request
# After review, merge to develop
# When ready, merge develop to main
```

## 📝 Example Usage

### Count extracted jobs
```bash
wc -l data/final/jobs_*.csv
```

### View jobs from specific location
```bash
grep "London" data/final/all_jobs.csv
```

### Get unique companies
```bash
cut -d',' -f2 data/final/all_jobs.csv | sort -u
```

### Export to other formats
```python
import pandas as pd
df = pd.read_csv('data/final/all_jobs.csv')
df.to_excel('all_jobs.xlsx', index=False)
```

## 🎓 Learning Outcomes

This project demonstrates:
- ✅ Professional Python development
- ✅ Web scraping with Selenium
- ✅ HTML parsing with BeautifulSoup
- ✅ Data processing with Pandas/CSV
- ✅ API integration
- ✅ Error handling and logging
- ✅ Git/GitHub workflow
- ✅ Code organization and architecture
- ✅ Documentation best practices

## 📞 Support

For issues:
1. Check console output for error messages
2. Review CSV files for data quality
3. Verify Chrome browser is installed
4. Check internet connection
5. See [IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md) for detailed help

## 📄 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

Built with:
- Selenium WebDriver
- BeautifulSoup 4
- Requests
- Pandas
- Python 3.8+

---

**Ready to start?** Run this command:

```bash
python -m scrapers.scraper_greenhouse
```

Check `data/final/jobs_greenhouse.csv` for results!

For detailed instructions, see [QUICKSTART.md](QUICKSTART.md)
