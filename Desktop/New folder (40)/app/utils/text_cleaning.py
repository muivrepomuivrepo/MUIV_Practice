import re


def clean_text(text_value):
    text_value = str(text_value)
    text_value = text_value.replace("ё", "е").replace("Ё", "Е")
    text_value = re.sub(r"http\S+|www\.\S+", " ", text_value)
    text_value = re.sub(r"\S+@\S+", " ", text_value)
    text_value = re.sub(r"[\n\r\t]+", " ", text_value)
    text_value = re.sub(r"\s+", " ", text_value)
    return text_value.strip()
