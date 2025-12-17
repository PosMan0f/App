from color_block import ColorBlock

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.anchorlayout import AnchorLayout

#import os
#import sys
#sys.path.append(os.path.join(os.path.dirname(__file__), '../game'))
#from game.game_2048 import Game2048
from kivy.clock import Clock
from ui_style import palette, scale_font

from game.game_2048 import Game2048

class DefaultScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "default"
        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса экрана default"""
        # Добавляем ColorBlock как фон
        self.add_widget(ColorBlock(color=palette['background']))

        # Создаем layout для центрирования сообщения
        message_layout = AnchorLayout(anchor_x='center', anchor_y='center')

        # Создаем метку для сообщения (изначально невидима)
        self.message_label = Label(
            text="Гусь\nсвинье\nне друг",
            font_size=scale_font(24),
            color=palette['text_primary'],
            size_hint=(None, None),
            opacity=0,  # Начальная прозрачность 0
            halign='center',  # Горизонтальное выравнивание по центру
            valign='middle',
            bold=True,
            outline_width=2,  # Толщина обводки/тени
            outline_color=(0, 0, 0, 1)
        )
        message_layout.add_widget(self.message_label)
        self.add_widget(message_layout)

        self.enter_game(self)

    def show_message(self):
        """Показать сообщение с анимацией"""
        # Сбрасываем прозрачность на всякий случай
        self.message_label.opacity = 0

        # Анимация появления
        anim_in = Animation(opacity=1, duration=0.5)
        # Анимация исчезновения после задержки
        anim_out = Animation(opacity=0, duration=0.5)

        # Последовательная анимация: появление -> задержка -> исчезновение
        anim_sequence = anim_in + Animation(duration=2) + anim_out
        anim_sequence.start(self.message_label)

    def enter_game(self, *args):
        """Запуск игры 2048"""
        # Скрываем сообщение если оно было показано
        self.message_label.opacity = 0

        # Очищаем экран от предыдущих виджетов (кроме фона)
        for widget in self.children[:]:
            if not isinstance(widget, ColorBlock):
                self.remove_widget(widget)

        # Создаем контейнер для центрирования
        center_layout = AnchorLayout(anchor_x='center', anchor_y='center')

        # Создаем и добавляем игру 2048 с фиксированным размером
        self.game_2048 = Game2048(size_hint=(0.8, 0.8))
        center_layout.add_widget(self.game_2048)

        self.add_widget(center_layout)

        # СРАЗУ ПРИВЯЗАТЬ КЛАВИАТУРУ ПОСЛЕ ДОБАВЛЕНИЯ
        Clock.schedule_once(lambda dt: self.game_2048.bind_keyboard(), 0.2)
