from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle

from random import choice, random
import numpy as np

#import os
#import sys
#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .game_button import GameButton
from kivy.clock import Clock
from ui_style import palette, scale_dp, scale_font

class Game2048(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = None
        self.keyboard_bind_id = None
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        self.last_board = None
        self.last_score = 0
        self.display_board = None

        # Верхняя панель: вернуть ход и счет
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=scale_dp(56),
            spacing=scale_dp(10),
            padding=[scale_dp(8), scale_dp(6)]
        )

        self.undo_container = BoxLayout(padding=[scale_dp(8), scale_dp(6)])
        with self.undo_container.canvas.before:
            Color(*palette['surface_alt'])
            self._undo_bg = RoundedRectangle(pos=self.undo_container.pos, size=self.undo_container.size,
                                             radius=[scale_dp(12)] * 4)
        self.undo_container.bind(
            pos=lambda *args: setattr(self._undo_bg, 'pos', self.undo_container.pos),
            size=lambda *args: setattr(self._undo_bg, 'size', self.undo_container.size)
        )

        self.undo_btn = Button(
            text='Вернуть ход',
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=palette['text_primary'],
            font_size=scale_font(16)
        )
        self.undo_btn.bind(on_press=self.undo_move)
        self.undo_container.add_widget(self.undo_btn)

        self.score_container = BoxLayout(padding=[scale_dp(8), scale_dp(6)])
        with self.score_container.canvas.before:
            Color(*palette['accent'])
            self._score_bg = RoundedRectangle(pos=self.score_container.pos, size=self.score_container.size,
                                              radius=[scale_dp(12)] * 4)
        self.score_container.bind(
            pos=lambda *args: setattr(self._score_bg, 'pos', self.score_container.pos),
            size=lambda *args: setattr(self._score_bg, 'size', self.score_container.size)
        )

        self.score_label = Label(
            text='Счет: 0',
            color=palette['text_primary'],
            font_size=scale_font(16),
            bold=True,
            halign='center',
            valign='middle'
        )
        self.score_label.bind(size=self.score_label.setter('text_size'))
        self.score_container.add_widget(self.score_label)

        header.add_widget(self.undo_container)
        header.add_widget(self.score_container)
        self.add_widget(header)

        # Игровое поле
        self.game_layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            spacing=scale_dp(12)
        )
        self.grid = GridLayout(cols=4, spacing=5, size_hint=(1, 1))
        self.game_layout.add_widget(self.grid)

        # Контейнер для центрирования кнопки
        button_container = AnchorLayout(
            size_hint=(1, None),
            height=scale_dp(56),
            anchor_x='center',
            anchor_y='center'
        )

        self.restart_container = BoxLayout(
            size_hint=(0.8, 1),
            padding=[scale_dp(8), scale_dp(6)]
        )
        with self.restart_container.canvas.before:
            Color(*palette['surface_alt'])
            self._restart_bg = RoundedRectangle(pos=self.restart_container.pos, size=self.restart_container.size,
                                                radius=[scale_dp(12)] * 4)
        self.restart_container.bind(
            pos=lambda *args: setattr(self._restart_bg, 'pos', self.restart_container.pos),
            size=lambda *args: setattr(self._restart_bg, 'size', self.restart_container.size)
        )

        self.restart_btn = Button(
            text="Новая игра",
            size_hint=(1, 1),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),
            color=palette['text_primary'],
            font_size=scale_font(16),
            bold=True
        )
        self.restart_btn.bind(on_press=self.restart_game)

        self.restart_container.add_widget(self.restart_btn)
        button_container.add_widget(self.restart_container)
        self.game_layout.add_widget(button_container)

        self.add_widget(self.game_layout)

        # Инициализация игры
        self.board = np.zeros((4, 4), dtype=int)
        self.cells = []
        self.score = 0
        self.init_ui()
        self.restart_game()

        # Привязка клавиатуры
        Clock.schedule_once(self.bind_keyboard, 0.1)

    def init_ui(self):
        """Инициализация игрового интерфейса"""
        self.grid.clear_widgets()
        self.cells = []

        for i in range(4):
            for j in range(4):
                # Используем обычную кнопку вместо GameButton
                cell = GameButton(
                    text="",
                    #disabled=True
                )
                self.grid.add_widget(cell)
                self.cells.append(cell)

    def update_cell_appearance(self, cell, value):
        if value == 0:
            color = (0.8, 0.8, 0.8, 0.6)
            text = ""
        else:
            # Вычисляем уровень (логарифм по основанию 2)
            level = int(np.log2(value))
            # Чем выше уровень, тем "краснее" и "насыщеннее" цвет
            # Формула подобрана эмпирически под реальные тона
            r = 0.93 - min(level, 11) * 0.015
            g = 0.89 - min(level, 11) * 0.055
            b = 0.85 - min(level, 11) * 0.09

            # Небольшая коррекция, чтобы цвета не уходили в черноту
            r = max(0.23, r)
            g = max(0.18, g)
            b = max(0.18, b)

            color = (r, g, b, 0.6)
            text = str(value)

        # print(color)

        cell.set_color(color)

        # Настраиваем шрифт
        if value >= 1000:
            font = '18sp'
        elif value >= 100:
            font = '20sp'
        else:
            font = '24sp'

        # Устанавливаем белую обводку/тень для текста
        cell.label.outline_color = (1, 1, 1, 1)  # Белый цвет
        cell.label.outline_width = 2  # Толщина обводки

        cell.set_text(text, font)

    def restart_game(self, instance=None):
        """Начать новую игру"""
        self.board = np.zeros((4, 4), dtype=int)
        self.score = 0
        self.last_board = None
        self.last_score = 0
        self.undo_btn.disabled = True
        self.add_random_tile()
        self.add_random_tile()
        self.update_display()
        self.update_score_label()

    def add_random_tile(self):
        """Добавить случайную плитку (2 или 4) в случайную пустую ячейку"""
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.board[i][j] == 0]
        if empty_cells:
            i, j = choice(empty_cells)
            self.board[i][j] = 2 if random() < 0.9 else 4

    def update_display(self):
        """Обновить отображение игрового поля"""
        for i in range(4):
            for j in range(4):
                index = i * 4 + j
                self.update_cell_appearance(self.cells[index], self.board[i][j])
                if self.display_board is None or self.display_board[i][j] != self.board[i][j]:
                    self.cells[index].animate_value_change()
        self.display_board = self.board.copy()

    def update_score_label(self):
        self.score_label.text = f'Счет: {self.score}'
        Animation.cancel_all(self.score_label)
        self.score_label.opacity = 0.6
        Animation(opacity=1, duration=0.2).start(self.score_label)
        
    def move(self, direction):
        """Выполнить ход в указанном направлении"""
        # Создаем копию доски для проверки изменений
        old_board = self.board.copy()
        old_score = self.score

        if direction == 'up':
            self.move_up()
        elif direction == 'down':
            self.move_down()
        elif direction == 'left':
            self.move_left()
        elif direction == 'right':
            self.move_right()

        # Если доска изменилась
        if not np.array_equal(old_board, self.board):
            self.last_board = old_board
            self.last_score = old_score
            self.undo_btn.disabled = False
            self.add_random_tile()
            self.update_display()
            self.update_score_label()
            # Проверяем окончание игры
            self.check_game_over()
        else:
            # Если ход не изменил доску, всё равно проверяем
            # Это важно для случаев когда нет возможных ходов
            self.check_game_over()

    def move_left(self):
        """Движение влево"""
        for i in range(4):
            row = self.board[i]
            # Убираем нули
            non_zero = row[row != 0]
            # Объединяем одинаковые
            merged = []
            skip = False
            for j in range(len(non_zero)):
                if skip:
                    skip = False
                    continue
                if j + 1 < len(non_zero) and non_zero[j] == non_zero[j + 1]:
                    merged.append(non_zero[j] * 2)
                    self.score += non_zero[j] * 2
                    skip = True
                else:
                    merged.append(non_zero[j])
            # Заполняем оставшиеся нулями
            merged.extend([0] * (4 - len(merged)))
            self.board[i] = merged

    def move_right(self):
        """Движение вправо"""
        for i in range(4):
            row = self.board[i]
            # Убираем нули
            non_zero = row[row != 0]
            # Объединяем одинаковые справа налево
            merged = []
            skip = False
            for j in range(len(non_zero) - 1, -1, -1):
                if skip:
                    skip = False
                    continue
                if j - 1 >= 0 and non_zero[j] == non_zero[j - 1]:
                    merged.insert(0, non_zero[j] * 2)
                    self.score += non_zero[j] * 2
                    skip = True
                else:
                    merged.insert(0, non_zero[j])
            # Заполняем начало нулями
            merged = [0] * (4 - len(merged)) + merged
            self.board[i] = merged

    def move_up(self):
        """Движение вверх"""
        self.board = self.board.T
        self.move_left()
        self.board = self.board.T

    def move_down(self):
        """Движение вниз"""
        self.board = self.board.T
        self.move_right()
        self.board = self.board.T

    def check_game_over(self):
        """Проверить условие окончания игры и обновить заголовок если игра окончена"""
        # Проверяем есть ли пустые клетки
        if 0 in self.board:
            return False

        # Проверяем возможны ли объединения по горизонтали и вертикали
        for i in range(4):
            for j in range(4):
                current = self.board[i][j]
                # Проверка соседа справа
                if j < 3 and current == self.board[i][j + 1]:
                    return False
                # Проверка соседа снизу
                if i < 3 and current == self.board[i + 1][j]:
                    return False

        # Если дошли сюда - игра действительно окончена
        return True
    
    def undo_move(self, instance=None):
        """Откатить один ход"""
        if self.last_board is None:
            return
        self.board = self.last_board.copy()
        self.score = self.last_score
        self.last_board = None
        self.last_score = 0
        self.undo_btn.disabled = True
        self.update_display()
        self.update_score_label()

    def bind_keyboard(self, dt=None):
        """Привязать клавиатуру к виджету"""
        # Сначала отвязать если уже привязано
        self.unbind_keyboard()

        # Привязать клавиатуру
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed,
            self
        )
        if self._keyboard:
            self.keyboard_bind_id = self._keyboard.bind(
                on_key_down=self._on_keyboard_down
            )

    def unbind_keyboard(self):
        """Отвязать клавиатуру"""
        if self._keyboard and self.keyboard_bind_id:
            self._keyboard.unbind(on_key_down=self.keyboard_bind_id)
        self._keyboard = None
        self.keyboard_bind_id = None

    def on_parent(self, widget, parent):
        """Вызывается при изменении родительского виджета"""
        if parent:
            # Когда виджет добавляется в дерево виджетов
            Clock.schedule_once(self.bind_keyboard, 0.1)
        else:
            # Когда виджет удаляется из дерева виджетов
            self.unbind_keyboard()

    def _keyboard_closed(self):
        """Закрытие клавиатуры"""
        self.unbind_keyboard()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Обработка нажатий клавиш"""
        key = keycode[1].lower()

        if key == 'w':
            self.move('up')
        elif key == 's':
            self.move('down')
        elif key == 'a':
            self.move('left')
        elif key == 'd':
            self.move('right')
        elif key == 'r':  # Дополнительно: R для рестарта
            self.restart_game()
            return True

        return True
