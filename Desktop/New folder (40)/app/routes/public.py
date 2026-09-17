from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.domain.contact_message import ContactMessage
from app.domain.feedback import Feedback
from app.domain.project import Project
from app.domain.service import Service
from app.extensions import db
from app.services.notification_service import notify_roles

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    services = Service.query.filter_by(is_active=True).limit(6).all()
    return render_template("index.html", services=services)


@public_bp.route("/services")
def services():
    services_list = Service.query.filter_by(is_active=True).all()
    return render_template("services.html", services=services_list)


@public_bp.route("/services/<slug>")
def service_detail(slug):
    service = Service.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template("service_detail.html", service=service)


@public_bp.route("/projects")
def projects():
    project_items = Project.query.filter_by(is_active=True).order_by(Project.created_at.desc()).all()
    return render_template("projects.html", projects=project_items)


@public_bp.route("/workflow")
def workflow():
    return render_template("workflow.html")


@public_bp.route("/reviews")
def reviews():
    feedback_items = Feedback.query.order_by(Feedback.created_at.desc()).limit(12).all()
    return render_template("reviews.html", feedback_items=feedback_items)


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        message_text = request.form.get("message", "").strip()
        consent = request.form.get("consent") == "yes"

        if not name or not email or not message_text:
            flash("Заполните имя, электронную почту и текст сообщения.", "danger")
            return render_template("contacts.html")
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Укажите корректный адрес электронной почты.", "danger")
            return render_template("contacts.html")
        if not consent:
            flash("Необходимо подтвердить согласие на обработку данных.", "danger")
            return render_template("contacts.html")

        contact_message = ContactMessage(
            name=name,
            email=email,
            phone=phone or None,
            message=message_text,
        )
        db.session.add(contact_message)
        db.session.flush()
        notify_roles(
            ["manager", "admin"],
            "Новое сообщение обратной связи",
            f"Получено сообщение #{contact_message.id} от {name}.",
            exclude_user_id=current_user.id if current_user.is_authenticated else None,
        )
        db.session.commit()
        flash(f"Сообщение #{contact_message.id} принято. Специалист свяжется с вами.", "success")
        return redirect(url_for("public.contacts"))
    return render_template("contacts.html")


@public_bp.route("/faq")
def faq():
    return render_template("faq.html")


@public_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")
