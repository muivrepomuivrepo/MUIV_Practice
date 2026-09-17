from pathlib import Path

from flask import current_app

from app.domain.client_request import ClientRequest
from app.domain.attachment import Attachment
from app.domain.contact_message import ContactMessage
from app.domain.feedback import Feedback
from app.domain.notification import Notification
from app.domain.project import Project
from app.domain.request_comment import RequestComment
from app.domain.service import Service
from app.domain.system_setting import SystemSetting
from app.domain.user import User
from app.extensions import db


def seed_database():
    seed_users()
    seed_services()
    seed_projects()
    seed_demo_requests()
    seed_contact_messages()
    seed_system_settings()
    seed_attachments()
    seed_notifications()


def seed_users():
    users_data = [
        ("admin", "admin@example.local", "Администратор системы", "admin", "admin1234", "ООО «ГК «ИРБИС»"),
        ("manager", "manager@example.local", "Менеджер клиентского отдела", "manager", "manager1234", "ООО «ГК «ИРБИС»"),
        ("client", "client@example.local", "Демонстрационный клиент", "client", "client1234", "ООО «Северный проект»"),
    ]
    for username, email, full_name, role, password, company in users_data:
        if not User.query.filter_by(username=username).first():
            user = User(username=username, email=email, full_name=full_name, role=role, company=company, phone="+7 900 000-00-00")
            user.set_password(password)
            db.session.add(user)
    db.session.commit()


def seed_services():
    services_data = [
        ("Строительный контроль", "construction-control", "Контроль качества и сроков строительно-монтажных работ.", "Услуга включает проверку соответствия работ проектной документации, фиксацию замечаний, подготовку отчетов и сопровождение взаимодействия с подрядчиками."),
        ("Технический надзор", "technical-supervision", "Надзор за выполнением работ на объекте заказчика.", "Специалисты контролируют соблюдение требований проекта, графика, технических регламентов и условий договора."),
        ("Обследование зданий", "building-inspection", "Техническое обследование конструкций и инженерных систем.", "Проводится осмотр объекта, анализ дефектов, подготовка выводов и рекомендаций для дальнейшей эксплуатации или реконструкции."),
        ("Управление проектированием", "design-management", "Координация проектных решений и документации.", "Сервис помогает согласовать требования заказчика, проектировщиков и подрядчиков, а также контролировать состав проектной документации."),
        ("Сметная экспертиза", "estimate-review", "Проверка стоимости, объемов и состава работ.", "Анализ сметной документации помогает выявлять завышенные позиции, неточности и риски перерасхода бюджета."),
        ("Технический заказчик", "technical-customer", "Комплексное сопровождение инвестиционно-строительного проекта.", "Услуга объединяет организацию взаимодействия участников проекта, контроль документации, сроков, стоимости и качества работ."),
    ]
    for title, slug, short_description, full_description in services_data:
        if not Service.query.filter_by(slug=slug).first():
            db.session.add(Service(title=title, slug=slug, short_description=short_description, full_description=full_description))
    db.session.commit()


def seed_projects():
    projects_data = [
        (
            "Сопровождение строительства жилого комплекса",
            "residential-complex-supervision",
            "Санкт-Петербург",
            "Контроль сроков, качества работ и документации на этапе строительно-монтажных работ.",
        ),
        (
            "Обследование административного здания",
            "administrative-building-inspection",
            "Ленинградская область",
            "Фиксация технического состояния конструкций и подготовка заключения для заказчика.",
        ),
        (
            "Проверка проектной документации",
            "design-documentation-review",
            "Северо-Западный регион",
            "Анализ проектных решений, замечаний подрядчика и состава исполнительной документации.",
        ),
    ]
    for title, slug, city, description in projects_data:
        if not Project.query.filter_by(slug=slug).first():
            db.session.add(Project(title=title, slug=slug, city=city, description=description))
    db.session.commit()


def seed_demo_requests():
    if ClientRequest.query.first():
        return
    client = User.query.filter_by(username="client").first()
    manager = User.query.filter_by(username="manager").first()
    service = Service.query.filter_by(slug="construction-control").first()
    request_item = ClientRequest(
        title="Проверка качества работ на объекте",
        description="Необходимо организовать строительный контроль отделочных работ и подготовить перечень замечаний подрядчику.",
        object_address="Санкт-Петербург, демонстрационный объект",
        priority="high",
        status="in_progress",
        client_id=client.id,
        manager_id=manager.id,
        service_id=service.id,
    )
    db.session.add(request_item)
    db.session.flush()
    db.session.add(RequestComment(request_id=request_item.id, author_id=client.id, body="Просим проверить сроки и качество работ по договору."))
    db.session.add(RequestComment(request_id=request_item.id, author_id=manager.id, body="Заявка принята, назначается специалист строительного контроля."))
    db.session.add(Feedback(request_id=request_item.id, author_id=client.id, text="Менеджер быстро связался и объяснил порядок проверки документов.", sentiment="positive", aspect="Коммуникация", model_available=False))
    db.session.commit()


def seed_contact_messages():
    if ContactMessage.query.first():
        return
    db.session.add(
        ContactMessage(
            name="Алексей Смирнов",
            email="alexey.smirnov@example.local",
            phone="+7 900 123-45-67",
            message="Нужна консультация по техническому обследованию здания перед реконструкцией.",
            status="new",
        )
    )
    db.session.commit()


def seed_system_settings():
    settings_data = [
        ("company_email", "info@irbis.example", "Контактная электронная почта"),
        ("support_phone", "+7 812 000-00-00", "Телефон клиентского отдела"),
        ("report_title", "Реестр клиентских заявок", "Название выгружаемого отчета"),
        ("max_upload_size_mb", "16", "Максимальный размер загружаемого файла, МБ"),
    ]
    for key, value, description in settings_data:
        if not SystemSetting.query.filter_by(key=key).first():
            db.session.add(SystemSetting(key=key, value=value, description=description))
    db.session.commit()


def seed_attachments():
    request_item = ClientRequest.query.order_by(ClientRequest.id.asc()).first()
    if request_item is None:
        return

    stored_name = f"requests/{request_item.id}/demo_request_document.txt"
    if not Attachment.query.filter_by(stored_name=stored_name).first():
        file_path = Path(current_app.config["UPLOAD_FOLDER"]) / stored_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not file_path.exists():
            file_path.write_text(
                "Исходные данные по объекту\n"
                "Назначение: демонстрация хранения файлов заявки.\n"
                "Документ доступен владельцу заявки, менеджеру и администратору.\n",
                encoding="utf-8",
            )
        db.session.add(
            Attachment(
                original_name="Исходные данные по объекту.txt",
                stored_name=stored_name,
                mime_type="text/plain",
                size_bytes=file_path.stat().st_size,
                request_id=request_item.id,
                uploader_id=request_item.client_id,
            )
        )
        db.session.commit()


def seed_notifications():
    if Notification.query.first():
        return
    request_item = ClientRequest.query.order_by(ClientRequest.id.asc()).first()
    if request_item is None:
        return
    db.session.add(
        Notification(
            user_id=request_item.client_id,
            title="Заявка принята в работу",
            message=f"Заявка #{request_item.id} назначена ответственному менеджеру.",
            related_request_id=request_item.id,
        )
    )
    db.session.commit()
