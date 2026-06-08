import json

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.domain.service import Service
from app.domain.user import User
from app.extensions import db
from app.services.sentiment_service import get_model_status as read_model_status
from app.utils.access_control import roles_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard")
@roles_required("admin")
def dashboard():
    users_count = User.query.count()
    services_count = Service.query.count()
    model_status = read_model_status()
    return render_template(
        "admin_dashboard.html",
        users_count=users_count,
        services_count=services_count,
        model_status=model_status,
    )


@admin_bp.route("/users")
@roles_required("admin")
def users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin_users.html", users=users_list)


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@roles_required("admin")
def update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get("role")
    if new_role in ["client", "manager", "admin"]:
        user.role = new_role
        db.session.commit()
        flash("Роль пользователя обновлена.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/services", methods=["GET", "POST"])
@roles_required("admin")
def services():
    if request.method == "POST":
        service = Service(
            title=request.form.get("title", "").strip(),
            slug=request.form.get("slug", "").strip(),
            short_description=request.form.get("short_description", "").strip(),
            full_description=request.form.get("full_description", "").strip(),
            is_active=True,
        )
        if service.title and service.slug:
            db.session.add(service)
            db.session.commit()
            flash("Услуга добавлена.", "success")
        else:
            flash("Заполните название и ссылочный код услуги.", "danger")
    services_list = Service.query.order_by(Service.title.asc()).all()
    return render_template("admin_services.html", services=services_list)


@admin_bp.route("/model")
@roles_required("admin")
def model_status():
    model_status_data = read_model_status()
    model_info_json = json.dumps(
        model_status_data.get("info", {}),
        ensure_ascii=False,
        indent=2,
    )
    return render_template(
        "admin_model.html",
        model_status=model_status_data,
        model_info_json=model_info_json,
    )
