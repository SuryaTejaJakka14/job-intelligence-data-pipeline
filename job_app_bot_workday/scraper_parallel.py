"""
Complete working scraper for jobs.nvoids.com - WORKDAY VERSION
Converts IST timestamps to PST and filters for today's jobs only.
Then filters by WORKDAY-specific keywords from config.py.
INCLUDES AUTOMATIC CHROMEDRIVER UPDATES
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import logging
import time
from datetime import datetime, timezone, timedelta
from pytz import timezone as tz
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import os
from config import (
    USER_AGENT,
    TARGET_KEYWORDS,
    EXCLUDE_KEYWORDS,
    MIN_YEARS_EXPERIENCE,
    HEADLESS_BROWSER,
    MAX_WORKERS
)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Timezone definitions
IST = tz('Asia/Kolkata')        # Indian Standard Time
PST = tz('America/Los_Angeles')  # Pacific Standard Time

CHROME_SERVICE = None

# ============================================================
# AUTOMATIC CHROMEDRIVER UPDATE
# ============================================================

def get_installed_chrome_version():
    """Get the installed Chrome browser version."""
    try:
        # macOS
        result = subprocess.run(
            ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            logging.info(f"✓ Installed Chrome version: {version}")
            print(f"✓ Installed Chrome version: {version}")
            return version
    except:
        pass
    
    try:
        # Linux
        result = subprocess.run(
            ['google-chrome', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1]
            logging.info(f"✓ Installed Chrome version: {version}")
            print(f"✓ Installed Chrome version: {version}")
            return version
    except:
        pass
    
    try:
        # Windows
        result = subprocess.run(
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\Binaries', '/v', 'pv'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split()[-1]
            logging.info(f"✓ Installed Chrome version: {version}")
            print(f"✓ Installed Chrome version: {version}")
            return version
    except:
        pass
    
    logging.warning("Could not detect Chrome version")
    return None

def update_chromedriver_automatically():
    """
    Automatically update ChromeDriver to match installed Chrome version.
    Clears cache and downloads latest matching version.
    """
    print("\n" + "="*70)
    print("CHROMEDRIVER AUTO-UPDATE CHECK")
    print("="*70 + "\n")
    
    try:
        # Get installed Chrome version
        chrome_version = get_installed_chrome_version()
        
        if not chrome_version:
            print("⚠ Could not detect Chrome version - using default ChromeDriver")
            logging.warning("Chrome version detection failed")
            return False
        
        # Clear WebDriver Manager cache
        print("🔄 Clearing ChromeDriver cache...")
        wdm_cache = os.path.expanduser("~/.wdm")
        if os.path.exists(wdm_cache):
            import shutil
            shutil.rmtree(wdm_cache)
            logging.info("✓ Cleared WebDriver Manager cache")
            print("✓ Cleared WebDriver Manager cache")
        
        # Download matching ChromeDriver
        print(f"📥 Downloading ChromeDriver for Chrome {chrome_version}...")
        manager = ChromeDriverManager()
        driver_path = manager.install()
        
        logging.info(f"✓ ChromeDriver updated to {chrome_version}")
        logging.info(f"✓ ChromeDriver path: {driver_path}")
        print(f"✓ ChromeDriver updated successfully")
        print(f"✓ ChromeDriver path: {driver_path}")
        
        # Fix permissions
        try:
            os.chmod(driver_path, 0o755)
            logging.info("✓ Fixed ChromeDriver permissions")
            print("✓ Fixed ChromeDriver permissions")
        except:
            pass
        
        # Remove quarantine (macOS)
        try:
            subprocess.run(['xattr', '-d', 'com.apple.quarantine', driver_path], check=False)
            logging.info("✓ Removed macOS quarantine attribute")
            print("✓ Removed macOS quarantine attribute")
        except:
            pass
        
        print("\n" + "="*70)
        print("✓ CHROMEDRIVER AUTO-UPDATE COMPLETE")
        print("="*70 + "\n")
        
        return True
        
    except Exception as e:
        logging.error(f"✗ ChromeDriver update failed: {str(e)}")
        print(f"✗ ChromeDriver update failed: {str(e)}")
        print("  Falling back to default ChromeDriver\n")
        return False

def get_chrome_service():
    """Get or create Chrome service (thread-safe singleton)."""
    global CHROME_SERVICE
    if CHROME_SERVICE is None:
        try:
            logging.info("Initializing ChromeDriver service...")
            print("Initializing ChromeDriver service...")
            
            CHROME_SERVICE = Service(ChromeDriverManager().install())
            logging.info("✓ ChromeDriver service initialized successfully")
            print("✓ ChromeDriver service initialized successfully")
        except Exception as e:
            logging.error(f"✗ Failed to initialize ChromeDriver: {str(e)}")
            print(f"✗ Failed to initialize ChromeDriver: {str(e)}")
            raise
    return CHROME_SERVICE

def setup_driver(max_retries=3):
    """Set up Chrome WebDriver with retry logic."""
    for attempt in range(max_retries):
        try:
            chrome_options = Options()
            
            if HEADLESS_BROWSER:
                chrome_options.add_argument('--headless=new')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={USER_AGENT}')
            
            service = get_chrome_service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logging.info(f"✓ WebDriver created (attempt {attempt + 1})")
            return driver
            
        except Exception as e:
            logging.error(f"✗ Driver setup failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                raise

def convert_ist_to_pst(ist_time_str):
    """Convert IST timestamp to PST."""
    try:
        ist_dt = datetime.strptime(ist_time_str.strip(), "%I:%M %p %d-%b-%y")
        ist_dt = IST.localize(ist_dt)
        pst_dt = ist_dt.astimezone(PST)
        
        return pst_dt
    
    except Exception as e:
        logging.warning(f"Failed to parse timestamp '{ist_time_str}': {e}")
        return None

def is_today_pst_job(ist_time_str):
    """Check if job was posted today (in PST)."""
    pst_dt = convert_ist_to_pst(ist_time_str)
    
    if not pst_dt:
        return False
    
    today_pst = datetime.now(PST).date()
    return pst_dt.date() == today_pst

def extract_email(text):
    """Extract email address from text."""
    if not text:
        return None
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    excluded = ['usjobs@nvoids.com', 'resumes@nvoids.com', 'nvoids.jobs@gmail.com']
    for email in matches:
        if email.lower() not in excluded:
            return email
    return None

def is_relevant_job(title):
    """Check if job title matches target roles."""
    title_lower = title.lower()
    for exclude in EXCLUDE_KEYWORDS:
        if exclude.lower() in title_lower:
            return False
    if not TARGET_KEYWORDS:
        return True
    for keyword in TARGET_KEYWORDS:
        if keyword.lower() in title_lower:
            return True
    return False

def scrape_job_detail(job_url):
    """Scrape individual job detail page."""
    driver = None
    try:
        driver = setup_driver()
        driver.get(job_url)
        time.sleep(1)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return None
        
        first_row = table.find('tr')
        if not first_row:
            return None
        
        title_text = first_row.get_text(strip=True)
        if ' at ' in title_text:
            title = title_text.split(' at ')[0].strip()
            location = title_text.split(' at ')[1].strip()
        else:
            title = title_text
            location = "Not specified"
        
        if not is_relevant_job(title):
            return None
        
        page_text = soup.get_text()
        email = extract_email(page_text)
        
        if not email:
            return None
        
        company = email.split('@')[1].split('.')[0].capitalize() if '@' in email else "Unknown"
        job_id = job_url.split('jid=')[1].split('&')[0] if 'jid=' in job_url else job_url
        
        return {
            'job_id': job_id,
            'title': title,
            'company': company,
            'email': email,
            'url': job_url,
            'location': location
        }
    
    except Exception as e:
        logging.error(f"Error scraping {job_url}: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

def scrape_jobs_parallel(unused_url=None, max_workers=None):
    """
    Scrape all jobs from the search page.
    Filters for jobs posted TODAY in PST (converted from IST).
    """
    if max_workers is None:
        max_workers = MAX_WORKERS
    
    all_jobs = []
    driver = None
    
    try:
        # ============================================================
        # AUTO-UPDATE CHROMEDRIVER AT START
        # ============================================================
        update_chromedriver_automatically()
        
        today_pst = datetime.now(PST).date()
        
        print(f"\n{'='*70}")
        print(f"JOB SCRAPER - IST TO PST CONVERSION")
        print(f"{'='*70}")
        print(f"Target: https://jobs.nvoids.com/search_sph.jsp")
        print(f"Today (PST): {today_pst}")
        print(f"{'='*70}\n")
        
        driver = setup_driver()
        driver.get("https://jobs.nvoids.com/search_sph.jsp")
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on page")
        
        if len(tables) < 2:
            print("✗ Expected table not found")
            return all_jobs
        
        job_table = tables[1] if len(tables) > 1 else tables[0]
        rows = job_table.find_all('tr')
        
        print(f"Found {len(rows)} rows in job table\n")
        
        today_job_urls = []
        
        for row_idx, row in enumerate(rows[1:], 1):
            cells = row.find_all('td')
            
            if len(cells) < 3:
                continue
            
            timestamp_cell = cells[-1].get_text(strip=True)
            
            if not is_today_pst_job(timestamp_cell):
                continue
            
            links = row.find_all('a', href=re.compile(r'job_details'))
            
            for link in links:
                href = link.get('href')
                if href:
                    if href.startswith('job_details'):
                        full_url = f"https://jobs.nvoids.com/{href}"
                    elif href.startswith('/'):
                        full_url = f"https://jobs.nvoids.com{href}"
                    else:
                        full_url = href
                    
                    if full_url not in today_job_urls:
                        today_job_urls.append(full_url)
        
        print(f"\n{'─'*70}")
        print(f"📋 Extracted {len(today_job_urls)} today's job URLs (PST)\n")
        
        if not today_job_urls:
            print("✗ No today's jobs found")
            return all_jobs
        
        print(f"🔄 Scraping {len(today_job_urls)} jobs with {max_workers} workers...\n")
        
        success = 0
        filtered = 0
        errors = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scrape_job_detail, url): url for url in today_job_urls}
            
            for idx, future in enumerate(as_completed(futures), 1):
                try:
                    job = future.result()
                    if job:
                        all_jobs.append(job)
                        success += 1
                        print(f"[{idx}/{len(today_job_urls)}] ✓ {job['title'][:50]}")
                        print(f"                  {job['email']}\n")
                    else:
                        filtered += 1
                except Exception as e:
                    errors += 1
        
        print(f"\n{'='*70}")
        print(f"SCRAPING COMPLETE - TODAY'S JOBS (PST)")
        print(f"{'='*70}")
        print(f"✓ Success: {success}")
        print(f"⊘ Filtered: {filtered}")
        print(f"✗ Errors: {errors}")
        print(f"📊 Total: {len(all_jobs)}")
        print(f"{'='*70}\n")
        
        logging.info(f"Scraped {len(all_jobs)} today's jobs (PST)")
        
        return all_jobs
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        logging.error(f"Error: {str(e)}")
        return all_jobs
    finally:
        if driver:
            driver.quit()

def test_parallel_scraper():
    """Test the parallel scraper."""
    jobs = scrape_jobs_parallel()
    if jobs:
        print(f"\n✅ Found {len(jobs)} jobs for today (PST):\n")
        for idx, job in enumerate(jobs[:5], 1):
            print(f"[{idx}] {job['title']}")
            print(f"    📧 {job['email']}\n")
    else:
        print("\n⚠ No jobs found for today (PST)")

if __name__ == "__main__":
    test_parallel_scraper()
