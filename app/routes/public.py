from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.domain.service import Service

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
    project_items = [
        {"title": "Сопровождение строительства жилого комплекса", "city": "Санкт-Петербург", "description": "Контроль сроков, качества работ и документации на этапе строительно-монтажных работ."},
        {"title": "Обследование административного здания", "city": "Ленинградская область", "description": "Фиксация технического состояния конструкций и подготовка заключения для заказчика."},
        {"title": "Проверка проектной документации", "city": "Северо-Западный регион", "description": "Анализ проектных решений, замечаний подрядчика и состава исполнительной документации."},
    ]
    return render_template("projects.html", projects=project_items)


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/contacts", methods=["GET", "POST"])
def contacts():
    if request.method == "POST":
        flash("Сообщение принято. Для полноценной обработки обращения зарегистрируйтесь или войдите в личный кабинет.", "success")
        return redirect(url_for("public.contacts"))
    return render_template("contacts.html")


@public_bp.route("/faq")
def faq():
    return render_template("faq.html")


@public_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")
