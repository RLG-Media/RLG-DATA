import logging
from typing import Dict, List, Union
from datetime import datetime
import pdfkit
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("custom_reporting_services.log"),
        logging.StreamHandler()
    ]
)

class CustomReportingService:
    """
    Service class for generating custom reports for RLG Data and RLG Fans.
    Supports generating reports in multiple formats (PDF, JSON, CSV).
    """

    def __init__(self, report_dir: str = "reports"):
        """
        Initialize the CustomReportingService.

        Args:
            report_dir: Directory to save generated reports.
        """
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        logging.info("CustomReportingService initialized with report directory: %s", self.report_dir)

    def generate_pdf_report(self, data: Dict, report_name: str) -> str:
        """
        Generate a PDF report.

        Args:
            data: The data to include in the report.
            report_name: The name of the report file (without extension).

        Returns:
            Path to the generated PDF report.
        """
        html_content = self._generate_html_content(data)
        report_path = os.path.join(self.report_dir, f"{report_name}.pdf")

        try:
            pdfkit.from_string(html_content, report_path)
            logging.info("PDF report generated: %s", report_path)
            return report_path
        except Exception as e:
            logging.error("Failed to generate PDF report: %s", e)
            raise

    def generate_json_report(self, data: Dict, report_name: str) -> str:
        """
        Generate a JSON report.

        Args:
            data: The data to include in the report.
            report_name: The name of the report file (without extension).

        Returns:
            Path to the generated JSON report.
        """
        report_path = os.path.join(self.report_dir, f"{report_name}.json")

        try:
            with open(report_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            logging.info("JSON report generated: %s", report_path)
            return report_path
        except Exception as e:
            logging.error("Failed to generate JSON report: %s", e)
            raise

    def generate_csv_report(self, data: List[Dict], report_name: str) -> str:
        """
        Generate a CSV report.

        Args:
            data: A list of dictionaries representing rows of the report.
            report_name: The name of the report file (without extension).

        Returns:
            Path to the generated CSV report.
        """
        import csv

        report_path = os.path.join(self.report_dir, f"{report_name}.csv")

        try:
            with open(report_path, "w", newline="") as csv_file:
                if len(data) > 0:
                    writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                logging.info("CSV report generated: %s", report_path)
            return report_path
        except Exception as e:
            logging.error("Failed to generate CSV report: %s", e)
            raise

    def _generate_html_content(self, data: Dict) -> str:
        """
        Generate HTML content for PDF reports.

        Args:
            data: The data to include in the report.

        Returns:
            A string containing HTML content.
        """
        html = """<html>
        <head><title>Custom Report</title></head>
        <body>
        <h1>Custom Report</h1>
        <p>Generated on: {}</p>
        <table border="1" cellspacing="0" cellpadding="5">
        <tr>
        {} <!-- Table Headers -->
        </tr>
        {} <!-- Table Rows -->
        </table>
        </body>
        </html>"""

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not isinstance(data, list):
            data = [data]

        headers = "".join([f"<th>{key}</th>" for key in data[0].keys()])
        rows = "".join([
            "<tr>" + "".join([f"<td>{value}</td>" for value in row.values()]) + "</tr>"
            for row in data
        ])
        return html.format(timestamp, headers, rows)

# Example usage
if __name__ == "__main__":
    service = CustomReportingService()

    # Example data
    data = [
        {"Name": "John Doe", "Age": 29, "Occupation": "Engineer"},
        {"Name": "Jane Smith", "Age": 34, "Occupation": "Designer"}
    ]

    # Generate PDF report
    pdf_path = service.generate_pdf_report(data, "example_report")
    print(f"PDF Report generated at: {pdf_path}")

    # Generate JSON report
    json_path = service.generate_json_report(data, "example_report")
    print(f"JSON Report generated at: {json_path}")

    # Generate CSV report
    csv_path = service.generate_csv_report(data, "example_report")
    print(f"CSV Report generated at: {csv_path}")
