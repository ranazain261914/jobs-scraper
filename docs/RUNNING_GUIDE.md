# 🚀 Complete System Running Guide

This document provides step-by-step instructions to run the entire job scraping system.

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser (installed)
- Internet connection
- ~30 MB disk space for dependencies

## Step 1: Install Dependencies

```powershell
cd path/to/scrap-pnjb-green
pip install -r requirements.txt
```

This will install:
- selenium==4.15.2
- pandas>=2.0.0
- requests==2.31.0
- beautifulsoup4==4.12.2
- webdriver-manager==4.0.1

## Step 2: Run Individual Scrapers

### Option A: Test with Greenhouse Only (Fastest)

```powershell
python -m scrapers.scraper_greenhouse
```

Expected output:
- Console logs showing progress
- Files created:
  - `data/raw/job_links_greenhouse.csv`
  - `data/final/jobs_greenhouse.csv`

**Time: 3-4 minutes**

### Option B: Run All Three Scrapers

```powershell
# Greenhouse (3-4 min)
python -m scrapers.scraper_greenhouse

# Punjab (1-2 min)
python -m scrapers.scraper_punjab

# Ashby (2-3 min)
python -m scrapers.scraper_ashby
```

**Total Time: 8-10 minutes**

## Step 3: Consolidate Data

After scraping, merge all data:

```powershell
python -m utilities.consolidator
```

Output:
- `data/raw/all_job_links.csv` - All extracted links
- `data/final/all_jobs.csv` - All job details

**Time: <1 second**

## Step 4: Verify Results

Compare scraped counts with actual website counts:

```powershell
python -m utilities.verifier
```

This will:
1. Open each website in Chrome
2. Count visible jobs
3. Compare with scraped counts
4. Report accuracy

**Time: 3-5 minutes**

## Complete Pipeline (One-by-One)

```powershell
# Install
pip install -r requirements.txt

# Scrape Greenhouse
python -m scrapers.scraper_greenhouse

# Scrape Punjab
python -m scrapers.scraper_punjab

# Scrape Ashby
python -m scrapers.scraper_ashby

# Consolidate
python -m utilities.consolidator

# Verify
python -m utilities.verifier
```

**Total Time: 15-20 minutes**

## Checking Results

### View Extracted Data

```powershell
# List all CSV files created
Get-ChildItem -Path data\final\ -Filter *.csv

# Count lines in each file
$files = Get-ChildItem -Path data\final\ -Filter *.csv
foreach ($file in $files) {
    $lines = (Get-Content $file.FullName | Measure-Object -Line).Lines
    Write-Output "$($file.Name): $lines rows"
}
```

### Open in Excel/Spreadsheet

```powershell
# Open consolidated data
Start-Process data\final\all_jobs.csv

# Or open raw links
Start-Process data\raw\all_job_links.csv
```

### Quick Statistics

```powershell
# Count total jobs
$jobs = Import-Csv data\final\all_jobs.csv
$jobs.Count

# Count by source
$jobs | Group-Object -Property source | Select Name, Count
```

## Troubleshooting

### Issue: "No such file or directory: requirements.txt"

```powershell
# Make sure you're in the correct directory
cd "C:\path\to\scrap-pnjb-green"
dir requirements.txt
```

### Issue: Chrome driver not found

```powershell
pip install --upgrade webdriver-manager
```

### Issue: No jobs extracted from any source

1. Check internet connection
2. Verify websites are accessible
3. Check Chrome is installed
4. Try single scraper with explicit path:

```powershell
python scrapers/scraper_greenhouse.py
```

### Issue: Timeout errors

Edit `config.py` and increase timeouts:

```python
TIMEOUTS = {
    'page_load': 25,           # Increase from 15
    'element_wait': 15,        # Increase from 10
    'between_requests': 1.0,   # Increase from 0.5
    'between_jobs': 2.0,       # Increase from 1.0
}
```

### Issue: Permission denied saving files

```powershell
# Clear old data and try again
Remove-Item -Path data\raw\* -Force
Remove-Item -Path data\final\* -Force

# Run scraper again
python -m scrapers.scraper_greenhouse
```

## Understanding the Console Output

### Successful Execution

```
2026-03-20 10:30:00 - INFO - ════════════════════════════════════════════════════════════════════════════════
2026-03-20 10:30:00 - INFO - GREENHOUSE JOBS - LINK EXTRACTION
2026-03-20 10:30:00 - INFO - ════════════════════════════════════════════════════════════════════════════════
2026-03-20 10:30:01 - INFO - [STEP 1] Waiting for jobs to load...
2026-03-20 10:30:05 - INFO -   ✓ Page loaded
2026-03-20 10:30:05 - INFO - [STEP 2] Extracting job links...
2026-03-20 10:30:06 - INFO - [STEP 3] Saving job links...
2026-03-20 10:30:07 - INFO - ✓ Saved 45 links to data/raw/job_links_greenhouse.csv

✓ Extracted 45 job links from Greenhouse

[PHASE 2/2] PARSING JOB DETAILS
Will parse 45 jobs...
  Parsing: [1/45] jobs...
  Parsing: [5/45] jobs...
  Parsing: [10/45] jobs...
  ...
✓ Successfully parsed 43 jobs
```

### Error Handling

If you see errors like:
```
⚠ Some warnings while parsing
✗ Failed to parse URL: https://example.com/job/123
```

This is normal - some jobs may not parse perfectly. The system continues and reports success rate at the end.

## Output File Examples

### job_links_greenhouse.csv
```
url,source,extracted_at
https://www.greenhouse.com/careers/...,greenhouse,2026-03-20T10:30:00
https://www.greenhouse.com/careers/...,greenhouse,2026-03-20T10:30:00
```

### jobs_greenhouse.csv
```
job_title,company_name,location,employment_type,posted_date,job_description,job_url,source,department,skills,extracted_at
Senior Engineer,Company Inc,San Francisco,Full-time,2026-03-15,"We're looking for...",https://...,greenhouse,,Python;JavaScript,2026-03-20T10:30:00
```

## Next Steps

1. ✅ Run `pip install -r requirements.txt`
2. ✅ Run `python -m scrapers.scraper_greenhouse` (test)
3. ✅ Check `data/final/jobs_greenhouse.csv` for data
4. ✅ Run all three scrapers
5. ✅ Run `python -m utilities.consolidator`
6. ✅ Run `python -m utilities.verifier`
7. ✅ Analyze results in CSV files

## Performance Tips

1. **First run is slowest** - WebDriver downloads Chrome driver
2. **Run overnight** if running repeatedly
3. **Use single source** while testing
4. **Monitor disk space** - CSVs can grow large with many jobs

## Getting Help

1. Check console output for error messages
2. Review the [Implementation Guide](IMPLEMENTATION_GUIDE.md)
3. Check the [README.md](../README.md)
4. Review individual scraper files for detailed comments

---

**Ready?** Run this now:

```powershell
pip install -r requirements.txt
python -m scrapers.scraper_greenhouse
```

Then check the results in `data/final/jobs_greenhouse.csv`!
