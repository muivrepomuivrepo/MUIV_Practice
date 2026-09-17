from app.extensions import db
from app.utils.datetime_utils import utc_now


class Attachment(db.Model):
    __tablename__ = "attachments"

    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(500), unique=True, nullable=False)
    mime_type = db.Column(db.String(160), nullable=True)
    size_bytes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    request_id = db.Column(db.Integer, db.ForeignKey("client_requests.id"), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    request = db.relationship("ClientRequest", back_populates="attachments")
    uploader = db.relationship("User")

    def size_label(self):
        if self.size_bytes < 1024:
            return f"{self.size_bytes} Б"
        if self.size_bytes < 1024 * 1024:
            return f"{self.size_bytes / 1024:.1f} КБ"
        return f"{self.size_bytes / (1024 * 1024):.1f} МБ"
