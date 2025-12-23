from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.label import Label


class GameButton(BoxLayout):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.padding = 2

        # Цвет фона по умолчанию
        self.bg_color = (0.8, 0.8, 0.8, 1)

        # Рисуем фон плитки
        with self.canvas.before:
            self.bg = Color(*self.bg_color)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(0, 0, 0, 1)  # черная рамка
            self.border = Line(width=1, rectangle=(self.x, self.y, self.width, self.height))

        self.bind(pos=self.update_graphics, size=self.update_graphics)

        # Метка (цифра)
        self.label = Label(
            text=text,
            color=(0, 0, 0, 1),  # черный текст (активный)
            disabled_color=(0, 0, 0, 1),  # черный текст (когда disabled)
            bold=True,
            font_size='24sp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            outline_width=2,  # Толщина обводки/тени
            outline_color=(1, 1, 1, 1)  # Белая обводка
        )
        self.label.bind(size=self._update_text_size)
        self.add_widget(self.label)

    def update_graphics(self, *args):
        """Обновление рамки и фона при изменении размера"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def set_color(self, color):
        """Обновление цвета фона плитки"""
        self.bg.rgba = color

    def set_text(self, text, font_size='24sp'):
        """Обновление текста и размера шрифта"""
        self.label.text = text
        self.label.font_size = font_size
        # Убедимся, что текст видимый
        self.label.color = (0, 0, 0, 1)
        self.label.disabled_color = (0, 0, 0, 1)

    def _update_text_size(self, instance, size):
        """Центрирование текста"""
        instance.text_size = size