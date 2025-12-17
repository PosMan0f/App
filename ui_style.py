from kivy.core.window import Window
from kivy.metrics import dp, sp

# Базовые размеры окна для расчёта пропорций
BASE_WIDTH = 1280
BASE_HEIGHT = 720


def _scale_factor() -> float:
    """Возвращает коэффициент масштабирования относительно базового окна."""
    width_ratio = Window.width / BASE_WIDTH if BASE_WIDTH else 1
    height_ratio = Window.height / BASE_HEIGHT if BASE_HEIGHT else 1
    factor = min(width_ratio, height_ratio)
    return factor if factor > 0 else 1


def scale_dp(value: float) -> float:
    """Масштабирует значения расстояний/размеров с учётом окна."""
    return dp(value * _scale_factor())


def scale_font(value: float) -> float:
    """Масштабирует размер шрифта относительно окна."""
    return sp(value * _scale_factor())


def vw(percent: float) -> float:
    """Преобразует процент ширины окна в абсолютное значение."""
    return Window.width * percent


def vh(percent: float) -> float:
    """Преобразует процент высоты окна в абсолютное значение."""
    return Window.height * percent


palette = {
    'background': (0.08, 0.10, 0.13, 1),
    'surface': (0.12, 0.15, 0.19, 1),
    'surface_alt': (0.16, 0.19, 0.24, 1),
    'accent': (0.27, 0.43, 0.63, 1),
    'accent_muted': (0.21, 0.33, 0.48, 1),
    'text_primary': (0.93, 0.95, 0.98, 1),
    'text_muted': (0.72, 0.76, 0.82, 1),
    'success': (0.38, 0.68, 0.45, 1),
    'danger': (0.78, 0.32, 0.32, 1),
}
