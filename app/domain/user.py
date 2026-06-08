from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(160), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="client")
    company = db.Column(db.String(160), nullable=True)
    phone = db.Column(db.String(40), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requests = db.relationship("ClientRequest", back_populates="client", foreign_keys="ClientRequest.client_id")
    assigned_requests = db.relationship("ClientRequest", back_populates="manager", foreign_keys="ClientRequest.manager_id")
    comments = db.relationship("RequestComment", back_populates="author")
    feedback_items = db.relationship("Feedback", back_populates="author")

    @property
    def is_active(self):
        return self.is_active_user

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return self.role == role_name

    def is_admin(self):
        return self.role == "admin"

    def is_manager(self):
        return self.role == "manager"

    def is_client(self):
        return self.role == "client"
