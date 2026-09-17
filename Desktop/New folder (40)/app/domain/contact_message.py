from app.extensions import db
from app.utils.datetime_utils import utc_now


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), nullable=False, index=True)
    phone = db.Column(db.String(40), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="new", index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)
    handled_at = db.Column(db.DateTime, nullable=True)

    handled_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    handled_by = db.relationship("User")

    def status_label(self):
        labels = {
            "new": "Новое",
            "in_progress": "В работе",
            "processed": "Обработано",
        }
        return labels.get(self.status, self.status)
