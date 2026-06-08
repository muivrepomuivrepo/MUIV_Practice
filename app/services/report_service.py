from sqlalchemy import func

from app.domain.client_request import ClientRequest
from app.domain.feedback import Feedback
from app.domain.service import Service
from app.extensions import db


def get_status_statistics():
    rows = db.session.query(ClientRequest.status, func.count(ClientRequest.id)).group_by(ClientRequest.status).all()
    return {status: count for status, count in rows}


def get_service_statistics():
    rows = (
        db.session.query(Service.title, func.count(ClientRequest.id))
        .outerjoin(ClientRequest, ClientRequest.service_id == Service.id)
        .group_by(Service.id)
        .order_by(func.count(ClientRequest.id).desc())
        .all()
    )
    return rows


def get_sentiment_statistics():
    rows = db.session.query(Feedback.sentiment, func.count(Feedback.id)).group_by(Feedback.sentiment).all()
    return {sentiment: count for sentiment, count in rows}


def get_aspect_statistics():
    rows = db.session.query(Feedback.aspect, func.count(Feedback.id)).group_by(Feedback.aspect).all()
    return {aspect: count for aspect, count in rows}
