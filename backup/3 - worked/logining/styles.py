from kivy.core.text import LabelBase
from kivy.metrics import sp

# Регистрируем шрифт Times New Roman
def register_fonts():
    try:
        LabelBase.register(name='TimesNewRoman',
                          fn_regular='times.ttf',
                          fn_bold='timesbd.ttf',
                          fn_italic='timesi.ttf',
                          fn_bolditalic='timesbi.ttf')
        return True
    except:
        # Если шрифт не найден, используем стандартный
        return False

# Стили для заголовков
def get_title_style():
    return {
        'size_hint_y': None,
        'height': sp(80),
        'halign': 'center',
        'font_size': sp(20),
        'bold': True,
        'font_name': 'TimesNewRoman'
    }

# Стили для меток
def get_label_style():
    return {
        'size_hint_y': None,
        'height': sp(30),
        'font_name': 'TimesNewRoman',
        'color': (0.8, 0.8, 0.8, 1)
    }

# Стили для полей ввода
def get_input_style():
    return {
        'multiline': False,
        'size_hint_y': None,
        'height': sp(40),
        'background_color': (1, 1, 1, 0.1),
        'foreground_color': (1, 1, 1, 1),
        'font_name': 'TimesNewRoman'
    }

# Стили для кнопок
def get_button_style(color=(0.2, 0.6, 1, 0.8)):
    return {
        'size_hint_y': None,
        'height': sp(50),
        'background_color': color,
        'font_name': 'TimesNewRoman'
    }