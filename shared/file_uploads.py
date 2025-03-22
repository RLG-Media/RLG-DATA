# file_uploads.py

import os
import uuid
from flask import current_app, jsonify
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# Allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'csv', 'xlsx', 'docx'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file: FileStorage, upload_folder: str):
    """
    Saves an uploaded file to the specified folder.
    
    Parameters:
        file (FileStorage): The file to save.
        upload_folder (str): Folder to save the file in.
    
    Returns:
        dict: A dictionary with the filename or error details.
    """
    if file and allowed_file(file.filename):
        try:
            # Ensure upload folder exists
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            # Generate unique filename and save
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            current_app.logger.info(f"File uploaded successfully: {filename}")
            return {"filename": filename, "filepath": filepath}
        
        except Exception as e:
            current_app.logger.error(f"Failed to save file: {e}")
            return {"error": "Failed to save file"}
    
    else:
        current_app.logger.warning("File type is not allowed or file is missing")
        return {"error": "Invalid file type or no file provided"}

def upload_file(file: FileStorage, tool="RLG Data"):
    """
    Handles file upload and storage, returning success or failure messages.
    
    Parameters:
        file (FileStorage): File to upload.
        tool (str): Tool name for logging purposes.
    
    Returns:
        Response: JSON response with success or failure status.
    """
    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    
    result = save_file(file, upload_folder)
    if "filename" in result:
        current_app.logger.info(f"{tool} - File uploaded: {result['filename']}")
        return jsonify({"message": "File uploaded successfully", "filename": result["filename"]}), 201
    
    else:
        current_app.logger.error(f"{tool} - File upload error: {result.get('error')}")
        return jsonify({"error": result.get("error")}), 400
