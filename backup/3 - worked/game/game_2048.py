from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button

from random import choice, random
import numpy as np

#import os
#import sys
#sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import  *
from .bordered_button import BorderedButton
from .game_button import GameButton
from kivy.clock import Clock

class Game2048(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = None
        self.keyboard_bind_id = None
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10

        # Заголовок
        self.title_label = Label(
            text="2048",
            size_hint=(1, 0.1),
            font_size=f'{int(win_width/16)}sp',
            color=(0,0,0,1),
            bold=True,
            halign='center',  # Центрирование по горизонтали
            valign='middle',  # Центрирование по вертикали
            text_size=(None, None),
            outline_width=2,  # Толщина обводки/тени
            outline_color=(1, 1, 1, 1)  # Займет всю доступную область
        )
        self.add_widget(self.title_label)

        # Игровое поле
        self.game_layout = BoxLayout(orientation='vertical', size_hint=(1,1))
        self.grid = GridLayout(cols=4, spacing=5, size_hint=(1, 1))
        self.game_layout.add_widget(self.grid)

        # Контейнер для центрирования кнопки
        button_container = AnchorLayout(
            size_hint=(1, 0.1),
            anchor_x='center',
            anchor_y='center'
        )

        # Кнопка с фиксированной шириной
        self.restart_btn = BorderedButton(
            text="Новая игра",
            size_hint=(0.6, 1)
        )
        self.restart_btn.bind(on_press=self.restart_game)

        button_container.add_widget(self.restart_btn)
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
        self.add_random_tile()
        self.add_random_tile()
        self.update_display()
        self.title_label.text = "2048\nСчет: 0"  # Убедись что это есть

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

    def move(self, direction):
        """Выполнить ход в указанном направлении"""
        # Создаем копию доски для проверки изменений
        old_board = self.board.copy()

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
            self.add_random_tile()
            self.update_display()
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
            # Есть пустые клетки - игра точно не окончена
            self.title_label.text = f"2048\nСчет: {self.score}"
            return False

        # Проверяем возможны ли объединения по горизонтали и вертикали
        for i in range(4):
            for j in range(4):
                current = self.board[i][j]
                # Проверка соседа справа
                if j < 3 and current == self.board[i][j + 1]:
                    self.title_label.text = f"2048\nСчет: {self.score}"
                    return False
                # Проверка соседа снизу
                if i < 3 and current == self.board[i + 1][j]:
                    self.title_label.text = f"2048\nСчет: {self.score}"
                    return False

        # Если дошли сюда - игра действительно окончена
        self.title_label.text = f"ИГРА ОКОНЧЕНА!\nСчет: {self.score}"
        return True

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