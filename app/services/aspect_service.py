import json
from pathlib import Path

from flask import current_app

DEFAULT_ASPECT_KEYWORDS = {
    "Сроки": ["срок", "задерж", "долго", "быстро", "оперативно", "ожидан", "перенесли"],
    "Стоимость": ["стоимость", "цена", "дорого", "смета", "расчет", "оплата", "деньги"],
    "Документы": ["документ", "акт", "договор", "смета", "проект", "чертеж", "отчет", "заключение"],
    "Коммуникация": ["менеджер", "специалист", "ответ", "позвонили", "связались", "общение", "консультация"],
    "Качество работ": ["качество", "работа", "монтаж", "ремонт", "ошибка", "дефект", "замечание", "контроль"],
    "Объект строительства": ["дом", "квартира", "здание", "объект", "стройка", "жилой комплекс", "помещение"],
}


class AspectService:
    def __init__(self):
        self.aspect_keywords = self.load_keywords()

    def load_keywords(self):
        keywords_path = Path(current_app.config["MODEL_DIR"]) / "aspect_keywords.json"
        if keywords_path.exists():
            with open(keywords_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return DEFAULT_ASPECT_KEYWORDS

    def detect(self, text_value):
        lowered_text = str(text_value).lower().replace("ё", "е")
        scores = {}
        for aspect_name, keywords in self.aspect_keywords.items():
            score = 0
            for keyword in keywords:
                normalized_keyword = str(keyword).lower().replace("ё", "е")
                if normalized_keyword in lowered_text:
                    score += 1
            scores[aspect_name] = score
        best_aspect = max(scores, key=scores.get)
        if scores[best_aspect] == 0:
            return "Общее обращение"
        return best_aspect
