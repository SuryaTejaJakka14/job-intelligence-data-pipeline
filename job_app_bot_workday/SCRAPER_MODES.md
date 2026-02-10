# Understanding the Two Scraper Modes

## The Issue You Encountered

When you ran `python scraper_parallel.py`, it was showing Java jobs instead of Workday jobs, even though the config has Workday keywords.

## Why This Happened

The Workday bot has **two different scraping modes** that work differently:

### Mode 1: Search-Based Scraper (`scraper.py`)
- **How it works**: Searches jobs.nvoids.com for specific keywords (e.g., "workday", "workday developer")
- **Then filters**: Applies TARGET_KEYWORDS to the search results
- **Result**: Only gets Workday-related jobs from the start
- **Best for**: Finding specific Workday roles

### Mode 2: Parallel Scraper (`scraper_parallel.py`)  
- **How it works**: Gets ALL jobs posted today from the main job list
- **Then filters**: Applies TARGET_KEYWORDS to filter the results
- **Problem**: Generic keywords like 'developer', 'consultant', 'analyst' match Java jobs too!
- **Result**: Was showing Java jobs because "Java Developer" contains "developer"
- **Best for**: Fast processing of today's jobs (when keywords are specific enough)

## The Fix Applied

Updated `config.py` to use **more specific TARGET_KEYWORDS**:

**Before:**
```python
TARGET_KEYWORDS = [
    'workday',
    'hcm',
    'integration',
    'consultant',      # ← Too generic!
    'developer',       # ← Matches "Java Developer"
    'analyst',         # ← Too generic!
    'specialist',
    'architect',
    'administrator',
    'functional',
    'technical'
]
```

**After:**
```python
TARGET_KEYWORDS = [
    'workday',      # Primary keyword - most jobs should have this
    'hcm',          # Workday HCM
    # Generic keywords removed to avoid false matches in parallel scraper
]
```

## Recommendation

**For Workday job search, use the search-based scraper:**

```bash
cd job_app_bot_workday

# Test scraping
python scraper.py

# Full workflow
python main.py
```

This searches specifically for "workday" keywords first, so you only get relevant results.

**Only use parallel scraper if:**
- You want to process ALL today's jobs very quickly
- You're okay with very strict filtering (only 'workday' or 'hcm' in title)

## Alternative: Broader Keywords for Search-Based Mode

If you want to use broader keywords with the search-based scraper, you can add them back:

```python
TARGET_KEYWORDS = [
    'workday',
    'hcm',
    'integration',
    'consultant',    # OK for search-based since it already searched "workday"
    'developer',     # OK for search-based
    'analyst',
    # etc.
]
```

But this will cause issues with `scraper_parallel.py` again.

## Summary

- ✅ **Use `scraper.py` + `main.py`** for Workday job search (recommended)
- ⚠️ **Use `scraper_parallel.py`** only with very specific keywords
- 🔧 **Fixed**: Updated config to use specific keywords ('workday', 'hcm' only)
