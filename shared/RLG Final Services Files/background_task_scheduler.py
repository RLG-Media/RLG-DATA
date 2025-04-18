import time
import threading
import schedule
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class BackgroundTaskScheduler:
    def __init__(self, max_workers=5):
        """
        Initialize the background task scheduler.
        
        Args:
            max_workers (int): Maximum number of concurrent tasks.
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = []
        self.stop_event = threading.Event()
    
    def add_task(self, func, interval, unit='seconds', *args, **kwargs):
        """
        Schedule a background task.
        
        Args:
            func (callable): Function to be executed.
            interval (int): Time interval for execution.
            unit (str): Time unit ('seconds', 'minutes', 'hours', 'days').
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.
        """
        scheduler_func = getattr(schedule.every(interval), unit)
        scheduler_func.do(self._run_task, func, *args, **kwargs)
        self.tasks.append((func.__name__, interval, unit))
        print(f"Scheduled task: {func.__name__} every {interval} {unit}")
    
    def _run_task(self, func, *args, **kwargs):
        """Execute a task asynchronously."""
        self.executor.submit(func, *args, **kwargs)
    
    def start(self):
        """Start the background scheduler loop."""
        print("Starting Background Task Scheduler...")
        while not self.stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """Stop the background scheduler."""
        self.stop_event.set()
        self.executor.shutdown(wait=False)
        print("Background Task Scheduler stopped.")

# Example tasks
def fetch_social_media_data():
    print(f"[INFO] Fetching social media data at {datetime.now()}...")

def process_analytics():
    print(f"[INFO] Processing analytics at {datetime.now()}...")

if __name__ == "__main__":
    scheduler = BackgroundTaskScheduler()
    scheduler.add_task(fetch_social_media_data, interval=5, unit='seconds')
    scheduler.add_task(process_analytics, interval=1, unit='minutes')
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.stop()
