# Workday Job Application Bot

Automated job application bot that searches for **Workday-related roles** on jobs.nvoids.com and sends personalized emails with your resume.

## 🎯 What This Bot Does

This is a **Workday-specific version** of the job application bot. It:
- Searches for Workday consultant, developer, HCM, and integration roles
- Filters jobs based on Workday-specific keywords
- Automatically sends personalized emails with your resume
- Tracks applications to prevent duplicates
- **Auto-updates ChromeDriver** to match your Chrome version
- Runs on a schedule or on-demand
- Supports parallel processing for faster scraping

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Settings

Edit `config.py`:

```python
# Email credentials (use Gmail App Password)
SENDER_EMAIL = "your.email@gmail.com"
SENDER_PASSWORD = "your-16-char-app-password"

# Path to your Workday-focused resume
RESUME_PATH = "/path/to/your/Workday_Resume.docx"

# Workday search keywords (already configured)
SEARCH_KEYWORDS = [
    'workday',
    'workday developer',
    'workday consultant',
    'workday integration',
    'workday hcm'
]

# Set to True for testing, False for live mode
DRY_RUN = True

# Parallel processing workers (1 = stable, 2-3 = faster)
MAX_WORKERS = 1
```

### 3. Get Gmail App Password

1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Generate App Password for "Mail"
4. Copy the 16-character password to `config.py`

## 🚀 Usage Options

### Option 1: Run Once (Testing/Manual)

Best for testing or running manually when you want to apply to jobs.

```bash
# Test the scraper (no emails sent)
python scraper.py

# Run full workflow once
python main.py
```

**How to use:**
- Edit `main.py` and make sure `run_once()` is uncommented (line 195)
- Comment out `run_scheduled()` (line 198)

### Option 2: Scheduled Mode (Automated - RECOMMENDED)

Runs automatically every 30 minutes with advanced scheduling features.

```bash
# Edit main.py first:
# 1. Comment out: run_once()
# 2. Uncomment: use_preset_business_hours() and run_scheduled()

python main.py
```

**Features:**
- Runs every 30 minutes automatically
- Configurable working hours (9 AM - 6 PM by default)
- Auto-resets daily limits at midnight
- Continuous operation (press Ctrl+C to stop)

**Configuration:**
Edit `scheduler_config.py` to customize:
- Run interval (default: 30 minutes)
- Working hours (default: business hours)
- Days of week
- Auto-reset behavior

**Presets available:**
```python
use_preset_business_hours()  # 9 AM - 6 PM, Mon-Fri
use_preset_extended_hours()  # 7 AM - 11 PM, Mon-Sun
use_preset_24_7()            # 24/7 operation
```

### Option 3: Parallel Processing (Faster, Today's Jobs Only)

Scrapes today's jobs using parallel workers for speed.

```bash
# Test parallel scraper
python scraper_parallel.py

# Run with parallel processing (once)
python main_parallel.py

# Run with parallel processing (scheduled)
python main_parallel_scheduled.py
```

**Note**: Parallel mode scrapes from the main job list (not search-based). It filters for today's jobs only and uses IST to PST timezone conversion. Requires very specific keywords to avoid false matches.

## 📊 Features

- ✅ **Workday-Specific Search**: Targets Workday consultant, developer, HCM, integration roles
- ✅ **Smart Filtering**: Filters by Workday-related keywords
- ✅ **Auto-Update ChromeDriver**: Automatically updates to match your Chrome version
- ✅ **Email Deduplication**: Never sends to the same email twice
- ✅ **Job ID Tracking**: Prevents duplicate applications
- ✅ **Daily Limits**: Configurable application limits
- ✅ **Parallel Processing**: Faster scraping with multiple workers
- ✅ **Automated Scheduling**: Run every 2 hours automatically
- ✅ **Comprehensive Logging**: Track all activities

## 📁 Files

### Core Files
- `config.py` - Configuration (Workday keywords, email, resume path)
- `scraper.py` - Search-based scraper for Workday jobs
- `main.py` - Standard application workflow

