import os
import mimetypes
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# Constants
ALLOWED_FILE_TYPES = {
    "image": ["jpg", "jpeg", "png", "gif"],
    "video": ["mp4", "avi", "mov", "mkv"],
    "text": ["txt", "csv"],
    "json": ["json"],
}
UPLOAD_DIRECTORY = "uploads/"
MAX_FILE_SIZE_MB = 50


class BulkContentUploader:
    """
    Handles bulk content uploads, validation, and processing for multiple content types.
    """

    def __init__(self, upload_dir: str = UPLOAD_DIRECTORY):
        """
        Initialize the uploader with the specified upload directory.
        :param upload_dir: Directory where uploaded files will be stored.
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _validate_file(self, file_path: Path) -> Optional[str]:
        """
        Validates the uploaded file for type and size.
        :param file_path: Path of the file to validate.
        :return: Error message if validation fails; None if validation passes.
        """
        if not file_path.exists():
            return f"File {file_path.name} does not exist."

        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return f"File {file_path.name} exceeds the maximum size of {MAX_FILE_SIZE_MB} MB."

        file_extension = file_path.suffix[1:].lower()
        file_type = mimetypes.guess_type(file_path)[0]
        if not any(file_extension in types for types in ALLOWED_FILE_TYPES.values()):
            return f"File {file_path.name} has an unsupported file type ({file_type})."

        return None

    def upload_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Upload and validate a list of files.
        :param file_paths: List of file paths to upload.
        :return: A dictionary summarizing the upload results.
        """
        results = {"success": [], "errors": []}

        for file_path in file_paths:
            path = Path(file_path)
            validation_error = self._validate_file(path)
            if validation_error:
                results["errors"].append({"file": path.name, "error": validation_error})
                continue

            destination = self.upload_dir / path.name
            try:
                os.rename(path, destination)  # Simulates moving the file to the upload directory
                results["success"].append({"file": path.name, "destination": str(destination)})
            except Exception as e:
                results["errors"].append({"file": path.name, "error": str(e)})

        return results

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Processes a single file based on its type.
        :param file_path: Path to the file.
        :return: A dictionary summarizing the processing results.
        """
        path = Path(file_path)
        file_extension = path.suffix[1:].lower()

        if file_extension in ALLOWED_FILE_TYPES["image"]:
            return self._process_image(path)
        elif file_extension in ALLOWED_FILE_TYPES["video"]:
            return self._process_video(path)
        elif file_extension in ALLOWED_FILE_TYPES["text"]:
            return self._process_text(path)
        elif file_extension in ALLOWED_FILE_TYPES["json"]:
            return self._process_json(path)
        else:
            return {"file": path.name, "status": "Unsupported file type"}

    def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """
        Processes an image file.
        :param file_path: Path to the image file.
        :return: A dictionary summarizing the processing results.
        """
        # Extract metadata (e.g., EXIF) and resize image if necessary
        return {"file": file_path.name, "status": "Processed as image", "metadata": "EXIF data extracted"}

    def _process_video(self, file_path: Path) -> Dict[str, Any]:
        """
        Processes a video file.
        :param file_path: Path to the video file.
        :return: A dictionary summarizing the processing results.
        """
        # Extract video metadata (e.g., resolution, duration)
        return {"file": file_path.name, "status": "Processed as video", "metadata": "Video metadata extracted"}

    def _process_text(self, file_path: Path) -> Dict[str, Any]:
        """
        Processes a text file.
        :param file_path: Path to the text file.
        :return: A dictionary summarizing the processing results.
        """
        with file_path.open("r") as file:
            content = file.read()
        return {"file": file_path.name, "status": "Processed as text", "content": content[:100] + "..."}

    def _process_json(self, file_path: Path) -> Dict[str, Any]:
        """
        Processes a JSON file.
        :param file_path: Path to the JSON file.
        :return: A dictionary summarizing the processing results.
        """
        with file_path.open("r") as file:
            content = json.load(file)
        return {"file": file_path.name, "status": "Processed as JSON", "content": content}


# Example Usage
if __name__ == "__main__":
    uploader = BulkContentUploader()

    # Upload and validate files
    upload_results = uploader.upload_files(["example.jpg", "example.mp4", "example.txt", "example.json"])
    print("Upload Results:", upload_results)

    # Process files
    for file in upload_results["success"]:
        file_path = file["destination"]
        processing_results = uploader.process_file(file_path)
        print("Processing Results:", processing_results)
