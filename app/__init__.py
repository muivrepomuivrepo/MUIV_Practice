from pathlib import Path

from flask import Flask

from config import Config
from app.extensions import db, login_manager
from app.database.seed_data import seed_database
from app.domain.user import User


def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).resolve().parent.parent / "templates"),
        static_folder=str(Path(__file__).resolve().parent.parent / "static"),
    )
    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["MODEL_DIR"]).mkdir(parents=True, exist_ok=True)
    (Path(app.config["UPLOAD_FOLDER"]) / "requests").mkdir(parents=True, exist_ok=True)
    (Path(app.config["UPLOAD_FOLDER"]) / "documents").mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    register_blueprints(app)

    with app.app_context():
        db.create_all()
        seed_database()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def register_blueprints(app):
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.client import client_bp
    from app.routes.manager import manager_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(manager_bp, url_prefix="/manager")
    app.register_blueprint(admin_bp, url_prefix="/admin")
