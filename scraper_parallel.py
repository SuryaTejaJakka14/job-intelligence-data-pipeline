"""
Complete working scraper for jobs.nvoids.com
Converts IST timestamps to PST and filters for today's jobs only.
INCLUDES AUTOMATIC CHROMEDRIVER UPDATES
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    MAX_WORKERS,
    SEARCH_KEYWORDS,
    MAX_PAGES_PER_SEARCH,
    BROWSER_WAIT_TIME
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

def update_chromedriver_automatically(max_retries=3):
    """
    Automatically update ChromeDriver to match installed Chrome version.
    Includes retry logic and exponential backoff for reliability.
    
    Args:
        max_retries: Maximum number of retry attempts
        
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n" + "="*70)
    print("CHROMEDRIVER AUTO-UPDATE CHECK")
    print("="*70 + "\n")
    
    for attempt in range(max_retries):
        try:
            # Get installed Chrome version
            chrome_version = get_installed_chrome_version()
            
            if not chrome_version:
                print("⚠ Could not detect Chrome version - using cached ChromeDriver")
                logging.warning("Chrome version detection failed")
                return False
            
            # Only clear cache on first attempt to preserve fallback option
            if attempt == 0:
                print("🔄 Clearing ChromeDriver cache...")
                wdm_cache = os.path.expanduser("~/.wdm")
                if os.path.exists(wdm_cache):
                    import shutil
                    try:
                        shutil.rmtree(wdm_cache)
                        logging.info("✓ Cleared WebDriver Manager cache")
                        print("✓ Cleared WebDriver Manager cache")
                    except Exception as e:
                        logging.warning(f"Could not clear cache: {e}")
                        print(f"⚠ Could not clear cache, continuing...")
            
            # Download matching ChromeDriver
            print(f"📥 Downloading ChromeDriver for Chrome {chrome_version}... (attempt {attempt + 1}/{max_retries})")
            manager = ChromeDriverManager()
            driver_path = manager.install()
            
            logging.info(f"✓ ChromeDriver updated to {chrome_version}")
            logging.info(f"✓ ChromeDriver path: {driver_path}")
            print(f"✓ ChromeDriver downloaded successfully")
            print(f"✓ ChromeDriver path: {driver_path}")
            
            # Fix permissions (critical for macOS)
            try:
                os.chmod(driver_path, 0o755)
                logging.info("✓ Fixed ChromeDriver permissions")
                print("✓ Fixed ChromeDriver permissions")
            except Exception as e:
                logging.warning(f"Could not set permissions: {e}")
            
            # Remove quarantine (macOS security)
            try:
                result = subprocess.run(
                    ['xattr', '-d', 'com.apple.quarantine', driver_path],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    logging.info("✓ Removed macOS quarantine attribute")
                    print("✓ Removed macOS quarantine attribute")
            except Exception as e:
                logging.warning(f"Could not remove quarantine: {e}")
            
            print("\n" + "="*70)
            print("✓ CHROMEDRIVER AUTO-UPDATE COMPLETE")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            logging.error(f"✗ ChromeDriver update failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            print(f"✗ Update failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 2, 4, 8 seconds
                wait_time = 2 ** (attempt + 1)
                print(f"  Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("  All retries exhausted - using cached ChromeDriver\n")
                logging.warning("ChromeDriver update failed after all retries, using cached version")
                return False
    
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
    """
    Set up Chrome WebDriver with retry logic and exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        
    Returns:
        WebDriver instance
        
    Raises:
        Exception if all retries fail
    """
    for attempt in range(max_retries):
        try:
            chrome_options = Options()
            
            if HEADLESS_BROWSER:
                chrome_options.add_argument('--headless=new')
            
            # Stability options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument(f'user-agent={USER_AGENT}')
            
            # Prevent crashes
            chrome_options.add_argument('--disable-crash-reporter')
            chrome_options.add_argument('--disable-in-process-stack-traces')
            
            service = get_chrome_service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logging.info(f"✓ WebDriver created successfully (attempt {attempt + 1})")
            return driver
            
        except Exception as e:
            logging.error(f"✗ Driver setup failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                # Exponential backoff: 2, 4, 8 seconds
                wait_time = 2 ** (attempt + 1)
                logging.info(f"Retrying driver setup in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logging.error("All driver setup retries exhausted")
                raise

def validate_chromedriver():
    """
    Validate ChromeDriver by attempting to create and use a driver.
    Used as a health check before starting scheduled jobs.
    
    Returns:
        bool: True if ChromeDriver is working, False otherwise
    """
    driver = None
    try:
        logging.info("Running ChromeDriver health check...")
        print("\n🔍 Running ChromeDriver health check...")
        
        driver = setup_driver(max_retries=2)
        driver.get("about:blank")
        
        logging.info("✓ ChromeDriver health check passed")
        print("✓ ChromeDriver health check passed\n")
        return True
        
    except Exception as e:
        logging.error(f"✗ ChromeDriver health check failed: {str(e)}")
        print(f"✗ ChromeDriver health check failed: {str(e)}\n")
        return False
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

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
    """
    Check if job was posted today in PST (current day only).
    
    Jobs are filtered strictly by the current PST date.
    Only jobs posted on today's date in PST will be accepted.
    """
    pst_dt = convert_ist_to_pst(ist_time_str)
    
    if not pst_dt:
        return False
    
    today_pst = datetime.now(PST).date()
    job_date_pst = pst_dt.date()
    
    # Accept jobs from today only in PST
    is_today = job_date_pst == today_pst
    
    if is_today:
        logging.info(f"✓ Job timestamp '{ist_time_str}' → PST: {pst_dt.strftime('%Y-%m-%d %I:%M %p')} - ACCEPTED")
    else:
        logging.info(f"✗ Job timestamp '{ist_time_str}' → PST: {pst_dt.strftime('%Y-%m-%d %I:%M %p')} - FILTERED (not today)")
    
    return is_today

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

def search_jobs_on_nvoids(driver, search_keyword):
    """
    Perform a search on jobs.nvoids.com using Selenium.
    
    Args:
        driver: Selenium WebDriver instance
        search_keyword: Keyword to search for (e.g., 'java developer')
        
    Returns:
        bool: True if search was successful
    """
    try:
        print(f"\n   Navigating to jobs.nvoids.com...")
        driver.get("https://jobs.nvoids.com")
        logging.info(f"Navigated to jobs.nvoids.com")
        
        # Wait for page to load
        time.sleep(2)
        
        # Find the search box - try multiple possible selectors
        print(f"   Looking for search box...")
        search_box = None
        
        # Try common search input selectors
        search_selectors = [
            (By.NAME, "keyword"),
            (By.NAME, "search"),
            (By.ID, "keyword"),
            (By.ID, "search"),
            (By.CSS_SELECTOR, "input[type='text']"),
            (By.CSS_SELECTOR, "input[placeholder*='search' i]"),
            (By.CSS_SELECTOR, "input[placeholder*='keyword' i]"),
            (By.XPATH, "//input[@type='text']"),
        ]
        
        for selector_type, selector_value in search_selectors:
            try:
                search_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                print(f"   ✓ Found search box using {selector_type}: {selector_value}")
                break
            except:
                continue
        
        if not search_box:
            logging.error("Search box not found on page")
            print("   ✗ Could not find search box")
            return False
        
        # Clear the search box and enter keyword
        print(f"   Entering search keyword: '{search_keyword}'")
        search_box.clear()
        search_box.send_keys(search_keyword)
        time.sleep(1)
        
        # Submit the search (press Enter)
        print(f"   Submitting search...")
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results to load
        time.sleep(3)
        
        logging.info(f"Search completed for keyword: {search_keyword}")
        print(f"   ✓ Search results loaded")
        
        return True
        
    except Exception as e:
        logging.error(f"Error performing search for '{search_keyword}': {str(e)}")
        print(f"   ✗ Search error: {str(e)}")
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
    Scrape jobs using automated search with configurable keywords.
    Uses SEARCH_KEYWORDS from config.py and parallel processing for job details.
    
    Args:
        unused_url: Ignored (for compatibility)
        max_workers: Number of parallel workers for scraping job details
        
    Returns:
        list: Combined unique jobs from all search keywords
    """
    if max_workers is None:
        max_workers = MAX_WORKERS
    
    all_jobs = []
    seen_job_ids = set()
    driver = None
    
    try:
        # ============================================================
        # AUTO-UPDATE CHROMEDRIVER AT START
        # ============================================================
        update_chromedriver_automatically()
        
        today_pst = datetime.now(PST).date()
        
        print(f"\n{'='*70}")
        print(f"AUTOMATED JOB SEARCH BOT - PARALLEL MODE WITH DATE FILTERING")
        print(f"{'='*70}")
        print(f"Search Keywords: {SEARCH_KEYWORDS}")
        print(f"Max Workers: {max_workers}")
        print(f"Headless Mode: {HEADLESS_BROWSER}")
        print(f"Today (PST): {today_pst}")
        print(f"{'='*70}\n")
        
        # ============================================================
        # SEARCH FOR EACH KEYWORD
        # ============================================================
        for keyword_idx, search_keyword in enumerate(SEARCH_KEYWORDS, 1):
            print(f"\n🔍 Search {keyword_idx}/{len(SEARCH_KEYWORDS)}: '{search_keyword}'")
            print(f"{'─'*70}")
            
            try:
                # Set up browser for this search
                driver = setup_driver()
                
                # Perform search
                search_success = search_jobs_on_nvoids(driver, search_keyword)
                
                if not search_success:
                    print(f"   ✗ Search failed for '{search_keyword}', skipping...")
                    driver.quit()
                    driver = None
                    continue
                
                # Get page source and parse
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # ============================================================
                # EXTRACT JOB URLs WITH DATE FILTERING
                # ============================================================
                job_urls = []
                today_job_urls = []
                
                # Find the job table (usually the second table on the page)
                tables = soup.find_all('table')
                if len(tables) < 2:
                    print(f"   ✗ Job table not found")
                    driver.quit()
                    driver = None
                    continue
                
                job_table = tables[1] if len(tables) > 1 else tables[0]
                rows = job_table.find_all('tr')
                
                print(f"   Found {len(rows)-1} job listings")
                
                # Parse each row to extract URL and timestamp
                for row_idx, row in enumerate(rows[1:], 1):  # Skip header row
                    cells = row.find_all('td')
                    
                    if len(cells) < 3:
                        continue
                    
                    # Last cell contains the timestamp
                    timestamp_cell = cells[-1].get_text(strip=True)
                    
                    # Check if job was posted today (in PST)
                    if not is_today_pst_job(timestamp_cell):
                        continue
                    
                    # Extract job URL from the row
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
                
                print(f"   ✓ Filtered to {len(today_job_urls)} recent jobs (posted today in PST)")
                
                if not today_job_urls:
                    print(f"   No jobs posted today for this keyword")
                    driver.quit()
                    driver = None
                    continue
                
                job_urls = today_job_urls
                
                # Close the search browser
                driver.quit()
                driver = None
                
                # ============================================================
                # PARALLEL SCRAPING OF JOB DETAILS
                # ============================================================
                print(f"   🔄 Scraping {len(job_urls)} jobs with {max_workers} workers...\n")
                
                keyword_jobs = []
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {executor.submit(scrape_job_detail, url): url for url in job_urls}
                    
                    for idx, future in enumerate(as_completed(futures), 1):
                        try:
                            job = future.result()
                            if job:
                                # Check for duplicates across keywords
                                if job['job_id'] not in seen_job_ids:
                                    keyword_jobs.append(job)
                                    seen_job_ids.add(job['job_id'])
                                    print(f"   [{idx}/{len(job_urls)}] ✓ {job['title'][:45]}... - {job['email']}")
                                else:
                                    print(f"   [{idx}/{len(job_urls)}] ⊘ Duplicate: {job['title'][:45]}...")
                        except Exception as e:
                            logging.error(f"Error processing job: {str(e)}")
                
                all_jobs.extend(keyword_jobs)
                print(f"\n   ✓ Added {len(keyword_jobs)} unique jobs from '{search_keyword}'")
                print(f"   Total unique jobs so far: {len(all_jobs)}")
                
                # Wait between searches
                if keyword_idx < len(SEARCH_KEYWORDS):
                    print(f"\n   ⏱ Waiting before next search...")
                    time.sleep(3)
                    
            except Exception as e:
                logging.error(f"Error searching for '{search_keyword}': {str(e)}")
                print(f"   ✗ Error: {str(e)}")
                if driver:
                    driver.quit()
                    driver = None
                continue
        
        # ============================================================
        # FINAL SUMMARY
        # ============================================================
        print(f"\n{'='*70}")
        print(f"ALL SEARCHES COMPLETE")
        print(f"{'='*70}")
        print(f"Keywords searched: {len(SEARCH_KEYWORDS)}")
        print(f"Total unique jobs: {len(all_jobs)}")
        print(f"{'='*70}\n")
        
        logging.info(f"Parallel scraping complete: {len(all_jobs)} unique jobs from {len(SEARCH_KEYWORDS)} keywords")
        
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
        print(f"\n✅ Found {len(jobs)} recent jobs:\n")
        for idx, job in enumerate(jobs[:5], 1):
            print(f"[{idx}] {job['title']}")
            print(f"    📧 {job['email']}\n")
    else:
        print("\n⚠ No recent jobs found")

if __name__ == "__main__":
    test_parallel_scraper()
