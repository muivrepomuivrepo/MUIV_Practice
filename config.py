from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = "replace-this-development-key"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'instance' / 'irbis_app.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    MODEL_DIR = BASE_DIR / "models"
    COMPANY_NAME = "ООО «ГК «ИРБИС»»"
    APP_TITLE = "IRBIS Client Service"
