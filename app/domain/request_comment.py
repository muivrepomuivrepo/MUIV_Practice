from datetime import datetime

from app.extensions import db


class RequestComment(db.Model):
    __tablename__ = "request_comments"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    request_id = db.Column(db.Integer, db.ForeignKey("client_requests.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    request = db.relationship("ClientRequest", back_populates="comments")
    author = db.relationship("User", back_populates="comments")
