import os
import subprocess
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DeploymentManager:
    """
    A class to handle deployment tasks such as setting up the environment, building, and running the application.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env = os.getenv("ENV", "production")

    def check_dependencies(self):
        """
        Ensures that all required dependencies are installed.
        """
        logger.info("Checking system dependencies...")
        dependencies = ["python", "pip", "docker", "docker-compose", "git"]

        for dep in dependencies:
            if not self._command_exists(dep):
                logger.error(f"Dependency '{dep}' is not installed or not in PATH.")
                sys.exit(1)

        logger.info("All required dependencies are installed.")

    def _command_exists(self, command):
        """
        Checks if a command is available in the system PATH.
        
        :param command: Command to check
        :return: True if the command exists, False otherwise
        """
        return subprocess.call(f"type {command}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def setup_virtualenv(self):
        """
        Sets up a Python virtual environment and installs dependencies.
        """
        logger.info("Setting up Python virtual environment...")

        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
            logger.info("Virtual environment created.")

        pip_path = venv_path / "bin" / "pip" if os.name != "nt" else venv_path / "Scripts" / "pip.exe"

        logger.info("Installing Python dependencies...")
        subprocess.check_call([str(pip_path), "install", "-r", str(self.project_root / "requirements.txt")])

        logger.info("Python dependencies installed successfully.")

    def build_docker_images(self):
        """
        Builds Docker images for the application.
        """
        logger.info("Building Docker images...")
        subprocess.check_call(["docker-compose", "build"])
        logger.info("Docker images built successfully.")

    def migrate_database(self):
        """
        Runs database migrations.
        """
        logger.info("Running database migrations...")
        subprocess.check_call(["docker-compose", "run", "web", "flask", "db", "upgrade"])
        logger.info("Database migrations completed.")

    def start_services(self):
        """
        Starts all services using Docker Compose.
        """
        logger.info("Starting all services...")
        subprocess.check_call(["docker-compose", "up", "-d"])
        logger.info("Services started successfully.")

    def run_tests(self):
        """
        Runs automated tests to ensure the application is functioning correctly.
        """
        logger.info("Running automated tests...")
        subprocess.check_call(["docker-compose", "run", "web", "pytest", "--cov=app", "--cov-report=term-missing"])
        logger.info("All tests passed successfully.")

    def deploy(self):
        """
        Executes the full deployment pipeline.
        """
        logger.info("Starting deployment process...")
        self.check_dependencies()
        self.setup_virtualenv()
        self.build_docker_images()
        self.migrate_database()
        self.run_tests()
        self.start_services()
        logger.info("Deployment completed successfully.")

    def monitor_services(self):
        """
        Monitors the health of services and restarts if necessary.
        """
        logger.info("Monitoring services...")
        try:
            subprocess.check_call(["docker", "ps"])
        except subprocess.CalledProcessError:
            logger.error("Some services are not running. Restarting services...")
            self.start_services()
            logger.info("Services restarted successfully.")

    def rollback(self):
        """
        Rolls back the application to the previous stable state.
        """
        logger.warning("Rolling back to the previous stable state...")
        subprocess.check_call(["docker-compose", "down"])
        subprocess.check_call(["docker-compose", "up", "-d", "--no-deps", "web"])
        logger.info("Rollback completed.")

if __name__ == "__main__":
    manager = DeploymentManager()

    actions = {
        "deploy": manager.deploy,
        "monitor": manager.monitor_services,
        "rollback": manager.rollback,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        logger.error(f"Usage: {sys.argv[0]} [deploy|monitor|rollback]")
        sys.exit(1)

    action = sys.argv[1]
    actions[action]()
