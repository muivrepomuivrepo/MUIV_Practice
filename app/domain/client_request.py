from datetime import datetime

from app.extensions import db


class ClientRequest(db.Model):
    __tablename__ = "client_requests"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(220), nullable=False)
    description = db.Column(db.Text, nullable=False)
    object_address = db.Column(db.String(260), nullable=True)
    priority = db.Column(db.String(40), nullable=False, default="medium")
    status = db.Column(db.String(60), nullable=False, default="new")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)

    client = db.relationship("User", back_populates="requests", foreign_keys=[client_id])
    manager = db.relationship("User", back_populates="assigned_requests", foreign_keys=[manager_id])
    service = db.relationship("Service", back_populates="requests")
    comments = db.relationship("RequestComment", back_populates="request", cascade="all, delete-orphan")
    feedback_items = db.relationship("Feedback", back_populates="request", cascade="all, delete-orphan")

    def status_label(self):
        labels = {
            "new": "Новая",
            "in_progress": "В работе",
            "waiting_client": "Ожидает клиента",
            "completed": "Завершена",
            "cancelled": "Отменена",
        }
        return labels.get(self.status, self.status)

    def priority_label(self):
        labels = {
            "low": "Низкий",
            "medium": "Средний",
            "high": "Высокий",
            "urgent": "Срочный",
        }
        return labels.get(self.priority, self.priority)
