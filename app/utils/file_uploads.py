from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "xls", "xlsx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage, subfolder="requests"):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None
    filename = secure_filename(file_storage.filename)
    unique_filename = f"{uuid4().hex}_{filename}"
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = upload_dir / unique_filename
    file_storage.save(target_path)
    return str(target_path)
