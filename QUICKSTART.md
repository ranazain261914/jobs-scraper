# Quick Start Guide

## First Time Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the scraper:**
   ```bash
   python analysis/run_all.py
   ```

3. **View results:**
   ```bash
   cat data/final/all_jobs.csv
   ```

## Usage with Existing Data

To run analysis without scraping:
```bash
python analysis/run_all.py --skip-scraping
```

Done! Check `data/final/` for your results.
