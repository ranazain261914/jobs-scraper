# 🚀 QUICKSTART GUIDE

## Installation

```powershell
# Install required packages
pip install -r requirements.txt
```

## Running the Scrapers

### Option 1: Get the Master Consolidated Data (Fastest)
```powershell
python consolidate_jobs.py
```
**Time:** <1 second  
**Output:** 
- `data/raw/all_job_links.csv` (104 job links)
- `data/final/all_jobs.csv` (103 complete jobs)

### Option 2: Scrape Individual Sources
```powershell
# Punjab Government Jobs (53 jobs, ~3 min)
python scraper_punjab.py

# Remote.com / Greenhouse Jobs (50 jobs, ~4 min)
python scraper_greenhouse.py

# Consolidate the results
python consolidate_jobs.py
```

### Option 3: Full Automated Pipeline
```powershell
# Scrape all sources and consolidate (7-8 minutes total)
python master_scraper.py
```

## Understanding the Output

### Master Files (Use These!)
- **`data/final/all_jobs.csv`** - 103 complete job records with all details
- **`data/raw/all_job_links.csv`** - 104 job posting URLs

### Data Fields in all_jobs.csv
```
job_title          - Position name
company_name       - Company hiring
location          - Job location
job_description   - Full job description
employment_type   - Full-time, Part-time, etc.
posted_date       - Date posted
source            - Data source (punjab/greenhouse)
job_url           - Direct link to job
extracted_at      - Extraction timestamp
```

## Project Structure

```
├── scraper_punjab.py          ✅ Working (53 jobs)
├── scraper_greenhouse.py      ✅ Working (50 jobs)
├── scraper_ashby.py           ⚠️  Framework (needs API work)
├── consolidate_jobs.py        ✅ Main consolidation tool
├── master_scraper.py          ✅ Full pipeline orchestrator
│
├── data/
│   ├── raw/                   Raw job links (CSV files)
│   └── final/                 Processed job data (CSV files)
│
├── QUICKSTART.md              This file
├── PROJECT_DESCRIPTION.md     Complete technical documentation
└── requirements.txt           Python dependencies
```

## Quick Examples

### View extracted data
```powershell
# Open in Excel or Python
Import-Csv 'data/final/all_jobs.csv' | Format-Table -AutoSize
```

### Count records
```powershell
@(Import-Csv 'data/final/all_jobs.csv').Count
# Output: 103 jobs
```

### Get jobs by location
```powershell
Import-Csv 'data/final/all_jobs.csv' | Where-Object {$_.location -like "*Lahore*"}
```

## Troubleshooting

**Q: No jobs extracted?**
- Check internet connection
- Verify Chrome browser is installed
- Run individual scrapers for more details

**Q: Selenium errors?**
- ChromeDriver may need updating
- Check if Chrome version matches Selenium version

**Q: CSV not opening in Excel?**
- Files are UTF-8 encoded
- Excel may need to import as Text file

## Statistics

- **Total Jobs:** 103
- **Total Links:** 104
- **Success Rate:** 98%
- **Data Sources:** 2 active (Punjab, Greenhouse)
- **Unique Companies:** 2
- **Unique Locations:** 20
- **Dataset Size:** 165 KB

## For More Information

See `PROJECT_DESCRIPTION.md` for:
- Complete technical documentation
- Architecture and design
- Data extraction methods
- Known limitations
- Future enhancements
