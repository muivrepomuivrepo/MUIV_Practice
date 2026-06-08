from datetime import datetime

from app.extensions import db


class Feedback(db.Model):
    __tablename__ = "feedback"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(40), nullable=False)
    aspect = db.Column(db.String(80), nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    model_available = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    request_id = db.Column(db.Integer, db.ForeignKey("client_requests.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    request = db.relationship("ClientRequest", back_populates="feedback_items")
    author = db.relationship("User", back_populates="feedback_items")

    def sentiment_label(self):
        labels = {
            "negative": "Отрицательная",
            "neutral": "Нейтральная",
            "positive": "Положительная",
        }
        return labels.get(self.sentiment, self.sentiment)
