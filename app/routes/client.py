from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.domain.client_request import ClientRequest
from app.domain.feedback import Feedback
from app.domain.service import Service
from app.extensions import db
from app.services.aspect_service import AspectService
from app.services.request_service import add_comment, create_request
from app.services.sentiment_service import SentimentService
from app.utils.access_control import roles_required

client_bp = Blueprint("client", __name__)


@client_bp.route("/dashboard")
@roles_required("client")
def dashboard():
    requests = ClientRequest.query.filter_by(client_id=current_user.id).order_by(ClientRequest.created_at.desc()).all()
    return render_template("client_dashboard.html", requests=requests)


@client_bp.route("/requests/new", methods=["GET", "POST"])
@roles_required("client")
def create_request_view():
    services = Service.query.filter_by(is_active=True).all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        service_id = request.form.get("service_id", type=int)
        object_address = request.form.get("object_address", "").strip()
        priority = request.form.get("priority", "medium")
        if not title or not description or not service_id:
            flash("Заполните название, описание и услугу.", "danger")
            return render_template("request_create.html", services=services)
        request_item = create_request(title, description, service_id, object_address, priority)
        flash("Заявка создана.", "success")
        return redirect(url_for("client.request_detail", request_id=request_item.id))
    return render_template("request_create.html", services=services)


@client_bp.route("/requests/<int:request_id>", methods=["GET", "POST"])
@login_required
def request_detail(request_id):
    request_item = ClientRequest.query.get_or_404(request_id)
    if current_user.is_client() and request_item.client_id != current_user.id:
        flash("Нет доступа к заявке.", "danger")
        return redirect(url_for("client.dashboard"))
    if request.method == "POST":
        body = request.form.get("body", "").strip()
        if body:
            add_comment(request_item, body, is_internal=False)
            flash("Комментарий добавлен.", "success")
        return redirect(url_for("client.request_detail", request_id=request_item.id))
    return render_template("request_detail.html", request_item=request_item)


@client_bp.route("/requests/<int:request_id>/feedback", methods=["GET", "POST"])
@roles_required("client")
def create_feedback(request_id):
    request_item = ClientRequest.query.get_or_404(request_id)
    if request_item.client_id != current_user.id:
        flash("Нет доступа к заявке.", "danger")
        return redirect(url_for("client.dashboard"))
    if request.method == "POST":
        feedback_text = request.form.get("text", "").strip()
        if not feedback_text:
            flash("Введите текст отзыва.", "danger")
            return render_template("feedback_create.html", request_item=request_item)
        sentiment_service = SentimentService()
        aspect_service = AspectService()
        prediction = sentiment_service.predict(feedback_text)
        aspect = aspect_service.detect(feedback_text)
        feedback_item = Feedback(
            request_id=request_item.id,
            author_id=current_user.id,
            text=feedback_text,
            sentiment=prediction["sentiment"],
            aspect=aspect,
            confidence=prediction.get("confidence"),
            model_available=prediction.get("model_available", False),
        )
        db.session.add(feedback_item)
        db.session.commit()
        flash("Отзыв сохранен и проанализирован.", "success")
        return redirect(url_for("client.request_detail", request_id=request_item.id))
    return render_template("feedback_create.html", request_item=request_item)
