from app.extensions import db
from app.utils.datetime_utils import utc_now


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    created_at = db.Column(db.DateTime, default=utc_now, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    related_request_id = db.Column(db.Integer, db.ForeignKey("client_requests.id"), nullable=True)

    user = db.relationship("User", back_populates="notifications")
    related_request = db.relationship("ClientRequest")
