"""
APScheduler Jobs — Runs background tasks.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

def run_automated_scan(app):
    """
    Run the ScannerService across all assets.
    Requires the Flask app instance to create an app context for DB operations.
    """
    logger.info("Running automated background scan...")
    with app.app_context():
        from app.services.scanner import ScannerService
        try:
            results = ScannerService.scan_all_assets()
            logger.info(f"Automated scan completed: {results}")
        except Exception as e:
            logger.error(f"Automated scan failed: {e}")

def init_scheduler(app):
    """Initialize and start the background scheduler."""
    scheduler = BackgroundScheduler()
    
    interval_hours = app.config.get("SCAN_INTERVAL_HOURS", 24)
    
    # Schedule the scan job
    scheduler.add_job(
        func=run_automated_scan,
        trigger=IntervalTrigger(hours=interval_hours),
        args=[app],
        id="automated_discovery_scan",
        name="Run Discovery Engine across all protected assets",
        replace_existing=True
    )
    
    scheduler.start()
    logger.info(f"APScheduler started. Scan job configured to run every {interval_hours} hours.")
    
    # Shut down scheduler gracefully when Flask stops
    import atexit
    atexit.register(lambda: scheduler.shutdown(wait=False))
