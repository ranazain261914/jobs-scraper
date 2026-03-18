# Job Scraping Pipeline - Complete Documentation

## Overview

This project implements a complete job scraping system that extracts job listings from three major career platforms:

1. **Greenhouse** - https://www.greenhouse.com/careers/opportunities
2. **Ashby** - https://www.ashbyhq.com/careers  
3. **Punjab Jobs** - https://jobs.punjab.gov.pk/new_recruit/jobs

## Project Features

✅ **Multi-source extraction** - Scrapes from 3 different job platforms  
✅ **Robust link extraction** - Uses Selenium for dynamic content  
✅ **Structured data parsing** - Extracts 10+ fields per job  
✅ **Data cleaning** - Normalizes, deduplicates, validates  
✅ **Comprehensive analysis** - Generates insights and statistics  
✅ **Git workflow** - Full feature branch workflow  
✅ **Error handling** - Graceful fallbacks and logging  

## Architecture

```
job-scraper/
├── selenium/                          # Selenium-based scrapers
│   ├── __init__.py
│   ├── selenium_utils.py              # WebDriver utilities
│   ├── utils.py                       # Common utilities
│   ├── greenhouse_scraper.py          # Greenhouse link extractor
│   ├── ashby_scraper.py               # Ashby link extractor
│   ├── punjab_scraper.py              # Punjab link extractor
│   ├── extract_links.py               # Master link extraction
│   ├── job_parser.py                  # Job detail parser
│   └── extract_job_data.py            # Job data extraction
├── analysis/
│   └── analysis.py                    # Data analysis module
├── data/
│   ├── raw/
│   │   └── job_links.csv              # Extracted job links
│   └── final/
│       ├── jobs.csv                   # Raw job data
│       └── jobs_cleaned.csv           # Cleaned job data
├── data_cleaning.py                   # Data cleaning orchestrator
├── run_pipeline.py                    # Master orchestration script
├── requirements.txt                   # Dependencies
├── README.md                          # Main documentation
├── .gitignore                         # Git ignore rules
└── docs/
    └── GITHUB_SETUP.md               # GitHub setup guide
```

## Installation & Setup

### Prerequisites

- Python 3.9 or higher
- Chrome or Firefox browser
- Git
- ~2 GB free disk space

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/job-scraper.git
cd job-scraper
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Run Complete Pipeline

Run all steps automatically:

```bash
python run_pipeline.py
```

This will:
1. Extract job links from all 3 websites
2. Visit each link and extract job data
3. Clean and normalize the data
4. Generate analysis and insights

**Estimated time:** 2-3 hours for 500+ jobs

### Option 2: Run Individual Steps

#### Step 1: Extract Job Links

```bash
cd selenium
python extract_links.py
```

**Output:** `data/raw/job_links.csv`

**Fields:**
- `url` - Job link
- `source` - Website (greenhouse/ashby/punjab)
- `extracted_at` - Extraction timestamp

**Duration:** 5-15 minutes

---

#### Step 2: Extract Job Data

```bash
cd selenium
python extract_job_data.py
```

**Output:** `data/final/jobs.csv`

**Extracted Fields:**
- `job_title` - Position name
- `company_name` - Hiring company
- `location` - Job location
- `department` - Department/Team
- `employment_type` - Full-time, Part-time, Contract, Internship
- `posted_date` - When job was posted
- `job_url` - Direct job link
- `job_description` - Full job description (first 2000 chars)
- `required_skills` - Extracted key skills
- `experience_level` - Junior, Mid, Senior, etc.
- `source` - Website source
- `extracted_at` - Extraction timestamp

**Duration:** 1-2 hours for 500 jobs

---

#### Step 3: Clean Data

```bash
python data_cleaning.py
```

**Input:** `data/final/jobs.csv`  
**Output:** `data/final/jobs_cleaned.csv`

**Operations:**
- Remove duplicate URLs
- Normalize location names
- Standardize employment types
- Remove incomplete records
- Extract and normalize skills
- Clean text fields

**Duration:** < 1 minute

---

#### Step 4: Analyze Results

```bash
cd analysis
python analysis.py
```

**Output:** `analysis/analysis_results.json`

**Generated Statistics:**
- Top 15 required skills
- Top 15 job locations
- Top 15 hiring companies
- Top 15 job titles
- Employment type distribution
- Entry-level opportunity count
- Experience level distribution
- Source distribution

**Duration:** < 2 minutes

## Data Fields

