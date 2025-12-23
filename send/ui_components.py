# send/ui_components.py
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from ui_style import palette, scale_dp, scale_font


class ThemedSpinnerOption(SpinnerOption):
    """Единый стиль для выпадающих пунктов"""

    def __init__(self, **kwargs):
        defaults = {
            'background_normal': '',
            'background_down': '',
            'background_color': palette['surface_alt'],
            'color': palette['text_primary'],
            'font_size': scale_font(15)
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class BaseLabel(Label):
    """Базовый класс для всех меток"""
    def __init__(self, **kwargs):
        defaults = {
            'color': palette['text_primary'],
            'size_hint': (1, None),
            'height': scale_dp(30),
            'font_size': scale_font(14)
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class TitleLabel(BaseLabel):
    """Заголовок экрана"""
    def __init__(self, **kwargs):
        defaults = {
            'font_size': scale_font(24),
            'bold': True,
            'height': scale_dp(40)
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class FieldLabel(BaseLabel):
    """Метка для полей ввода"""
    def __init__(self, **kwargs):
        defaults = {
            'font_size': scale_font(16),
            'height': scale_dp(25)
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class BaseTextInput(TextInput):
    """Базовый класс для полей ввода"""
    def __init__(self, **kwargs):
        defaults = {
            'multiline': False,
            'size_hint': (1, None),
            'height': scale_dp(45),
            'background_color': palette['surface_alt'],
            'foreground_color': palette['text_primary'],
            'padding': scale_dp(10),
            'background_normal': '',
            'background_active': '',
            'write_tab': False,
            'font_size': scale_font(15)
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class MultilineTextInput(BaseTextInput):
    """Многострочное поле ввода"""
    def __init__(self, **kwargs):
        defaults = {
            'multiline': True,
            'height': scale_dp(120)
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class DepartmentSpinner(Spinner):
    """Спиннер для выбора отдела"""
    def __init__(self, **kwargs):
        defaults = {
            'text': 'Выберите отдел',
            'values': ('IT-отдел', 'Юридический отдел', 'HR-отдел'),
            'size_hint': (1, None),
            'height': scale_dp(45),
            'background_color': palette['surface_alt'],
            'background_normal': '',
            'background_down': '',
            'color': palette['text_primary'],
            'font_size': scale_font(15),
            'option_cls': ThemedSpinnerOption
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class SubmitButton(Button):
    """Кнопка отправки"""
    def __init__(self, **kwargs):
        defaults = {
            'size_hint': (1, None),
            'height': scale_dp(50),
            'background_color': palette['accent'],
            'background_normal': '',
            'background_down': '',
            'color': palette['text_primary'],
            'font_size': scale_font(18),
            'bold': True
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

class StatusLabel(BaseLabel):
    """Метка статуса"""
    def __init__(self, **kwargs):
        defaults = {
            'font_size': scale_font(14),
            'height': scale_dp(0),
            'opacity': 0,
            'halign': 'center',
            'valign': 'middle',
            'padding': (scale_dp(8), scale_dp(6))
        }
        defaults.update(kwargs)
        super().__init__(**defaults)
        with self.canvas.before:
            self._bg_color = Color(*palette['surface_alt'])
            self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[scale_dp(10)] * 4)
        self.bind(
            pos=lambda *args: setattr(self._bg_rect, 'pos', self.pos),
            size=lambda *args: setattr(self._bg_rect, 'size', self.size)
        )
        self.bind(size=lambda *args: setattr(self, 'text_size', self.size))

    def set_background(self, color):
        self._bg_color.rgba = color
