from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.domain.client_request import ClientRequest
from app.domain.user import User
from app.extensions import db
from app.services.report_service import get_aspect_statistics, get_sentiment_statistics, get_service_statistics, get_status_statistics
from app.utils.access_control import roles_required

manager_bp = Blueprint("manager", __name__)


@manager_bp.route("/dashboard")
@roles_required("manager", "admin")
def dashboard():
    requests = ClientRequest.query.order_by(ClientRequest.created_at.desc()).limit(10).all()
    status_stats = get_status_statistics()
    sentiment_stats = get_sentiment_statistics()
    return render_template("manager_dashboard.html", requests=requests, status_stats=status_stats, sentiment_stats=sentiment_stats)


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
    request_item = ClientRequest.query.get_or_404(request_id)
    managers = User.query.filter(User.role.in_(["manager", "admin"])).all()
    if request.method == "POST":
        request_item.status = request.form.get("status", request_item.status)
        manager_id = request.form.get("manager_id", type=int)
        request_item.manager_id = manager_id if manager_id else None
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
    )
