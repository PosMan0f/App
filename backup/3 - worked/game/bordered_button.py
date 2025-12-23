from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Line


class BorderedButton(BoxLayout):
    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.padding = 2  # Отступ для обводки

        # Создаем обводку вокруг всего BoxLayout
        with self.canvas.before:
            Color(0.55, 0.27, 0.07, 0)  # Коричневый
            self.border = Line(width=2)

        # Создаем кнопку с прозрачным фоном
        self.button = Button(
            text=text,
            size_hint=(1, 1),
            background_color=(0, 0, 0, 0),
            color=(0, 0, 0, 1),
            bold=True,
            halign='center',  # Центрирование по горизонтали
            valign='middle',  # Центрирование по вертикали
            text_size=(None, None),
            outline_width=2,  # Толщина обводки/тени
            outline_color=(1, 1, 1, 1)
        )

        self.add_widget(self.button)
        self.bind(pos=self.update_border, size=self.update_border)

    def update_border(self, *args):
        """Обновить обводку"""
        self.border.rectangle = (self.x, self.y, self.width, self.height)

    def bind(self, **kwargs):
        """Перенаправляем события на кнопку"""
        self.button.bind(**kwargs)

    @property
    def text(self):
        return self.button.text

    @text.setter
    def text(self, value):
        self.button.text = value