### Parallel/Scheduled Files
- `scraper_parallel.py` - Parallel scraper (faster, today's jobs only)
- `main_parallel.py` - Parallel processing workflow
- `main_parallel_scheduled.py` - Scheduled automation
- `scheduler_config.py` - Schedule configuration

### Utility Files
- `database.py` - CSV-based tracking system
- `email_sender.py` - Email automation
- `check_duplicates.py` - Duplicate analysis tool
- `test_email_send.py` - Email testing
- `test_filtering.py` - Filter testing
- `debug_page_str.py` - Page debugging tool

### Data Files
- `applied_jobs.csv` - Application history
- `logs/app.log` - Activity logs

## ⚙️ Configuration Options

### Search Keywords (Workday-Specific)
```python
SEARCH_KEYWORDS = [
    'workday',
    'workday developer',
    'workday consultant',
    'workday integration',
    'workday hcm'
]
```

### Target Keywords (Workday Roles)
```python
TARGET_KEYWORDS = [
    'workday',
    'hcm',
    'integration',
    'consultant',
    'developer',
    'analyst',
    'specialist',
    'architect',
    'administrator',
    'functional',
    'technical'
]
```

### Exclude Keywords
```python
EXCLUDE_KEYWORDS = [
    'intern',
    'internship',
    'junior',
    'entry level',
    'student',
    'trainee'
]
```

### Parallel Processing
```python
# Number of parallel workers
# 1 = Most stable (recommended for first run)
# 2-3 = Faster but uses more resources
MAX_WORKERS = 1
```

## 🔍 How It Works

### Standard Mode (scraper.py + main.py)
1. **Search**: Uses Selenium to search jobs.nvoids.com for Workday keywords
2. **Scrape**: Extracts job details from search results
3. **Filter**: Applies Workday-specific keyword filtering
4. **Deduplicate**: Checks against applied_jobs.csv
5. **Apply**: Sends personalized email with resume
6. **Track**: Records application in database

### Parallel Mode (scraper_parallel.py + main_parallel.py)
1. **Fetch**: Gets today's job list from jobs.nvoids.com
2. **Convert**: Converts IST timestamps to PST
3. **Filter**: Filters for today's jobs only
4. **Parallel Scrape**: Uses multiple workers to scrape job details
5. **Apply**: Same as standard mode
6. **Track**: Same as standard mode

## 📈 Monitoring & Utilities

### View Application Statistics
```bash
python database.py
```

### Check for Duplicate Emails
```bash
python check_duplicates.py
```

### Test Email Sending
```bash
python test_email_send.py
```

### Test Job Filtering
```bash
python test_filtering.py
```

### Check Logs
```bash
tail -f logs/app.log
```

## ⚠️ Important Notes

- **ChromeDriver Auto-Update**: The bot automatically updates ChromeDriver to match your Chrome version
- Start with `DRY_RUN = True` to test
- Use `MAX_WORKERS = 1` for stability (increase to 2-3 for speed)
- Respect rate limits (default: 10 seconds between emails)
- Update `RESUME_PATH` to your Workday-focused resume
- The bot searches jobs.nvoids.com (same site as Java bot)

## 🆚 Difference from Java Bot

This bot is identical in functionality but configured for **Workday roles**:
- Different search keywords (Workday vs Java)
- Different target keywords (Workday-specific)
- Different resume path (Workday resume)
- Separate tracking database

## 🔧 Troubleshooting

### ChromeDriver Issues
The bot auto-updates ChromeDriver, but if you encounter issues:
1. Check Chrome version: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --version`
2. Clear cache: `rm -rf ~/.wdm`
3. Run scraper again: `python scraper.py`

### No Jobs Found
1. Check `SEARCH_KEYWORDS` in config.py
2. Verify `TARGET_KEYWORDS` aren't too restrictive
3. Test with `HEADLESS_BROWSER = False` to see browser
4. Check internet connection

### Email Not Sending
1. Verify Gmail App Password (16 characters)
2. Check `SENDER_EMAIL` and `SENDER_PASSWORD`
3. Test with: `python test_email_send.py`
4. Check logs: `tail -f logs/app.log`

## 📝 License

This is a personal automation tool. Use responsibly and in accordance with the target website's terms of service.

