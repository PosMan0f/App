# send/difficulty_predictor.py
from __future__ import annotations

import importlib.util
from pathlib import Path

_embedding_model = None
_difficulty_model = None

DIFFICULTY_LABELS = {
    1: "Легкая",
    2: "Средняя",
    3: "Сложная",
}


def configure_predictor(embedding_model, torch_model) -> None:
    """Настройка моделей для ML-предсказания сложности."""
    global _embedding_model, _difficulty_model
    _embedding_model = embedding_model
    _difficulty_model = torch_model


def _ml_dependencies_available() -> bool:
    return (
        _embedding_model is not None
        and _difficulty_model is not None
        and importlib.util.find_spec("numpy") is not None
        and importlib.util.find_spec("torch") is not None
        and importlib.util.find_spec("sklearn.preprocessing") is not None
    )


def configure_from_checkpoint(model_path: str) -> None:
    """Настройка моделей из чекпоинта."""
    if importlib.util.find_spec("torch") is None:
        raise RuntimeError("torch не доступен для загрузки модели.")

    from importlib import import_module
    import torch
    import torch.nn as nn

    if importlib.util.find_spec("langchain_community.embeddings") is not None:
        embeddings_module = import_module("langchain_community.embeddings")
        embeddings_cls = getattr(embeddings_module, "HuggingFaceEmbeddings")
    else:
        embeddings_module = import_module("langchain.embeddings")
        embeddings_cls = getattr(embeddings_module, "HuggingFaceEmbeddings")

    class RidgeModel(nn.Module):
        def __init__(self, dim):
            super().__init__()
            self.linear = nn.Linear(dim, 1)

        def forward(self, x):
            return self.linear(x)

    checkpoint = torch.load(model_path, map_location="cpu")
    embedding_model = embeddings_cls(model_name=checkpoint["embedding_model"])

    model = RidgeModel(checkpoint["input_dim"])
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    configure_predictor(embedding_model, model)


def format_difficulty(value: int) -> str:
    """Форматированный вывод сложности."""
    label = DIFFICULTY_LABELS.get(value, "Неизвестно")
    return f"{label} ({value})"


def _heuristic_difficulty(text: str) -> int:
    """Быстрая эвристика для определения сложности без ML."""
    normalized = (text or "").lower()
    words = [word for word in normalized.split() if word]
    word_count = len(words)

    score = 1
    if word_count >= 12:
        score += 1
    if word_count >= 25:
        score += 1

    advanced_keywords = (
        "оптимизац", "граф", "нейросет", "распредел",
        "кластер", "асинхрон", "машин", "алгоритм",
        "архитектур", "миграц", "производител",
    )
    if any(keyword in normalized for keyword in advanced_keywords):
        score += 1

    very_advanced_keywords = (
        "нагрузк", "масштаб", "отказоуст", "шифрован",
        "интеграц", "параллел", "математ", "компилят",
    )
    if any(keyword in normalized for keyword in very_advanced_keywords):
        score += 1

    return max(1, min(3, score))


def difficulty_text(raw_value: float) -> str:
    """Текстовое определение сложности по сырому значению."""
    if raw_value > 2.5:
        return DIFFICULTY_LABELS[3]
    if raw_value > 1.5:
        return DIFFICULTY_LABELS[2]
    return DIFFICULTY_LABELS[1]


def _difficulty_from_raw(raw_value: float) -> int:
    if raw_value > 2.5:
        return 3
    if raw_value > 1.5:
        return 2
    return 1


def predict_difficulty(text: str, return_raw: bool = False):
    """
    Предсказывает сложность задачи по тексту.
    Возвращает значение от 1 до 3.
    """
    if not text:
        if return_raw:
            return 1, 1.0
        return 1

    if not _ml_dependencies_available():
        raise RuntimeError("ML модель недоступна для оценки сложности.")

        import numpy as np
        import torch
        from sklearn.preprocessing import normalize

        emb_vec = _embedding_model.embed_query(text)
        emb_vec = np.array(emb_vec).reshape(1, -1)
        emb_vec = normalize(emb_vec)

        x = torch.tensor(emb_vec, dtype=torch.float32)

        with torch.no_grad():
            pred = _difficulty_model(x).item()

    pred_round = _difficulty_from_raw(pred)

    if return_raw:
        return pred_round, pred

    return pred_round


def _auto_configure_default_model():
    model_path = Path(__file__).resolve().parent / "ridge_model.pt"
    if model_path.exists():
        configure_from_checkpoint(str(model_path))
        print("Model download")


_auto_configure_default_model()
