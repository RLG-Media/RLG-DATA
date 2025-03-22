import subprocess
import os
import logging
from datetime import datetime
from .exceptions import DeploymentError
from .config import DEPLOYMENT_BRANCH, DEPLOYMENT_SERVER, SSH_KEY_PATH, PROJECT_DIRECTORY

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for deployment configuration
DEPLOYMENT_SUCCESS = "Deployment successful"
DEPLOYMENT_FAILURE = "Deployment failed"

# Function to execute deployment commands on the remote server
def execute_remote_command(command: str):
    """
    Executes a remote shell command via SSH to the deployment server.
    
    Args:
        command (str): The command to execute remotely.
        
    Returns:
        str: The output from the command execution.
    """
    try:
        # Using subprocess to call SSH with a private key to securely connect and execute commands
        ssh_command = f"ssh -i {SSH_KEY_PATH} user@{DEPLOYMENT_SERVER} '{command}'"
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise DeploymentError(f"Error executing command: {result.stderr}")
        
        logger.info(f"Command executed successfully: {result.stdout}")
        return result.stdout
    
    except Exception as e:
        logger.error(f"Error executing remote command: {str(e)}")
        raise DeploymentError("Deployment failed during command execution.")

# Function to clone or pull the latest code on the deployment server
def update_codebase():
    """
    This function checks if the code is already cloned on the deployment server.
    If it is, it pulls the latest changes from the repository; otherwise, it clones the repository.
    """
    try:
        # Command to check if the project directory exists on the server
        check_directory_command = f"test -d {PROJECT_DIRECTORY}"
        directory_exists = execute_remote_command(check_directory_command)
        
        if directory_exists:
            # If the directory exists, pull the latest changes
            pull_command = f"cd {PROJECT_DIRECTORY} && git pull origin {DEPLOYMENT_BRANCH}"
            execute_remote_command(pull_command)
            logger.info("Codebase updated from remote repository.")
        else:
            # If the directory does not exist, clone the repository
            clone_command = f"git clone -b {DEPLOYMENT_BRANCH} git@github.com:your-organization/your-repo.git {PROJECT_DIRECTORY}"
            execute_remote_command(clone_command)
            logger.info(f"Repository cloned into {PROJECT_DIRECTORY}.")
    
    except Exception as e:
        logger.error(f"Error updating the codebase: {str(e)}")
        raise DeploymentError("Failed to update codebase during deployment.")

# Function to install necessary dependencies on the server
def install_dependencies():
    """
    This function installs the required dependencies for the project on the deployment server.
    """
    try:
        # Command to install dependencies using pip
        install_command = f"cd {PROJECT_DIRECTORY} && pip install -r requirements.txt"
        execute_remote_command(install_command)
        logger.info("Dependencies installed successfully.")
    
    except Exception as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        raise DeploymentError("Failed to install dependencies during deployment.")

# Function to run database migrations
def run_migrations():
    """
    This function runs database migrations on the deployment server.
    """
    try:
        # Command to run migrations (adjust for your project’s migration tool)
        migration_command = f"cd {PROJECT_DIRECTORY} && python manage.py migrate"
        execute_remote_command(migration_command)
        logger.info("Database migrations completed successfully.")
    
    except Exception as e:
        logger.error(f"Error running database migrations: {str(e)}")
        raise DeploymentError("Failed to run database migrations during deployment.")

# Function to restart application services
def restart_services():
    """
    This function restarts the application services on the deployment server.
    """
    try:
        # Command to restart the web server (adjust for your server setup)
        restart_command = f"cd {PROJECT_DIRECTORY} && systemctl restart app.service"
        execute_remote_command(restart_command)
        logger.info("Application services restarted successfully.")
    
    except Exception as e:
        logger.error(f"Error restarting services: {str(e)}")
        raise DeploymentError("Failed to restart services during deployment.")

# Function to verify the deployment
def verify_deployment():
    """
    Verifies if the deployment was successful by checking the application status.
    """
    try:
        # Command to check if the web server is running and application is responsive
        verify_command = f"curl -f http://localhost:8000/health"
        result = execute_remote_command(verify_command)
        
        if "healthy" in result.lower():
            logger.info("Deployment verification successful. Application is healthy.")
        else:
            logger.warning("Deployment verification failed. Application is not healthy.")
            raise DeploymentError("Deployment verification failed.")
    
    except Exception as e:
        logger.error(f"Error verifying deployment: {str(e)}")
        raise DeploymentError("Deployment verification failed.")

# Function to handle the entire deployment process
def deploy():
    """
    Orchestrates the entire deployment process, including:
    1. Updating the codebase
    2. Installing dependencies
    3. Running migrations
    4. Restarting services
    5. Verifying the deployment
    """
    try:
        logger.info(f"Deployment started at {datetime.utcnow()}.")

        # Step 1: Update codebase
        update_codebase()

        # Step 2: Install dependencies
        install_dependencies()

        # Step 3: Run database migrations
        run_migrations()

        # Step 4: Restart services
        restart_services()

        # Step 5: Verify deployment
        verify_deployment()

        logger.info(DEPLOYMENT_SUCCESS)
    
    except DeploymentError as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {str(e)}")
        raise DeploymentError("Unexpected error occurred during deployment.")

# Function to schedule regular automated deployment checks
def schedule_regular_deployments():
    """
    Schedules regular deployment checks using a cron job or task scheduler.
    Ensure that your system's scheduler is set up to call this function at regular intervals.
    """
    try:
        # Example: Adding a cron job to execute deployment every 24 hours
        cron_command = f"0 0 * * * python3 {PROJECT_DIRECTORY}/automated_deployments.py deploy"
        
        # Add cron job to the crontab
        subprocess.run(f'(crontab -l; echo "{cron_command}") | crontab -', shell=True, check=True)
        logger.info("Regular automated deployment scheduled.")
    
    except Exception as e:
        logger.error(f"Error scheduling regular deployments: {str(e)}")
        raise DeploymentError("Failed to schedule regular deployments.")

if __name__ == "__main__":
    deploy()