### Required Fields (Always Present)
- **job_title** - Job position name
- **job_url** - Direct link to job posting

### Common Fields
- **company_name** - Hiring organization
- **location** - Job location (normalized)
- **employment_type** - Type of position
- **job_description** - Full job description (truncated)
- **required_skills** - Key skills (comma-separated)
- **source** - Data source (greenhouse/ashby/punjab)

### Optional Fields
- **department** - Team/Department
- **posted_date** - Posting date
- **experience_level** - Required experience (Junior/Mid/Senior)

## Git Workflow

### Branches

```
main                          ← Stable releases (tagged)
  ↑
  └─ develop                  ← Integration branch
       ↑
       ├─ feature/link-extractor
       ├─ feature/job-scraper
       ├─ feature/data-analysis
       └─ bugfix/*
```

### Key Commands

**Create feature branch:**
```bash
git checkout develop
git checkout -b feature/your-feature
```

**Commit changes:**
```bash
git add .
git commit -m "feature/your-feature: Description of changes"
```

**Push to GitHub:**
```bash
git push -u origin feature/your-feature
```

**Merge to develop:**
```bash
git checkout develop
git merge feature/your-feature
git push origin develop
```

**Create release:**
```bash
git checkout main
git merge develop
git tag -a v1.0 -m "Release version 1.0"
git push origin main --tags
```

## Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Optional configuration
SELENIUM_HEADLESS=true
REQUEST_TIMEOUT=30
RETRY_COUNT=3
```

### Selenium Settings

Edit `selenium/selenium_utils.py`:

```python
# Change headless mode
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Remove to see browser
```

### Link Extraction Selectors

Customize CSS selectors in:
- `selenium/greenhouse_scraper.py`
- `selenium/ashby_scraper.py`
- `selenium/punjab_scraper.py`

## Troubleshooting

### Issue: "No links extracted"

**Solutions:**
1. Check website structure hasn't changed
2. Test with `headless=False` to see what browser sees
3. Verify internet connection
4. Check website isn't blocking automated access

### Issue: "Module not found"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "WebDriver error"

**Solution:**
```bash
pip install --upgrade selenium webdriver-manager
```

### Issue: "Memory errors with large datasets"

**Solution:**
```python
# Process in batches in extract_job_data.py
extractor.extract_job_data(limit=100)  # Process 100 jobs at a time
```

## Performance Notes

- **Link extraction:** 2-5 min per website (5-15 min total)
- **Job data extraction:** 1-2 hours for 500+ jobs
- **Data cleaning:** < 1 minute
- **Analysis:** < 2 minutes
- **Total pipeline:** 2-3 hours for ~500 jobs

## Best Practices

✅ **Do:**
- Use WebDriverWait instead of time.sleep()
- Add delays between requests (2-5 seconds)
- Validate extracted links before using
- Remove duplicate entries
- Clean and normalize data
- Write modular, well-commented code
- Commit frequently with clear messages
- Test with small samples first

❌ **Don't:**
- Make rapid requests without delays
- Extract data without validation
- Hardcode selectors without fallbacks
- Skip error handling
- Commit directly to main branch
- Store API keys in code

## Data Privacy & Legal

⚠️ **Important:**

This tool is for **educational and research purposes only**. Before scraping:

1. Check the website's `robots.txt`
2. Review Terms of Service
3. Ensure you have permission
4. Respect rate limits
5. Don't overload servers
6. Handle personal data carefully

## Extending the Project

### Adding a New Website

1. Create `new_site_scraper.py` in `selenium/`
2. Implement `NewSiteExtractor` class
3. Add to `extract_links.py` orchestrator
4. Create feature branch and merge

### Adding Analysis

1. Add analysis function to `analysis/analysis.py`
2. Update `JobAnalyzer.analyze()` method
3. Add visualization if desired

### Adding Data Export

1. Create export function in `data_cleaning.py`
2. Support CSV, JSON, Excel formats
3. Add to pipeline

## Support & Contributing

Issues? Questions?

1. Check existing documentation
2. Review error logs
3. Test with small dataset
4. Check GitHub issues
5. Create detailed bug report

## License

MIT License - See LICENSE file

## Version History

**v1.0.0** (Initial Release)
- Link extraction from 3 websites
- Job data extraction
- Data cleaning
- Market analysis
- Full git workflow

## Author

GitHub User  
2026

## Changelog

### v1.0.0
- Initial release
- 3 website support
- 10+ data fields
- Complete analysis suite

---

**Last Updated:** March 2026  
**Documentation Version:** 1.0
