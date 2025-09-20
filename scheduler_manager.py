# AMAR - AI Med Assistance Robot
# Schedule Management Module (scheduler_manager.py)
# Manages all timed events using APScheduler.

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime

# --- INITIALIZATION ---
scheduler = BackgroundScheduler(timezone="UTC") # Use UTC for consistency

def start_scheduler():
    """Starts the background scheduler."""
    if not scheduler.running:
        scheduler.start()
        logging.info("APScheduler started.")

def stop_scheduler():
    """Stops the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logging.info("APScheduler shut down.")

def add_dispense_job(schedule_id, compartment, pill_name, time_str, callback):
    """
    Adds a new daily dispense job to the scheduler.
    
    :param schedule_id: A unique ID for the job.
    :param compartment: The compartment number (1-7).
    :param pill_name: The name of the medication.
    :param time_str: The time in "HH:MM" format (24-hour).
    :param callback: The function to call when the job triggers.
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        
        # Create a cron trigger to run daily at the specified time
        trigger = CronTrigger(hour=hour, minute=minute, second=0)
        
        scheduler.add_job(
            callback,
            trigger=trigger,
            args=[schedule_id, compartment, pill_name],
            id=str(schedule_id),
            name=f"Dispense '{pill_name}'",
            replace_existing=True # Update the job if an ID already exists
        )
        logging.info(f"Scheduled job '{schedule_id}' for {pill_name} at {time_str} daily.")
        
    except Exception as e:
        logging.error(f"Failed to add schedule job for {pill_name}: {e}")

def remove_job(schedule_id):
    """Removes a job from the scheduler."""
    try:
        scheduler.remove_job(str(schedule_id))
        logging.info(f"Removed job '{schedule_id}' from scheduler.")
    except Exception as e:
        logging.warning(f"Could not remove job '{schedule_id}': {e}")

def get_all_jobs():
    """Returns a list of all currently scheduled jobs."""
    jobs_list = []
    for job in scheduler.get_jobs():
        jobs_list.append({
            'id': job.id,
            'name': job.name,
            'next_run_time': str(job.next_run_time)
        })
    return jobs_list

def get_current_time_str():
    """Returns the current time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
