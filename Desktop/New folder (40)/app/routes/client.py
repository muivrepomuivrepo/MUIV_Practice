from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.domain.audit_log import AuditLog
from app.domain.attachment import Attachment
from app.domain.client_request import ClientRequest
from app.domain.feedback import Feedback
from app.domain.service import Service
from app.domain.user import User
from app.extensions import db
from app.services.aspect_service import AspectService
from app.services.attachment_service import add_request_attachment
from app.services.notification_service import notify_roles
from app.services.request_service import add_comment, create_request
from app.services.sentiment_service import SentimentService
from app.utils.access_control import client_or_staff_required, roles_required
from app.utils.file_uploads import ALLOWED_EXTENSIONS, allowed_file, resolve_uploaded_file

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
        attachment_file = request.files.get("attachment")
        if not title or not description or not service_id:
            flash("Заполните название, описание и услугу.", "danger")
            return render_template("request_create.html", services=services)
        if attachment_file and attachment_file.filename and not allowed_file(attachment_file.filename):
            extensions = ", ".join(sorted(ALLOWED_EXTENSIONS))
            flash(f"Недопустимый формат файла. Разрешены: {extensions}.", "danger")
            return render_template("request_create.html", services=services)
        request_item = create_request(title, description, service_id, object_address, priority)
        if attachment_file and attachment_file.filename:
            try:
                add_request_attachment(request_item, attachment_file)
                flash("Заявка и приложенный файл сохранены.", "success")
            except (OSError, ValueError) as error:
                flash(f"Заявка создана, но файл не сохранен: {error}", "warning")
        else:
            flash("Заявка создана.", "success")
        return redirect(url_for("client.request_detail", request_id=request_item.id))
    return render_template("request_create.html", services=services)


@client_bp.route("/requests/<int:request_id>", methods=["GET", "POST"])
@login_required
def request_detail(request_id):
    request_item = db.get_or_404(ClientRequest, request_id)
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


@client_bp.route("/requests/<int:request_id>/attachments", methods=["POST"])
@login_required
def upload_attachment(request_id):
    request_item = db.get_or_404(ClientRequest, request_id)
    client_or_staff_required(request_item.client_id)
    attachment_file = request.files.get("attachment")
    if not attachment_file or not attachment_file.filename:
        flash("Выберите файл для загрузки.", "danger")
        return redirect(request.referrer or url_for("client.request_detail", request_id=request_item.id))

    try:
        add_request_attachment(request_item, attachment_file)
        flash("Файл добавлен к заявке.", "success")
    except (OSError, ValueError) as error:
        flash(str(error), "danger")
    return redirect(request.referrer or url_for("client.request_detail", request_id=request_item.id))


@client_bp.route("/attachments/<int:attachment_id>/download")
@login_required
def download_attachment(attachment_id):
    attachment = db.get_or_404(Attachment, attachment_id)
    client_or_staff_required(attachment.request.client_id)
    try:
        file_path = resolve_uploaded_file(attachment.stored_name)
    except ValueError:
        abort(404)
    if not file_path.is_file():
        abort(404)
    return send_file(
        file_path,
        as_attachment=True,
        download_name=attachment.original_name,
        mimetype=attachment.mime_type or "application/octet-stream",
    )


@client_bp.route("/requests/<int:request_id>/feedback", methods=["GET", "POST"])
@roles_required("client")
def create_feedback(request_id):
    request_item = db.get_or_404(ClientRequest, request_id)
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
        notify_roles(
            ["manager", "admin"],
            "Получен новый отзыв",
            f"К заявке #{request_item.id} добавлен отзыв клиента.",
            related_request_id=request_item.id,
            exclude_user_id=current_user.id,
        )
        db.session.commit()
        flash("Отзыв сохранен и проанализирован.", "success")
        return redirect(url_for("client.request_detail", request_id=request_item.id))
    return render_template("feedback_create.html", request_item=request_item)


@client_bp.route("/profile", methods=["GET", "POST"])
@roles_required("client")
def profile():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        company = request.form.get("company", "").strip()

        if not full_name or not email:
            flash("Заполните ФИО и электронную почту.", "danger")
            return render_template("client_profile.html")

        email_owner = User.query.filter(User.email == email, User.id != current_user.id).first()
        if email_owner:
            flash("Эта электронная почта уже используется другим пользователем.", "danger")
            return render_template("client_profile.html")

        current_user.full_name = full_name
        current_user.email = email
        current_user.phone = phone or None
        current_user.company = company or None
        db.session.add(
            AuditLog(
                action="Обновлен профиль клиента",
                entity_type="User",
                entity_id=current_user.id,
                user_id=current_user.id,
            )
        )
        db.session.commit()
        flash("Данные профиля обновлены.", "success")
        return redirect(url_for("client.profile"))

    return render_template("client_profile.html")
