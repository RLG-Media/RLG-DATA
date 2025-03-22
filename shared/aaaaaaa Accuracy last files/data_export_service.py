"""
data_export_service.py
Handles the exporting of data for RLG Data and RLG Fans in multiple formats.
Provides customizable and automated export processes for reports, raw data, and analytics.
"""

import os
import csv
import json
import logging
from typing import List, Dict, Union
from pathlib import Path
from datetime import datetime

# Load environment variables and configurations
from config import ActiveConfig

# Logger setup
logger = logging.getLogger(__name__)

# Base export directory
EXPORT_DIR = Path(ActiveConfig.EXPORT_STORAGE_DIR)
SUPPORTED_FORMATS = ["csv", "json", "xlsx"]


class DataExportService:
    """
    Manages data export processes for RLG Data and RLG Fans.
    """

    def __init__(self, export_dir: Path = EXPORT_DIR):
        self.export_dir = export_dir
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """
        Ensures the export directory exists.
        """
        self.export_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Export directory ensured: {self.export_dir}")

    def export_data(
        self,
        data: List[Dict[str, Union[str, int, float, bool]]],
        filename: str,
        format: str = "csv",
        metadata: Dict[str, Union[str, int]] = None,
    ) -> Path:
        """
        Exports data in the specified format.

        Args:
            data (List[Dict[str, Union[str, int, float, bool]]]): Data to export.
            filename (str): Base name for the export file (without extension).
            format (str): Format to export the data in (csv, json, xlsx).
            metadata (Dict[str, Union[str, int]], optional): Additional metadata to include in exports.

        Returns:
            Path: Path to the exported file.
        """
        if format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Supported formats: {SUPPORTED_FORMATS}")

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        file_path = self.export_dir / f"{filename}_{timestamp}.{format}"

        logger.info(f"Exporting data to {file_path} in {format} format.")

        if format == "csv":
            self._export_to_csv(data, file_path, metadata)
        elif format == "json":
            self._export_to_json(data, file_path, metadata)
        elif format == "xlsx":
            self._export_to_xlsx(data, file_path, metadata)

        logger.info(f"Data export completed: {file_path}")
        return file_path

    def _export_to_csv(self, data: List[Dict[str, Union[str, int, float, bool]]], file_path: Path, metadata: Dict[str, Union[str, int]]):
        """
        Exports data to a CSV file.

        Args:
            data (List[Dict[str, Union[str, int, float, bool]]]): Data to export.
            file_path (Path): Path to the CSV file.
            metadata (Dict[str, Union[str, int]]): Additional metadata to include in the CSV file.
        """
        with file_path.open(mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
            writer.writeheader()

            # Write metadata if provided
            if metadata:
                writer.writerow({key: f"Metadata: {value}" for key, value in metadata.items()})

            writer.writerows(data)
        logger.debug(f"Exported data to CSV: {file_path}")

    def _export_to_json(self, data: List[Dict[str, Union[str, int, float, bool]]], file_path: Path, metadata: Dict[str, Union[str, int]]):
        """
        Exports data to a JSON file.

        Args:
            data (List[Dict[str, Union[str, int, float, bool]]]): Data to export.
            file_path (Path): Path to the JSON file.
            metadata (Dict[str, Union[str, int]]): Additional metadata to include in the JSON file.
        """
        with file_path.open(mode="w", encoding="utf-8") as jsonfile:
            output = {"data": data, "metadata": metadata} if metadata else {"data": data}
            json.dump(output, jsonfile, indent=4)
        logger.debug(f"Exported data to JSON: {file_path}")

    def _export_to_xlsx(self, data: List[Dict[str, Union[str, int, float, bool]]], file_path: Path, metadata: Dict[str, Union[str, int]]):
        """
        Exports data to an XLSX file.

        Args:
            data (List[Dict[str, Union[str, int, float, bool]]]): Data to export.
            file_path (Path): Path to the XLSX file.
            metadata (Dict[str, Union[str, int]]): Additional metadata to include in the XLSX file.
        """
        try:
            import openpyxl
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Data"

            # Write metadata if provided
            if metadata:
                for key, value in metadata.items():
                    sheet.append([f"Metadata: {key}", value])
                sheet.append([])  # Add a blank row

            # Write data
            sheet.append(data[0].keys())  # Write headers
            for row in data:
                sheet.append(row.values())

            workbook.save(file_path)
            logger.debug(f"Exported data to XLSX: {file_path}")
        except ImportError:
            logger.error("openpyxl is required for exporting to XLSX format.")
            raise

    def cleanup_old_exports(self, retention_days: int = 30):
        """
        Deletes exported files older than the retention period.

        Args:
            retention_days (int): Number of days to retain export files.
        """
        logger.info("Starting cleanup of old exports.")
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        for export_file in self.export_dir.glob("*"):
            if export_file.is_file() and self._get_file_modification_time(export_file) < cutoff_date:
                logger.info(f"Deleting old export: {export_file}")
                export_file.unlink()

        logger.info("Cleanup of old exports completed.")

    @staticmethod
    def _get_file_modification_time(file_path: Path) -> datetime:
        """
        Retrieves the last modification time of a file.

        Args:
            file_path (Path): File path.

        Returns:
            datetime: Modification time of the file.
        """
        return datetime.utcfromtimestamp(file_path.stat().st_mtime)


# Entry point for scheduled exports
def export_service():
    """
    Handles scheduled data exports for RLG Data and RLG Fans.
    """
    exporter = DataExportService()
    data_sources = {
        "rlg_data": [{"id": 1, "name": "Sample RLG Data", "value": 100}],
        "rlg_fans": [{"id": 1, "name": "Sample RLG Fan Data", "value": 200}],
    }

    for name, data in data_sources.items():
        exporter.export_data(data, filename=name, format="csv", metadata={"source": name, "generated_by": "RLG System"})

    logger.info("Scheduled data export service completed successfully.")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run export service
    try:
        export_service()
    except Exception as e:
        logger.exception(f"An error occurred during data export: {e}")
