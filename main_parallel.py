"""
Main file using PARALLEL scraping for faster job processing.
"""

import schedule
import time
import logging
import pandas as pd
from datetime import datetime
from scraper_parallel import scrape_jobs_parallel  # ← Import parallel version
from email_sender import send_application
from database import (
    initialize_database,
    is_already_applied,
    is_email_already_contacted,
    record_application,
    get_application_stats,
    get_todays_application_count
)
from config import (
    DELAY_BETWEEN_EMAILS,
    MAX_APPLICATIONS_PER_DAY,
    DRY_RUN
)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def process_applications_parallel(max_workers=3):
    """
    Main job application workflow using PARALLEL scraping.
    
    Args:
        max_workers (int): Number of parallel threads (3-5 recommended)
    """
    print(f"\n{'='*70}")
    print(f"Job Application Bot - PARALLEL MODE")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"Parallel Workers: {max_workers}")
    print(f"{'='*70}\n")
    
    logging.info("Starting new application cycle (PARALLEL)")
    initialize_database()
    
    today_count = get_todays_application_count()
    if today_count >= MAX_APPLICATIONS_PER_DAY:
        print(f"⚠ Daily limit reached ({today_count}/{MAX_APPLICATIONS_PER_DAY})")
        return
    
    print(f"Applications sent today: {today_count}/{MAX_APPLICATIONS_PER_DAY}\n")
    
    # ============================================================
    # PARALLEL SCRAPING HERE
    # ============================================================
    print("🔍 Starting parallel job search...\n")
    start_time = time.time()
    
    jobs = scrape_jobs_parallel(None, max_workers=max_workers)
    
    scrape_time = time.time() - start_time
    print(f"\n⏱ Scraping completed in {scrape_time:.1f} seconds")
    
    # Load applied jobs for deduplication
    print("\nLoading application history for deduplication...")
    df_applied = pd.read_csv('applied_jobs.csv')
    applied_emails = set(df_applied['email'].str.lower())
    applied_job_ids = set(df_applied['job_id'])
    
    # Filter jobs - also track emails within this cycle
    filtered_jobs = []
    emails_in_current_cycle = set()  # Track emails being sent in THIS cycle
    
    for job in jobs:
        job_email_lower = job['email'].lower()
        
        # Skip if already applied (from CSV)
        if job['job_id'] in applied_job_ids:
            continue
        
        # Skip if already contacted (from CSV)
        if job_email_lower in applied_emails:
            continue
        
        # Skip if already added in this cycle (NEW CHECK)
        if job_email_lower in emails_in_current_cycle:
            print(f"⊘ Skipping duplicate email in current cycle: {job['email']} - {job['title'][:40]}...")
            continue
        
        # Add to filtered list and mark email as used in this cycle
        filtered_jobs.append(job)
        emails_in_current_cycle.add(job_email_lower)
    
    print(f"After deduplication: {len(filtered_jobs)} unique applications\n")
    
    total_applied = 0
    
    # ============================================================
    # Send applications (sequential - unavoidable)
    # ============================================================
    print("📧 Sending applications...\n")
    
    for job in filtered_jobs:
        if get_todays_application_count() >= MAX_APPLICATIONS_PER_DAY:
            break
        
        print(f"→ {job['title'][:50]}")
        success = send_application(job['title'], job['company'], job['email'])
        record_application(job['job_id'], job['title'], job['company'], job['email'])
        
        if success:
            total_applied += 1
        
        time.sleep(DELAY_BETWEEN_EMAILS)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"Cycle Complete")
    print(f"{'='*70}")
    print(f"Jobs found: {len(jobs)}")
    print(f"Unique jobs: {len(filtered_jobs)}")
    print(f"Applications sent: {total_applied}")
    print(f"Scraping time: {scrape_time:.1f} seconds")
    print(f"{'='*70}\n")
    
    logging.info(f"Parallel cycle complete: {total_applied} sent in {scrape_time:.1f}s scrape time")

def run_once_parallel():
    """Run once with parallel scraping."""
    print("\n🤖 Running Job Application Bot (PARALLEL MODE)\n")
    process_applications_parallel(max_workers=3)  # 3 parallel threads

def run_scheduled_parallel():
    """Run scheduled with parallel scraping."""
    print("\n🤖 Job Application Bot Started (PARALLEL MODE)")
    print("📅 Schedule: Every 2 hours")
    print("⚙️  Parallel Workers: 3")
    print("⏹ Press Ctrl+C to stop\n")
    
    process_applications_parallel(max_workers=3)
    schedule.every(2).hours.do(process_applications_parallel, max_workers=3)
    
    logging.info("Scheduler started - parallel mode, every 2 hours")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\n⏹ Bot stopped by user")

if __name__ == "__main__":
    # Run once with parallel scraping
    run_once_parallel()
    
    # Or uncomment for scheduled:
    # run_scheduled_parallel()
