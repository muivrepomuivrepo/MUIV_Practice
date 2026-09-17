from app.services.sentiment_service import SentimentService


def test_fallback_sentiment_detection(app):
    with app.app_context():
        service = SentimentService()
        assert service.predict("Спасибо, все сделали быстро и качественно")["sentiment"] == "positive"
        assert service.predict("Работы выполнены плохо, обнаружены дефекты")["sentiment"] == "negative"
