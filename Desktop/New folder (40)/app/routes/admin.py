import json

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.domain.audit_log import AuditLog
from app.domain.project import Project
from app.domain.service import Service
from app.domain.system_setting import SystemSetting
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
    projects_count = Project.query.count()
    model_status = read_model_status()
    return render_template(
        "admin_dashboard.html",
        users_count=users_count,
        services_count=services_count,
        projects_count=projects_count,
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
    user = db.get_or_404(User, user_id)
    new_role = request.form.get("role")
    if new_role in ["client", "manager", "admin"]:
        old_role = user.role
        user.role = new_role
        db.session.add(
            AuditLog(
                action="Изменена роль пользователя",
                entity_type="User",
                entity_id=user.id,
                details=f"Роль изменена: {old_role} → {new_role}",
                user_id=current_user.id,
            )
        )
        db.session.commit()
        flash("Роль пользователя обновлена.", "success")
    else:
        flash("Выбрана недопустимая роль.", "danger")
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
            db.session.flush()
            db.session.add(
                AuditLog(
                    action="Добавлена услуга",
                    entity_type="Service",
                    entity_id=service.id,
                    details=service.title,
                    user_id=current_user.id,
                )
            )
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


@admin_bp.route("/audit-log")
@roles_required("admin")
def audit_log():
    log_entries = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(200).all()
    return render_template("admin_audit_log.html", log_entries=log_entries)


@admin_bp.route("/projects", methods=["GET", "POST"])
@roles_required("admin")
def projects():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip().lower()
        city = request.form.get("city", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not slug or not city or not description:
            flash("Заполните все поля проекта.", "danger")
        elif Project.query.filter_by(slug=slug).first():
            flash("Проект с таким ссылочным кодом уже существует.", "danger")
        else:
            project = Project(
                title=title,
                slug=slug,
                city=city,
                description=description,
            )
            db.session.add(project)
            db.session.flush()
            db.session.add(
                AuditLog(
                    action="Добавлен проект",
                    entity_type="Project",
                    entity_id=project.id,
                    details=project.title,
                    user_id=current_user.id,
                )
            )
            db.session.commit()
            flash("Проект опубликован.", "success")
            return redirect(url_for("admin.projects"))
    projects_list = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("admin_projects.html", projects=projects_list)


@admin_bp.route("/settings", methods=["GET", "POST"])
@roles_required("admin")
def settings():
    settings_list = SystemSetting.query.order_by(SystemSetting.key.asc()).all()
    if request.method == "POST":
        for setting in settings_list:
            form_key = f"setting_{setting.id}"
            if form_key in request.form:
                setting.value = request.form.get(form_key, "").strip()
                setting.updated_by_id = current_user.id
        db.session.add(
            AuditLog(
                action="Обновлены системные настройки",
                entity_type="SystemSetting",
                user_id=current_user.id,
            )
        )
        db.session.commit()
        flash("Системные настройки сохранены.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin_settings.html", settings=settings_list)
