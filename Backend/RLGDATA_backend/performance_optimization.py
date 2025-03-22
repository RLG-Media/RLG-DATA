import time
import redis
from sqlalchemy import func, select
from app import db
from models import Project, SocialMediaData
from concurrent.futures import ThreadPoolExecutor
from cache import cache_result, invalidate_cache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Redis connection for caching
cache = redis.StrictRedis(host='localhost', port=6379, db=0)


### DATABASE PERFORMANCE OPTIMIZATION ###

def optimize_database_queries():
    """
    Optimize database queries by adding indexes and using efficient query patterns.
    """
    try:
        # Adding an index to the 'project_id' column in the SocialMediaData table for faster lookups
        db.session.execute("CREATE INDEX IF NOT EXISTS idx_project_id ON social_media_data (project_id)")
        db.session.commit()
        logging.info("Added index on 'project_id' in SocialMediaData table.")

        # Adding index on 'created_at' column for better query performance on time-based searches
        db.session.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON social_media_data (created_at)")
        db.session.commit()
        logging.info("Added index on 'created_at' in SocialMediaData table.")

    except Exception as e:
        logging.error(f"Error optimizing database queries: {e}")


def get_project_data_optimized(project_id):
    """
    Optimized query to fetch project-related data.
    
    :param project_id: ID of the project to fetch data for
    :return: List of social media data records related to the project
    """
    try:
        # Avoid N+1 problem by preloading related data
        project_data = db.session.query(SocialMediaData).filter_by(project_id=project_id).all()
        logging.info(f"Fetched {len(project_data)} records for project ID {project_id}")
        return project_data

    except Exception as e:
        logging.error(f"Error fetching project data for {project_id}: {e}")
        return []


### API RATE LIMITING AND THROTTLING ###

def throttle_api_requests(api_func, max_calls_per_minute=60):
    """
    Throttle API requests to avoid hitting rate limits.
    
    :param api_func: The API function to be throttled
    :param max_calls_per_minute: Maximum API calls allowed per minute
    :return: Wrapped function that respects rate limits
    """
    call_interval = 60.0 / max_calls_per_minute
    last_call_time = [0]  # Use list to maintain state in nested function

    def wrapped_func(*args, **kwargs):
        time_since_last_call = time.time() - last_call_time[0]
        if time_since_last_call < call_interval:
            time.sleep(call_interval - time_since_last_call)
        last_call_time[0] = time.time()
        return api_func(*args, **kwargs)

    return wrapped_func


@throttle_api_requests
def fetch_optimized_twitter_data(keyword):
    """
    Optimized API call to fetch data from Twitter with rate limiting.
    
    :param keyword: The keyword to search for
    :return: List of Twitter data (if available)
    """
    # Use API integration here (fetch_twitter_data), but respect rate limits
    return fetch_twitter_data(keyword)


### CACHING STRATEGIES ###

@cache_result(timeout=300)  # Cache results for 5 minutes
def get_cached_project_data(project_id):
    """
    Fetch project data and cache it for improved performance.
    
    :param project_id: ID of the project to fetch data for
    :return: List of cached social media data records
    """
    logging.info(f"Fetching and caching data for project ID {project_id}")
    return get_project_data_optimized(project_id)


def invalidate_project_cache(project_id):
    """
    Invalidate the cache for a specific project's data.
    
    :param project_id: ID of the project to invalidate cache for
    """
    logging.info(f"Invalidating cache for project ID {project_id}")
    invalidate_cache('get_cached_project_data', project_id)


### CONCURRENT TASK EXECUTION ###

def run_concurrent_scraping_tasks(keywords):
    """
    Run multiple scraping tasks concurrently to improve performance.
    
    :param keywords: List of keywords to scrape
    :return: List of results from all scraping tasks
    """
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_optimized_twitter_data, keyword) for keyword in keywords]
        for future in futures:
            try:
                result = future.result()
                results.append(result)
                logging.info(f"Scraping completed for keyword: {keyword}")
            except Exception as e:
                logging.error(f"Error scraping data for keyword: {keyword} - {e}")
    return results


### GENERAL PERFORMANCE TIPS ###

def measure_execution_time(func):
    """
    Decorator to measure the execution time of a function.
    
    :param func: The function whose execution time will be measured
    :return: Wrapped function with timing logic
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.info(f"Execution time for {func.__name__}: {end_time - start_time:.2f} seconds")
        return result

    return wrapper


@measure_execution_time
def generate_report(project_id):
    """
    Generate a report for a project, optimizing performance by preloading data.
    
    :param project_id: ID of the project to generate the report for
    :return: Report data
    """
    # Fetch cached project data for faster access
    project_data = get_cached_project_data(project_id)
    # Generate the report from the fetched data (implement report generation logic)
    return f"Report for project {project_id} generated with {len(project_data)} records"


