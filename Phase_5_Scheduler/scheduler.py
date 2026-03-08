"""
Phase 5 Scheduler: runs ingest/rebuild and reloads FAISS so Backend API chat/query
uses fresh data; frontend chat UI continues to show citations and error handling.
"""
import os
import time
import subprocess
import sys
from apscheduler.schedulers.background import BackgroundScheduler

# Resolve base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_ingestion(reload_callback=None):
    """
    Triggers the full data update pipeline:
    1. Phase 1: Scraper
    2. Phase 2: Processor (Structured Data)
    3. Phase 2: Vector DB Builder (FAISS)
    """
    print(f"\n[{time.ctime()}] Starting scheduled data update pipeline...")
    
    try:
        # 1. Run Scraper
        scraper_path = os.path.join(BASE_DIR, "Phase_1_Data_Ingestion", "scraper.py")
        print(f"--- Step 1: Running Scraper ({scraper_path}) ---")
        subprocess.run([sys.executable, scraper_path], check=True, cwd=os.path.dirname(scraper_path))
        
        # 2. Run Processor
        processor_path = os.path.join(BASE_DIR, "Phase_2_Knowledge_Base", "processor.py")
        print(f"--- Step 2: Running Processor ({processor_path}) ---")
        subprocess.run([sys.executable, processor_path], check=True, cwd=os.path.dirname(processor_path))
        
        # 3. Run Vector DB Builder
        builder_path = os.path.join(BASE_DIR, "Phase_2_Knowledge_Base", "build_faiss_db.py")
        print(f"--- Step 3: Building FAISS Index ({builder_path}) ---")
        subprocess.run([sys.executable, builder_path], check=True, cwd=os.path.dirname(builder_path))
        
        print(f"[{time.ctime()}] Data update pipeline completed successfully.")
        
        # 4. Trigger Reload across the API
        if reload_callback:
            print("--- Step 4: Triggering Index Reload in Backend ---")
            success = reload_callback()
            if success:
                print("Backend index reloaded successfully.")
            else:
                print("Backend index reload failed.")
        
    except subprocess.CalledProcessError as e:
        print(f"Pipeline failed at step: {e.cmd}")
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error during scheduled update: {e}")

def start_scheduler(reload_callback=None):
    """
    Initializes and starts the APScheduler.
    """
    scheduler = BackgroundScheduler()
    
    # Schedule to run every 24 hours. 
    # For testing purposes, you can change 'hours=24' to 'minutes=1'
    scheduler.add_job(
        run_ingestion, 
        'interval', 
        hours=24, 
        args=[reload_callback],
        id='mutual_fund_update_job',
        replace_existing=True
    )
    
    scheduler.start()
    print("Scheduler started. Mutual Fund data update job scheduled every 24 hours.")
    return scheduler

if __name__ == "__main__":
    # If run directly, start the scheduler and keep it alive
    print("Manual Scheduler Start (Phase 5)...")
    # For manual testing, we trigger it once immediately
    run_ingestion()
    
    scheduler = start_scheduler()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")
