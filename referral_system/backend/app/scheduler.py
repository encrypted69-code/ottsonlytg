"""
Background scheduled jobs for commission processing
"""
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from .database import SessionLocal
from .services import PaymentService
import logging

logger = logging.getLogger(__name__)

def process_pending_commissions_job():
    """
    Scheduled job to process pending commissions
    Runs every hour to check for commissions past their 24h hold period
    """
    db: Session = SessionLocal()
    try:
        count = PaymentService.process_pending_commissions(db)
        logger.info(f"Processed {count} pending commissions")
    except Exception as e:
        logger.error(f"Error processing pending commissions: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler"""
    scheduler = BackgroundScheduler()
    
    # Process pending commissions every hour
    scheduler.add_job(
        process_pending_commissions_job,
        'interval',
        hours=1,
        id='process_pending_commissions',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Background scheduler started")
    
    return scheduler
