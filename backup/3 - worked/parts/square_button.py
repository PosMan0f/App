from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.graphics import Color, Line

class SquareButton(Button):
    progress = NumericProperty(0)  # 0..1 заполнение
    tab_name = StringProperty('')
    is_active = BooleanProperty(False)

    def __init__(self, **kwargs):
        # Убираем переопределение background_normal и background_down
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        # Убираем эти строки, чтобы не перезаписывать переданные свойства
        # self.background_normal = ''
        # self.background_down = ''
        self.color = (0, 0, 0, 0)  # Прозрачный текст

        self.border = (2, 2, 2, 2) if self.is_active else (0, 0, 0, 0)

        self.bind(
            pos=self.update_canvas,
            size=self.update_canvas,
            progress=self.update_canvas,
            is_active=self.update_canvas
        )

        # Создаем canvas для обводки
        with self.canvas.after:
            self.border_color = Color(0, 0, 0, 0)
            # Левая линия
            self.left_line = Line(width=2)
            # Верхняя линия
            self.top_line = Line(width=2)
            # Правая линия
            self.right_line = Line(width=2)
            # Нижняя линия
            self.bottom_line = Line(width=2)

    def update_canvas(self, *args):
        if not self.is_active:
            self.border_color.rgba = (0, 0, 0, 0)
            # Очищаем линии когда кнопка не активна
            self.left_line.points = []
            self.top_line.points = []
            self.right_line.points = []
            self.bottom_line.points = []
            return

        self.border_color.rgba = (0, 0, 0, 1)

        # Левая сторона
        progress_left = min(1, self.progress * 4)
        self.left_line.points = [
            self.x, self.y,
            self.x, self.y + self.height * progress_left
        ]

        # Верхняя сторона
        progress_top = min(1, max(0, (self.progress - 0.25) * 1.33))
        self.top_line.points = [
            self.x, self.y + self.height,
                    self.x + self.width * progress_top, self.y + self.height
        ]

        # Правая сторона
        progress_right = min(1, max(0, (self.progress - 0.5) * 2))
        self.right_line.points = [
            self.x + self.width, self.y + self.height,
            self.x + self.width, self.y + self.height * (1 - progress_right)
        ]

        # Нижняя сторона
        progress_bottom = min(1, max(0, (self.progress - 0.75) * 4))
        self.bottom_line.points = [
            self.x + self.width, self.y,
            self.x + self.width * (1 - progress_bottom), self.y
        ]

    def animate_border(self):
        self.progress = 0
        anim = Animation(progress=1, duration=0.5)
        anim.start(self)

    def on_release(self):
        self.animate_border()