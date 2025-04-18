from flask import Blueprint, request, jsonify, Response
from io import StringIO
import csv
import json
from shared.error_handling import APIError

# Create a Blueprint for data export functionality
data_export = Blueprint("data_export", __name__)

@data_export.route("/export", methods=["POST"])
def export_data():
    """
    Exports data in the requested format (CSV, JSON, etc.).

    Request Body:
    - data (list): A list of dictionaries representing the data to export.
    - format (str): The desired export format ('csv' or 'json').

    Returns:
    - A file response with the exported data.
    """
    try:
        # Parse request data
        request_data = request.get_json()
        if not request_data:
            raise ValueError("Invalid request: No data provided.")

        data = request_data.get("data")
        export_format = request_data.get("format", "csv").lower()

        if not data or not isinstance(data, list):
            raise ValueError("The 'data' field must be a non-empty list.")

        if export_format not in ["csv", "json"]:
            raise ValueError("The 'format' field must be either 'csv' or 'json'.")

        # Generate export file based on format
        if export_format == "csv":
            return _export_csv(data)
        elif export_format == "json":
            return _export_json(data)

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": "An unexpected error occurred. Please try again later."}), 500


def _export_csv(data):
    """
    Generates a CSV file from the provided data.

    Args:
    - data (list): A list of dictionaries representing the data.

    Returns:
    - A Flask Response containing the CSV file.
    """
    output = StringIO()
    if not data:
        raise ValueError("No data available for export.")

    # Extract headers from the first row
    headers = data[0].keys()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(data)

    output.seek(0)

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=data_export.csv"}
    )


def _export_json(data):
    """
    Generates a JSON file from the provided data.

    Args:
    - data (list): A list of dictionaries representing the data.

    Returns:
    - A Flask Response containing the JSON file.
    """
    json_output = json.dumps(data, indent=4)

    return Response(
        json_output,
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=data_export.json"}
    )


@data_export.route("/available-formats", methods=["GET"])
def available_formats():
    """
    Returns the list of supported export formats.

    Returns:
    - A JSON response with the list of formats.
    """
    try:
        formats = ["csv", "json"]
        return jsonify({"success": True, "formats": formats}), 200
    except Exception as e:
        return jsonify({"success": False, "error": "Unable to fetch available formats."}), 500
