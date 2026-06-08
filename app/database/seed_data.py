from app.domain.client_request import ClientRequest
from app.domain.feedback import Feedback
from app.domain.request_comment import RequestComment
from app.domain.service import Service
from app.domain.user import User
from app.extensions import db


def seed_database():
    seed_users()
    seed_services()
    seed_demo_requests()


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
