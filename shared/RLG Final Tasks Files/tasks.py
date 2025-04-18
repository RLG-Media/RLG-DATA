from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

# Create Celery instance and configure it
app = Celery('tasks', broker='pyamqp://guest@localhost//')

# Set the logger
logger = get_task_logger(__name__)

# Celery configuration
app.conf.update(
    result_backend='redis://localhost:6379/0',
    timezone='UTC',
    task_serializer='json',
    accept_content=['json'],
    enable_utc=True,
    task_routes={
        'tasks.*': 'queue.general',
    },
    task_default_queue='default',
    task_queues=[
        {
            'name': 'default',
            'routing_key': 'queue.general',
        },
        {
            'name': 'high_priority',
            'routing_key': 'queue.high_priority',
        },
    ],
    task_default_exchange='celery',
    task_default_exchange_type='direct',
    task_default_routing_key='task.default',
    task_default_exchange='default'
)

@app.task
def process_data(data):
    """
    Task to process data
    :param data: Data object to be processed
    """
    logger.info(f"Processing data: {data}")
    # Process the data here
    processed_data = data  # Replace with actual processing logic
    return processed_data

@app.task
def archive_data(data):
    """
    Task to archive data
    :param data: Data object to be archived
    """
    logger.info(f"Archiving data: {data}")
    # Archiving logic goes here
    archived_result = data  # Replace with actual archiving logic
    return archived_result

@app.task
def send_notification(user_id, message):
    """
    Task to send notifications
    :param user_id: ID of the user to notify
    :param message: Notification message
    """
    logger.info(f"Sending notification to user {user_id} with message: {message}")
    # Send notification logic here
    notification_result = f"Notification sent to {user_id}"  # Replace with actual notification sending logic
    return notification_result

@app.task
def clean_temp_files():
    """
    Task to clean temporary files
    """
    logger.info("Cleaning temporary files")
    # Logic to clean temp files goes here
    cleaned_files = True  # Replace with actual cleaning logic
    return cleaned_files

@app.task
def fetch_fan_data(fan_id):
    """
    Task to fetch fan data
    :param fan_id: ID of the fan whose data needs to be fetched
    """
    logger.info(f"Fetching data for fan ID: {fan_id}")
    # Logic to fetch fan data goes here
    fan_data = {"fan_id": fan_id, "data": "fan_data"}  # Replace with actual data fetching logic
    return fan_data

@app.task
def send_fan_update(fan_id, update_message):
    """
    Task to send updates to fans
    :param fan_id: ID of the fan to receive updates
    :param update_message: Message to send to the fan
    """
    logger.info(f"Sending update to fan ID: {fan_id} with message: {update_message}")
    # Logic to send updates goes here
    update_result = f"Update sent to fan {fan_id}"  # Replace with actual update sending logic
    return update_result

# Celery periodic tasks configuration (For scheduled tasks)
app.conf.beat_schedule = {
    'data-processing': {
        'task': 'tasks.process_data',
        'schedule': crontab(hour=0, minute=0),
    },
    'data-archiving': {
        'task': 'tasks.archive_data',
        'schedule': crontab(hour=1, minute=0),
    },
    'notification-sending': {
        'task': 'tasks.send_notification',
        'schedule': crontab(hour=9, minute=0),
    },
    'clean-temp-files': {
        'task': 'tasks.clean_temp_files',
        'schedule': crontab(hour=3, minute=0),
    },
    'fetch-fan-data': {
        'task': 'tasks.fetch_fan_data',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'send-fan-updates': {
        'task': 'tasks.send_fan_update',
        'schedule': crontab(hour=18, minute=0),
    },
}

# Logging configuration for Celery
app.conf.task_logger_format = '[%(asctime)s: %(levelname)s/%(processName)s] %(message)s'
