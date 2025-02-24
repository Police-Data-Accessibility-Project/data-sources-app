import atexit
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


class SchedulerManager:

    def __init__(self, app):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.jobs = {}

    def add_job(self, job_id, func, minutes=10, delay_minutes=0):
        """
        Adds a new job to the scheduler.

        :param job_id: Unique ID for the job.
        :param func: The function to execute.
        :param minutes: The interval (in minutes) at which the job runs.
        """
        if job_id in self.jobs:
            print(f"Job {job_id} already exists. Skipping addition.")
            return

        start_time = datetime.now() + timedelta(minutes=delay_minutes)

        job = self.scheduler.add_job(
            func,
            trigger=IntervalTrigger(start_date=start_time, minutes=minutes),
            id=job_id,
            replace_existing=True,
        )
        self.jobs[job_id] = job
        print(
            f"Scheduled job '{job_id}' to run every {minutes} minutes, starting at {start_time}."
        )

    def start(self):
        """
        Starts the scheduler.
        """
        self.scheduler.start()
        atexit.register(lambda: self.shutdown())

    def shutdown(self):
        """
        Shuts down the scheduler gracefully.
        """
        self.scheduler.shutdown()
        print("Scheduler shut down.")
