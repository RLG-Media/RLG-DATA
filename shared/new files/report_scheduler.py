import logging
import schedule
import time
from datetime import datetime
from threading import Thread
from utils import send_email, generate_report
from exceptions import SchedulerError

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ReportScheduler:
    """
    A class to handle scheduling, executing, and managing reports.
    """

    def __init__(self):
        self.jobs = {}
        self.scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def add_job(self, job_id, report_type, schedule_time, email_recipients, **kwargs):
        """
        Adds a new scheduled job.
        Args:
            job_id (str): Unique identifier for the job.
            report_type (str): Type of report to generate.
            schedule_time (str): Schedule time in 'HH:MM' 24-hour format.
            email_recipients (list): List of email recipients.
            kwargs: Additional parameters for report generation.
        """
        if job_id in self.jobs:
            raise SchedulerError(f"Job ID '{job_id}' already exists.")

        def job():
            try:
                logging.info(f"Generating report for job '{job_id}'...")
                report = generate_report(report_type, **kwargs)
                send_email(email_recipients, f"Scheduled Report: {report_type}", report)
                logging.info(f"Report for job '{job_id}' successfully sent to {email_recipients}.")
            except Exception as e:
                logging.error(f"Failed to generate or send report for job '{job_id}': {e}")

        # Schedule the job
        schedule.every().day.at(schedule_time).do(job)
        self.jobs[job_id] = {
            "report_type": report_type,
            "schedule_time": schedule_time,
            "email_recipients": email_recipients,
            "kwargs": kwargs,
        }
        logging.info(f"Scheduled job '{job_id}' for {schedule_time}.")

    def update_job(self, job_id, report_type=None, schedule_time=None, email_recipients=None, **kwargs):
        """
        Updates an existing scheduled job.
        Args:
            job_id (str): Unique identifier for the job.
            report_type (str, optional): Updated type of report.
            schedule_time (str, optional): Updated schedule time.
            email_recipients (list, optional): Updated email recipients.
            kwargs: Additional updated parameters for report generation.
        """
        if job_id not in self.jobs:
            raise SchedulerError(f"Job ID '{job_id}' does not exist.")

        self.remove_job(job_id)  # Remove the old job
        updated_job = self.jobs[job_id]

        # Update job details
        if report_type:
            updated_job["report_type"] = report_type
        if schedule_time:
            updated_job["schedule_time"] = schedule_time
        if email_recipients:
            updated_job["email_recipients"] = email_recipients
        updated_job["kwargs"].update(kwargs)

        # Re-add the job with updated parameters
        self.add_job(
            job_id,
            updated_job["report_type"],
            updated_job["schedule_time"],
            updated_job["email_recipients"],
            **updated_job["kwargs"],
        )
        logging.info(f"Updated job '{job_id}' with new details.")

    def remove_job(self, job_id):
        """
        Removes a scheduled job.
        Args:
            job_id (str): Unique identifier for the job.
        """
        if job_id not in self.jobs:
            raise SchedulerError(f"Job ID '{job_id}' does not exist.")

        # Remove the job from the schedule and job list
        schedule.clear(job_id)
        del self.jobs[job_id]
        logging.info(f"Removed job '{job_id}' from the schedule.")

    def list_jobs(self):
        """
        Lists all scheduled jobs.
        Returns:
            dict: A dictionary of all scheduled jobs.
        """
        logging.info(f"Listing all scheduled jobs: {self.jobs}")
        return self.jobs

    def run_scheduler(self):
        """
        Runs the scheduler in a separate thread to check and execute jobs.
        """
        while True:
            schedule.run_pending()
            time.sleep(1)


# Example usage
if __name__ == "__main__":
    try:
        report_scheduler = ReportScheduler()

        # Add a sample job
        report_scheduler.add_job(
            job_id="daily_sales_report",
            report_type="sales",
            schedule_time="14:00",
            email_recipients=["user@example.com"],
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
        )

        # Update the job
        report_scheduler.update_job(
            job_id="daily_sales_report",
            schedule_time="15:00",
            email_recipients=["updated_user@example.com"],
        )

        # List all jobs
        jobs = report_scheduler.list_jobs()
        print("Scheduled Jobs:", jobs)

        # Keep the script running to execute scheduled jobs
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
