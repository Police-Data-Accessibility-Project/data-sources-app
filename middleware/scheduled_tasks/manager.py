import atexit
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db.client.core import DatabaseClient


class SchedulerManager:

    def __init__(self, app):
        self.scheduler = BackgroundScheduler()
        self.app = app
        self.jobs = {}
        self.dbc = DatabaseClient()

    def add_materialized_view_scheduled_job(self, view_name: str, hour_delay: int):
        current_time = datetime.now()

        def func():
            return self.dbc.refresh_materialized_view(view_name)

        self.add_job(
            job_id=f"refresh_materialized_view_{view_name}",
            func=func,
            interval=IntervalTrigger(
                start_date=current_time + timedelta(hours=hour_delay), hours=24
            ),
        )

    def add_job(self, job_id, func, interval: IntervalTrigger):
        """
        Adds a new job to the scheduler.

        :param job_id: Unique ID for the job.
        :param func: The function to execute.
        :param interval: The interval at which to run the job.
        """
        if job_id in self.jobs:
            print(f"Job {job_id} already exists. Skipping addition.")
            return

        job = self.scheduler.add_job(
            func,
            trigger=interval,
            id=job_id,
            replace_existing=True,
        )
        self.jobs[job_id] = job
        print(
            f"Scheduled job '{job_id}' to run every {interval.interval_length / 60} minutes, starting at {interval.start_date}."
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
