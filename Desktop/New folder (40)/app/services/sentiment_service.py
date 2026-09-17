import json
from pathlib import Path

import joblib
from flask import current_app

from app.utils.text_cleaning import clean_text


class SentimentService:
    def __init__(self):
        self.model = None
        self.model_info = None
        self.model_loaded = False
        self.load_artifacts()

    def load_artifacts(self):
        model_dir = Path(current_app.config["MODEL_DIR"])
        model_path = model_dir / "model.joblib"
        info_path = model_dir / "model_info.json"

        if model_path.exists():
            self.model = joblib.load(model_path)
            self.model_loaded = True
        else:
            self.model = None
            self.model_loaded = False

        if info_path.exists():
            with open(info_path, "r", encoding="utf-8") as file:
                self.model_info = json.load(file)
        else:
            self.model_info = {}

    def predict(self, text_value):
        normalized_text = clean_text(text_value)
        if self.model_loaded and self.model is not None:
            label = self.model.predict([normalized_text])[0]
            return {
                "sentiment": str(label),
                "confidence": None,
                "model_available": True,
                "clean_text": normalized_text,
            }
        return self._fallback_predict(normalized_text)

    def _fallback_predict(self, text_value):
        lowered_text = text_value.lower()
        negative_markers = [
            "не рекомендую", "ужас", "плохо", "сорвали", "задерж", "обман", "дорого",
            "не отвеч", "претенз", "ошибка", "дефект", "разочар",
        ]
        positive_markers = [
            "спасибо", "отлич", "хорош", "рекомендую", "быстро", "качественно",
            "профессион", "понятно", "оперативно", "доволен", "благодар",
        ]
        negative_score = sum(marker in lowered_text for marker in negative_markers)
        positive_score = sum(marker in lowered_text for marker in positive_markers)
        if negative_score > positive_score:
            sentiment = "negative"
        elif positive_score > negative_score:
            sentiment = "positive"
        else:
            sentiment = "neutral"
        return {
            "sentiment": sentiment,
            "confidence": None,
            "model_available": False,
            "clean_text": text_value,
        }


def get_model_status():
    service = SentimentService()
    return {
        "available": service.model_loaded,
        "info": service.model_info,
    }
