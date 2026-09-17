from io import BytesIO

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user

from app.domain.audit_log import AuditLog
from app.domain.client_request import ClientRequest
from app.domain.contact_message import ContactMessage
from app.domain.user import User
from app.extensions import db
from app.services.notification_service import create_notification
from app.services.report_service import (
    REPORT_TYPES,
    generate_report,
    generate_requests_csv,
    get_aspect_statistics,
    get_sentiment_statistics,
    get_service_statistics,
    get_status_statistics,
    list_generated_reports,
    resolve_generated_report,
)
from app.utils.access_control import roles_required
from app.utils.datetime_utils import utc_now

manager_bp = Blueprint("manager", __name__)


@manager_bp.route("/dashboard")
@roles_required("manager", "admin")
def dashboard():
    requests = ClientRequest.query.order_by(ClientRequest.created_at.desc()).limit(10).all()
    status_stats = get_status_statistics()
    sentiment_stats = get_sentiment_statistics()
    new_messages_count = ContactMessage.query.filter_by(status="new").count()
    return render_template(
        "manager_dashboard.html",
        requests=requests,
        status_stats=status_stats,
        sentiment_stats=sentiment_stats,
        new_messages_count=new_messages_count,
    )


@manager_bp.route("/requests")
@roles_required("manager", "admin")
def requests_list():
    status = request.args.get("status")
    query = ClientRequest.query.order_by(ClientRequest.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    requests = query.all()
    return render_template("manager_requests.html", requests=requests, selected_status=status)


@manager_bp.route("/requests/<int:request_id>", methods=["GET", "POST"])
@roles_required("manager", "admin")
def request_detail(request_id):
    request_item = db.get_or_404(ClientRequest, request_id)
    managers = User.query.filter(User.role.in_(["manager", "admin"])).all()
    if request.method == "POST":
        old_status = request_item.status
        old_manager_id = request_item.manager_id
        request_item.status = request.form.get("status", request_item.status)
        manager_id = request.form.get("manager_id", type=int)
        request_item.manager_id = manager_id if manager_id else None
        db.session.add(
            AuditLog(
                action="Обновлена заявка менеджером",
                entity_type="ClientRequest",
                entity_id=request_item.id,
                details=(
                    f"Статус: {old_status} → {request_item.status}; "
                    f"ответственный: {old_manager_id or 'не назначен'} → "
                    f"{request_item.manager_id or 'не назначен'}"
                ),
                user_id=current_user.id,
            )
        )
        create_notification(
            request_item.client_id,
            "Статус заявки обновлен",
            f"Заявка #{request_item.id}: новый статус — {request_item.status_label()}.",
            related_request_id=request_item.id,
        )
        db.session.commit()
        flash("Заявка обновлена.", "success")
        return redirect(url_for("manager.request_detail", request_id=request_item.id))
    return render_template("manager_request_detail.html", request_item=request_item, managers=managers)


@manager_bp.route("/reports")
@roles_required("manager", "admin")
def reports():
    return render_template(
        "reports.html",
        status_stats=get_status_statistics(),
        service_stats=get_service_statistics(),
        sentiment_stats=get_sentiment_statistics(),
        aspect_stats=get_aspect_statistics(),
        report_types=REPORT_TYPES,
        generated_reports=list_generated_reports(),
    )


@manager_bp.route("/reports/generate", methods=["POST"])
@roles_required("manager", "admin")
def generate_report_file():
    report_type = request.form.get("report_type", "")
    report_format = request.form.get("report_format", "")
    try:
        report_path = generate_report(report_type, report_format)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("manager.reports"))

    db.session.add(
        AuditLog(
            action="Сформирован отчет",
            entity_type="Report",
            details=report_path.name,
            user_id=current_user.id,
        )
    )
    db.session.commit()
    return send_file(
        report_path,
        as_attachment=True,
        download_name=report_path.name,
    )


@manager_bp.route("/reports/files/<path:filename>")
@roles_required("manager", "admin")
def download_report(filename):
    try:
        report_path = resolve_generated_report(filename)
    except ValueError:
        abort(404)
    if not report_path.is_file():
        abort(404)
    return send_file(
        report_path,
        as_attachment=True,
        download_name=report_path.name,
    )


@manager_bp.route("/reports/export.csv")
@roles_required("manager", "admin")
def export_report():
    report_data = generate_requests_csv()
    filename = f"irbis_requests_{utc_now().strftime('%Y%m%d_%H%M')}.csv"
    return send_file(
        BytesIO(report_data),
        as_attachment=True,
        download_name=filename,
        mimetype="text/csv; charset=utf-8",
    )


@manager_bp.route("/clients")
@roles_required("manager", "admin")
def clients():
    clients_list = User.query.filter_by(role="client").order_by(User.full_name.asc()).all()
    return render_template("manager_clients.html", clients=clients_list)


@manager_bp.route("/contact-messages")
@roles_required("manager", "admin")
def contact_messages():
    selected_status = request.args.get("status", "").strip()
    query = ContactMessage.query.order_by(ContactMessage.created_at.desc())
    if selected_status in {"new", "in_progress", "processed"}:
        query = query.filter_by(status=selected_status)
    else:
        selected_status = ""
    return render_template(
        "manager_contact_messages.html",
        messages=query.all(),
        selected_status=selected_status,
    )


@manager_bp.route("/contact-messages/<int:message_id>/status", methods=["POST"])
@roles_required("manager", "admin")
def update_contact_message(message_id):
    contact_message = db.get_or_404(ContactMessage, message_id)
    new_status = request.form.get("status", "")
    if new_status not in {"new", "in_progress", "processed"}:
        flash("Выбран недопустимый статус сообщения.", "danger")
        return redirect(url_for("manager.contact_messages"))

    contact_message.status = new_status
    contact_message.handled_by_id = current_user.id
    contact_message.handled_at = utc_now() if new_status == "processed" else None
    db.session.add(
        AuditLog(
            action="Изменен статус сообщения обратной связи",
            entity_type="ContactMessage",
            entity_id=contact_message.id,
            details=contact_message.status_label(),
            user_id=current_user.id,
        )
    )
    db.session.commit()
    flash("Статус сообщения обновлен.", "success")
    return redirect(url_for("manager.contact_messages"))
