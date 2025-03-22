from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
from typing import Dict, List, Any, Optional
from flask import current_app
from shared.utils import log_error, log_info, validate_api_response  # Shared utilities for logging and response validation
from shared.config import GOOGLE_ANALYTICS_SCOPES  # Shared configuration (e.g., a list of scopes)

# Configure logging (if not already configured)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class GoogleAnalyticsService:
    """
    Service class for interacting with the Google Analytics Reporting API v4 and Management API v3.
    Provides methods to fetch analytics reports, list account summaries, and validate credentials and view IDs.
    Designed for both RLG Data and RLG Fans.
    """

    def __init__(self, credentials_json: str) -> None:
        """
        Initialize the GoogleAnalyticsService with service account credentials.

        Args:
            credentials_json (str): Path to the Google service account JSON credentials file.
        Raises:
            Exception: If initialization fails.
        """
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                credentials_json, scopes=GOOGLE_ANALYTICS_SCOPES
            )
            # Build the Analytics Reporting API client (v4)
            self.analytics = build('analyticsreporting', 'v4', credentials=self.credentials)
            log_info("Google Analytics Reporting API client initialized successfully.")
        except Exception as e:
            log_error(f"Error initializing Google Analytics client: {e}")
            raise

    def get_report(self, view_id: str, start_date: str, end_date: str, metrics: List[str],
                   dimensions: Optional[List[str]] = None, filters: Optional[str] = None,
                   page_token: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch an analytics report for the specified view and date range.

        Args:
            view_id (str): Google Analytics view ID.
            start_date (str): Start date for the report (e.g., '2023-01-01').
            end_date (str): End date for the report (e.g., '2023-12-31').
            metrics (List[str]): List of metric expressions (e.g., ['ga:sessions', 'ga:pageviews']).
            dimensions (Optional[List[str]]): List of dimensions (e.g., ['ga:country', 'ga:browser']).
            filters (Optional[str]): Dimension or metric filters as a string.
            page_token (Optional[str]): Token for paginated results.
            
        Returns:
            Optional[List[Dict[str, Any]]]: Parsed report as a list of dictionaries, or None if an error occurs.
        """
        try:
            log_info(f"Fetching report for view ID: {view_id}, date range: {start_date} to {end_date}")
            request_body = {
                "reportRequests": [{
                    "viewId": view_id,
                    "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                    "metrics": [{"expression": metric} for metric in metrics]
                }]
            }
            if dimensions:
                request_body["reportRequests"][0]["dimensions"] = [{"name": dim} for dim in dimensions]
            if filters:
                request_body["reportRequests"][0]["filtersExpression"] = filters
            if page_token:
                request_body["reportRequests"][0]["pageToken"] = page_token

            response = self.analytics.reports().batchGet(body=request_body).execute()
            if validate_api_response(response):
                log_info(f"Successfully fetched report for view ID: {view_id}")
                return self.parse_report(response)
            else:
                log_error(f"Invalid API response for view ID: {view_id}")
                return {'error': 'Invalid response from Google Analytics API'}
        except HttpError as e:
            log_error(f"Google Analytics API error: {e}")
            return None
        except Exception as e:
            log_error(f"Error fetching report from Google Analytics: {e}")
            return None

    @staticmethod
    def parse_report(report: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Parse the raw Google Analytics report into a structured list of dictionaries.

        Args:
            report (Dict[str, Any]): Raw report data from the API.
            
        Returns:
            Optional[List[Dict[str, Any]]]: Parsed report data, or None if an error occurs.
        """
        try:
            parsed_data = []
            for report_data in report.get("reports", []):
                column_headers = report_data.get("columnHeader", {})
                dimension_headers = column_headers.get("dimensions", [])
                metric_headers = [entry.get("name") for entry in column_headers.get("metricHeader", {}).get("metricHeaderEntries", [])]
                rows = report_data.get("data", {}).get("rows", [])
                for row in rows:
                    row_data = {}
                    dimensions = row.get("dimensions", [])
                    metrics = row.get("metrics", [])[0].get("values", [])
                    for header, value in zip(dimension_headers, dimensions):
                        row_data[header] = value
                    for header, value in zip(metric_headers, metrics):
                        row_data[header] = value
                    parsed_data.append(row_data)
            log_info("Parsed Google Analytics report data successfully.")
            return parsed_data
        except Exception as e:
            log_error(f"Error parsing Google Analytics report: {e}")
            return None

    def list_account_summaries(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch a list of account summaries associated with the credentials.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of account summaries, or None if an error occurs.
        """
        try:
            log_info("Fetching account summaries")
            # Build a management API client for Analytics v3
            management = build('analytics', 'v3', credentials=self.credentials)
            response = management.management().accountSummaries().list().execute()
            if validate_api_response(response):
                log_info("Successfully fetched account summaries")
                return response.get('items', [])
            else:
                log_error("Invalid API response while fetching account summaries")
                return {'error': 'Failed to fetch account summaries'}
        except Exception as e:
            log_error(f"Error fetching account summaries: {e}")
            return None

    def validate_view_id(self, view_id: str) -> bool:
        """
        Validate if a given view ID exists and is accessible.

        Args:
            view_id (str): The view ID to validate.

        Returns:
            bool: True if valid and accessible; False otherwise.
        """
        try:
            log_info(f"Validating view ID: {view_id}")
            # Perform a test report query using a short date range and a basic metric/dimension.
            test_report = self.get_report(view_id, '2023-01-01', '2023-01-02', ['ga:sessions'], ['ga:date'])
            if test_report is not None:
                log_info(f"View ID {view_id} is valid and accessible")
                return True
            else:
                log_error(f"Validation failed for view ID {view_id}: No report data returned")
                return False
        except Exception as e:
            log_error(f"Validation failed for view ID {view_id}: {e}")
            return False

# -------------------------------
# Example Usage (for testing purposes)
# -------------------------------
if __name__ == "__main__":
    # Replace with your actual credentials JSON file path and view ID.
    credentials_path = "path/to/credentials.json"
    view_id = "123456789"
    
    # Initialize the Google Analytics Service
    ga_service = GoogleAnalyticsService(credentials_json=credentials_path)

    # Validate credentials and view ID
    if ga_service.list_account_summaries() is not None:
        print("Account summaries fetched successfully.")
    else:
        print("Failed to fetch account summaries.")

    is_valid_view = ga_service.validate_view_id(view_id=view_id)
    print(f"Is View ID valid? {is_valid_view}")

    # Fetch an analytics report
    report = ga_service.get_report(
        view_id=view_id,
        start_date="2024-01-01",
        end_date="2024-12-31",
        metrics=["ga:sessions", "ga:pageviews"],
        dimensions=["ga:country", "ga:browser"]
    )
    if report:
        print("Analytics Report:")
        for row in report:
            print(row)
    else:
        print("Failed to fetch analytics report.")
