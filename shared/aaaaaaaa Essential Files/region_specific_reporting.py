import logging
from datetime import datetime
from typing import List, Dict, Optional
from shared.utils import log_info, log_error, generate_pdf_report, send_email
from shared.config import SUPPORTED_REGIONS, REPORT_TEMPLATES, REGION_CONFIGURATIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/region_specific_reporting.log"),
    ],
)


class RegionSpecificReporting:
    """
    Class to handle generation of region-specific reports for RLG Data and RLG Fans.
    Supports customization and compliance with regional requirements.
    """

    def __init__(self):
        self.supported_regions = SUPPORTED_REGIONS
        self.templates = REPORT_TEMPLATES

    def generate_report(
        self,
        region: str,
        report_type: str,
        data: Dict,
        output_format: str = "PDF",
    ) -> Optional[str]:
        """
        Generate a region-specific report.

        Args:
            region: The region for which the report is being generated.
            report_type: Type of the report (e.g., analytics, compliance).
            data: Data to include in the report.
            output_format: The format of the report (default: PDF).

        Returns:
            The file path of the generated report or None if an error occurs.
        """
        try:
            if region not in self.supported_regions:
                raise ValueError(f"Region '{region}' is not supported.")

            template = self.get_report_template(region, report_type)
            if not template:
                raise ValueError(f"No template found for {report_type} in region {region}.")

            log_info(f"Generating {report_type} report for region {region}.")
            file_path = generate_pdf_report(template, data, output_format)
            log_info(f"Report generated successfully: {file_path}")
            return file_path
        except Exception as e:
            log_error(f"Error generating report for region {region}: {e}")
            return None

    def get_report_template(self, region: str, report_type: str) -> Optional[str]:
        """
        Get the report template for a specific region and report type.

        Args:
            region: The region for the report.
            report_type: The type of report.

        Returns:
            The path to the report template or None if not found.
        """
        try:
            region_config = REGION_CONFIGURATIONS.get(region, {})
            return region_config.get("templates", {}).get(report_type, None)
        except Exception as e:
            log_error(f"Error retrieving template for {report_type} in region {region}: {e}")
            return None

    def send_report(
        self, email: str, file_path: str, subject: str = "Your Region-Specific Report"
    ) -> bool:
        """
        Send the generated report to a specific email.

        Args:
            email: Recipient's email address.
            file_path: Path to the generated report file.
            subject: Email subject (default: "Your Region-Specific Report").

        Returns:
            True if the email is sent successfully, otherwise False.
        """
        try:
            log_info(f"Sending report to {email}.")
            result = send_email(email, subject, "Please find your report attached.", attachments=[file_path])
            if result:
                log_info(f"Report sent successfully to {email}.")
                return True
            else:
                log_error(f"Failed to send report to {email}.")
                return False
        except Exception as e:
            log_error(f"Error sending report to {email}: {e}")
            return False

    def audit_region_reports(self, region: str) -> Dict:
        """
        Audit region-specific reports for accuracy and compliance.

        Args:
            region: The region to audit reports for.

        Returns:
            A dictionary summarizing the audit results.
        """
        try:
            log_info(f"Starting audit for reports in region {region}.")
            if region not in self.supported_regions:
                raise ValueError(f"Region '{region}' is not supported for auditing.")

            # Simulated audit logic
            results = {"region": region, "issues_found": 0, "recommendations": []}
            log_info(f"Audit completed for region {region}. Results: {results}")
            return results
        except Exception as e:
            log_error(f"Error auditing reports for region {region}: {e}")
            return {"error": str(e)}

    def get_supported_regions(self) -> List[str]:
        """
        Get the list of supported regions.

        Returns:
            A list of supported regions.
        """
        try:
            log_info("Fetching supported regions for reporting.")
            return list(self.supported_regions.keys())
        except Exception as e:
            log_error(f"Error fetching supported regions: {e}")
            return []

    def generate_aggregate_report(self, regions: List[str], report_type: str, data: Dict) -> Optional[str]:
        """
        Generate an aggregate report combining data from multiple regions.

        Args:
            regions: List of regions to include in the aggregate report.
            report_type: Type of the report (e.g., analytics, compliance).
            data: Data to include in the report.

        Returns:
            The file path of the aggregate report or None if an error occurs.
        """
        try:
            log_info(f"Generating aggregate {report_type} report for regions: {regions}.")
            aggregated_data = {}
            for region in regions:
                region_data = data.get(region, {})
                aggregated_data[region] = region_data

            file_path = self.generate_report("Aggregate", report_type, aggregated_data)
            log_info(f"Aggregate report generated: {file_path}")
            return file_path
        except Exception as e:
            log_error(f"Error generating aggregate report: {e}")
            return None


# Example Usage
if __name__ == "__main__":
    reporting_service = RegionSpecificReporting()

    # Example data
    example_data = {
        "region": "GDPR",
        "analytics": {"views": 12000, "clicks": 4500},
        "compliance": {"violations": 0, "alerts": 3},
    }

    # Generate a region-specific analytics report
    file_path = reporting_service.generate_report("GDPR", "analytics", example_data)
    if file_path:
        reporting_service.send_report("user@example.com", file_path)

    # Audit reports for a specific region
    audit_results = reporting_service.audit_region_reports("GDPR")
    print(audit_results)

    # Generate an aggregate report for multiple regions
    regions = ["GDPR", "CCPA"]
    aggregate_file_path = reporting_service.generate_aggregate_report(regions, "compliance", example_data)
    print(f"Aggregate report saved at: {aggregate_file_path}")
