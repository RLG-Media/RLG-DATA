import logging
from datetime import datetime

# Configure the logger
LOG_FILE = "auth_logs.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def log_auth_event(user_id: str, event: str, ip_address: str = "Unknown", status: str = "Success"):
    """
    Log an authentication event.
    
    Args:
        user_id (str): The ID of the user involved in the event.
        event (str): The type of authentication event (e.g., "Login", "Logout", "Password Change").
        ip_address (str): The IP address of the user. Default is "Unknown".
        status (str): The status of the event (e.g., "Success", "Failure"). Default is "Success".
    """
    log_message = (
        f"User ID: {user_id} | Event: {event} | IP Address: {ip_address} | Status: {status}"
    )
    if status.lower() == "failure":
        logging.warning(log_message)
    else:
        logging.info(log_message)

def read_auth_logs(start_date: str = None, end_date: str = None):
    """
    Read authentication logs filtered by date range.
    
    Args:
        start_date (str): Start date in the format 'YYYY-MM-DD'. Optional.
        end_date (str): End date in the format 'YYYY-MM-DD'. Optional.
    
    Returns:
        list: A list of log entries within the specified date range.
    """
    logs = []
    try:
        with open(LOG_FILE, "r") as log_file:
            for line in log_file:
                log_date_str = line.split(" - ")[0]
                log_date = datetime.strptime(log_date_str, "%Y-%m-%d %H:%M:%S")
                if start_date:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    if log_date < start_date_obj:
                        continue
                if end_date:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                    if log_date > end_date_obj:
                        continue
                logs.append(line.strip())
    except FileNotFoundError:
        logs.append("No logs found.")
    except Exception as e:
        logs.append(f"Error reading logs: {str(e)}")
    return logs

# Example usage
if __name__ == "__main__":
    # Example log events
    log_auth_event("user123", "Login", "192.168.1.100")
    log_auth_event("user456", "Login", "203.0.113.1", "Failure")
    log_auth_event("user123", "Password Change", "192.168.1.100")
    
    # Read logs for today
    today = datetime.now().strftime("%Y-%m-%d")
    print("\n".join(read_auth_logs(start_date=today)))
