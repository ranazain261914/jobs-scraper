# Job Scraping System

A comprehensive Python-based job scraping system using Selenium and Scrapy to extract job data from multiple career websites.

## Overview

This project extracts job listings from three major job platforms:
1. **Greenhouse** - https://www.greenhouse.com/careers/opportunities
2. **Ashby** - https://www.ashbyhq.com/careers
3. **Punjab Jobs** - https://jobs.punjab.gov.pk/new_recruit/jobs

## Features

- ✅ Multi-website job link extraction
- ✅ Structured job data extraction (title, company, location, salary, skills, etc.)
- ✅ Data cleaning and normalization
- ✅ Duplicate removal
- ✅ Comprehensive data analysis
- ✅ CSV/JSON export
- ✅ Full Git workflow with feature branches

## Project Structure

```
job-scraper/
├── selenium/                    # Selenium-based scrapers
│   ├── greenhouse_scraper.py
│   ├── ashby_scraper.py
│   └── punjab_scraper.py
├── scrapy_project/             # Scrapy project (if needed)
├── data/
│   ├── raw/
│   │   └── job_links.csv       # Extracted links
│   └── final/
│       └── jobs.csv            # Final processed data
├── analysis/
│   ├── analysis.py             # Data analysis scripts
│   └── visualizations/
├── docs/                        # Documentation
├── README.md
├── .gitignore
└── requirements.txt
```

## Installation

### Prerequisites
- Python 3.9+
- Git
- Chrome/Firefox for Selenium

### Setup

1. Clone the repository:
```bash
git clone <github-repo-url>
cd job-scraper
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Extract Job Links

```bash
# Extract links from all websites
python selenium/extract_links.py
```

This creates `data/raw/job_links.csv` with all job links.

### 2. Extract Job Data

```bash
python selenium/extract_job_data.py
```

This visits each link and extracts detailed job information.

### 3. Clean and Process Data

```bash
python data_cleaning.py
```

### 4. Run Analysis

```bash
python analysis/analysis.py
```

## Data Fields Extracted

- **Job Title**: Position name
- **Company Name**: Hiring company
- **Location**: Job location
- **Department**: Department/Team
- **Employment Type**: Full-time, Part-time, Contract, etc.
- **Posted Date**: When job was posted
- **Job URL**: Direct link to job posting
- **Job Description**: Full description text
- **Required Skills**: Key skills needed
- **Experience Level**: Junior, Mid, Senior (if available)

## Git Workflow

This project follows a feature-branch workflow:

```
main (stable releases)
  ↑
develop (integration)
  ↑
feature/link-extractor (Greenhouse, Ashby, Punjab)
feature/job-scraper (Job data extraction)
feature/data-analysis (Analysis & visualization)
bugfix/* (Bug fixes)
```

### Branch Commands

```bash
# Create feature branch
git checkout -b feature/link-extractor

# Push to GitHub
git push -u origin feature/link-extractor

# Merge to develop
git checkout develop
git merge feature/link-extractor
git push origin develop
```

## Data Analysis

The analysis module generates:

- **Top Skills**: Most demanded skills
- **Top Locations**: Cities with most jobs
- **Companies Hiring Most**: Company rankings
- **Entry-level Opportunities**: Internship/junior positions
- **Common Job Titles**: Most frequent positions

## Error Handling

For any issues:

1. Create a bugfix branch:
```bash
git checkout -b bugfix/issue-name develop
```

2. Fix the issue and test

3. Merge back:
```bash
git checkout develop
git merge bugfix/issue-name
```

## Best Practices

- ✅ Use WebDriverWait for Selenium (no time.sleep)
- ✅ Add delays between requests (2-5 seconds)
- ✅ Validate extracted links
- ✅ Remove duplicate entries
- ✅ Clean and normalize data
- ✅ Modular, well-commented code
- ✅ Regular git commits with clear messages

## Performance Notes

- Initial link extraction: ~2-5 minutes per website
- Job data extraction: ~1-2 hours for 500+ jobs
- Data cleaning: < 1 minute
- Analysis: < 2 minutes

## Troubleshooting

### Selenium issues
- Ensure Chrome/Firefox is installed
- Update WebDriver via webdriver-manager
- Check internet connection and website availability

### Data extraction issues
- Websites may have updated their HTML structure
- Add delays between requests if getting blocked
- Check robots.txt for scraping policies

## License

MIT License - See LICENSE file for details

## Author

GitHub User - 2026

## Version

v1.0.0
