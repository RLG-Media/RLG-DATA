import psutil
import platform
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText

class SystemHealthMonitor:
    """
    Monitors and reports the health of the system, including CPU, memory, disk, and services.
    """

    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None, alert_email: Optional[str] = None):
        """
        Initialize the SystemHealthMonitor.
        Args:
            alert_thresholds (dict, optional): Custom thresholds for alerts (default is preset values).
            alert_email (str, optional): Email address to send alerts.
        """
        self.alert_thresholds = alert_thresholds or {
            "cpu": 90.0,       # CPU usage in percentage
            "memory": 90.0,    # Memory usage in percentage
            "disk": 90.0,      # Disk usage in percentage
        }
        self.alert_email = alert_email
        self.logger = logging.getLogger("SystemHealthMonitor")
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    def get_cpu_usage(self) -> float:
        """Returns the current CPU usage as a percentage."""
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self) -> Dict[str, float]:
        """Returns memory usage details in percentage."""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total / (1024 ** 3),  # Total memory in GB
            "used": memory.used / (1024 ** 3),   # Used memory in GB
            "percent": memory.percent,          # Memory usage percentage
        }

    def get_disk_usage(self, path: str = "/") -> Dict[str, float]:
        """Returns disk usage details for the given path."""
        disk = psutil.disk_usage(path)
        return {
            "total": disk.total / (1024 ** 3),  # Total disk space in GB
            "used": disk.used / (1024 ** 3),   # Used disk space in GB
            "percent": disk.percent,          # Disk usage percentage
        }

    def get_network_io(self) -> Dict[str, float]:
        """Returns network input/output statistics."""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent / (1024 ** 2),    # Bytes sent in MB
            "bytes_recv": net_io.bytes_recv / (1024 ** 2),    # Bytes received in MB
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Returns basic system information."""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "platform_release": platform.release(),
            "architecture": platform.architecture()[0],
            "hostname": platform.node(),
            "processor": platform.processor(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
        }

    def check_service_status(self, service_name: str) -> bool:
        """
        Checks the status of a given service.
        Args:
            service_name (str): Name of the service to check.
        Returns:
            bool: True if the service is running, False otherwise.
        """
        try:
            for service in psutil.win_service_iter():  # Adjust for non-Windows systems if necessary
                if service_name in service.name():
                    return service.status() == "running"
            return False
        except Exception as e:
            self.logger.error(f"Error checking service status for {service_name}: {e}")
            return False

    def send_alert(self, subject: str, message: str) -> None:
        """
        Sends an email alert.
        Args:
            subject (str): Subject of the alert email.
            message (str): Body of the alert email.
        """
        if not self.alert_email:
            self.logger.warning("Alert email is not configured. Skipping email alert.")
            return

        try:
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "your_email@example.com"
            sender_password = "your_password"  # Use a secure method to store this password

            msg = MIMEText(message)
            msg["Subject"] = subject
            msg["From"] = sender_email
            msg["To"] = self.alert_email

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, self.alert_email, msg.as_string())
                self.logger.info("Alert email sent successfully.")
        except Exception as e:
            self.logger.error(f"Failed to send alert email: {e}")

    def monitor(self) -> Dict[str, Any]:
        """Runs the monitoring process and checks thresholds."""
        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_usage": self.get_cpu_usage(),
            "memory_usage": self.get_memory_usage(),
            "disk_usage": self.get_disk_usage(),
            "network_io": self.get_network_io(),
            "system_info": self.get_system_info(),
        }

        # Check thresholds and send alerts if necessary
        self._check_thresholds(health_report)

        self.logger.info(f"Health report: {health_report}")
        return health_report

    def _check_thresholds(self, health_report: Dict[str, Any]) -> None:
        """
        Checks resource usage against thresholds and triggers alerts if necessary.
        Args:
            health_report (dict): The health report data.
        """
        alerts = []

        if health_report["cpu_usage"] > self.alert_thresholds["cpu"]:
            alerts.append(f"High CPU usage detected: {health_report['cpu_usage']}%")

        if health_report["memory_usage"]["percent"] > self.alert_thresholds["memory"]:
            alerts.append(f"High memory usage detected: {health_report['memory_usage']['percent']}%")

        if health_report["disk_usage"]["percent"] > self.alert_thresholds["disk"]:
            alerts.append(f"High disk usage detected: {health_report['disk_usage']['percent']}%")

        if alerts:
            alert_message = "\n".join(alerts)
            self.logger.warning(alert_message)
            self.send_alert("System Health Alert", alert_message)


# Example Usage
if __name__ == "__main__":
    monitor = SystemHealthMonitor(alert_email="admin@example.com")
    monitor.monitor()
