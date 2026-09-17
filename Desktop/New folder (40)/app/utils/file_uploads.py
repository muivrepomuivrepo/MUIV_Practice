from pathlib import Path
from uuid import uuid4

from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "xls", "xlsx", "txt"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage, subfolder="requests"):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        extensions = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Недопустимый формат файла. Разрешены: {extensions}.")

    original_name = Path(file_storage.filename).name
    extension = original_name.rsplit(".", 1)[1].lower()
    safe_stem = secure_filename(Path(original_name).stem) or "document"
    unique_filename = f"{uuid4().hex}_{safe_stem}.{extension}"

    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    upload_dir = (upload_root / subfolder).resolve()
    if upload_dir != upload_root and upload_root not in upload_dir.parents:
        raise ValueError("Недопустимый путь для сохранения файла.")
    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = upload_dir / unique_filename
    file_storage.save(target_path)

    size_bytes = target_path.stat().st_size
    if size_bytes == 0:
        target_path.unlink(missing_ok=True)
        raise ValueError("Нельзя загрузить пустой файл.")

    return {
        "original_name": original_name,
        "stored_name": target_path.relative_to(upload_root).as_posix(),
        "mime_type": file_storage.mimetype or "application/octet-stream",
        "size_bytes": size_bytes,
    }


def resolve_uploaded_file(stored_name):
    upload_root = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    target_path = (upload_root / stored_name).resolve()
    if target_path == upload_root or upload_root not in target_path.parents:
        raise ValueError("Недопустимый путь к файлу.")
    return target_path


def remove_uploaded_file(stored_name):
    target_path = resolve_uploaded_file(stored_name)
    target_path.unlink(missing_ok=True)
