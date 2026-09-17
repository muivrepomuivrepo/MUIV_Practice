from app.services.aspect_service import AspectService


def test_aspect_detection(app):
    with app.app_context():
        service = AspectService()
        assert service.detect("Менеджер быстро ответил и связался с нами") == "Коммуникация"
        assert service.detect("Нужно проверить договор и проектную документацию") == "Документы"
