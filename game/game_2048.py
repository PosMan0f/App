from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle

from random import choice, random
import numpy as np

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
        self.grid_container = FloatLayout(size_hint=(1, 1))
        self.grid = GridLayout(cols=4, spacing=5, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.grid_container.add_widget(self.grid)
        self.animation_layer = FloatLayout(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.grid_container.add_widget(self.animation_layer)
        self.game_layout.add_widget(self.grid_container)
        self.grid.bind(pos=self._sync_animation_layer, size=self._sync_animation_layer)

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
        self.is_animating = False
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
        self.display_board = self.board.copy()

    def update_score_label(self):
        self.score_label.text = f'Счет: {self.score}'
        Animation.cancel_all(self.score_label)
        self.score_label.opacity = 0.6
        Animation(opacity=1, duration=0.2).start(self.score_label)

    def _sync_animation_layer(self, *args):
        self.animation_layer.pos = self.grid.pos
        self.animation_layer.size = self.grid.size

    def _animate_move(self, old_board, new_board, direction):
        moves = self._build_move_map(old_board, direction)
        self.animation_layer.clear_widgets()
        moving_tiles = []

        for move in moves:
            if move["from"] == move["to"]:
                continue
            from_index = move["from"][0] * 4 + move["from"][1]
            to_index = move["to"][0] * 4 + move["to"][1]
            from_cell = self.cells[from_index]
            to_cell = self.cells[to_index]
            tile = GameButton(text="")
            tile.size_hint = (None, None)
            tile.size = from_cell.size
            tile.pos = self.grid.to_parent(*from_cell.pos)
            self.update_cell_appearance(tile, move["value"])
            self.animation_layer.add_widget(tile)
            moving_tiles.append((tile, to_cell))

        if not moving_tiles:
            self._finish_move(new_board)
            return

        self.is_animating = True
        remaining = {"count": len(moving_tiles)}

        def _on_complete(*args):
            remaining["count"] -= 1
            if remaining["count"] <= 0:
                self.animation_layer.clear_widgets()
                self._finish_move(new_board)

        for tile, to_cell in moving_tiles:
            end_pos = self.grid.to_parent(*to_cell.pos)
            anim = Animation(pos=end_pos, duration=0.12, t='out_quad')
            anim.bind(on_complete=_on_complete)
            anim.start(tile)

    def _finish_move(self, new_board):
        self.board = new_board.copy()
        self.add_random_tile()
        self.update_display()
        self.update_score_label()
        self.is_animating = False
        self.check_game_over()

    def _build_move_map(self, board, direction):
        moves = []
        if direction in ("left", "right"):
            for row in range(4):
                line = board[row].tolist()
                moves.extend(self._build_line_moves(line, row, direction))
        else:
            for col in range(4):
                line = board[:, col].tolist()
                moves.extend(self._build_line_moves(line, col, direction, vertical=True))
        return moves

    def _build_line_moves(self, line, fixed_index, direction, vertical=False):
        tiles = [(value, idx) for idx, value in enumerate(line) if value != 0]
        moves = []
        target_index = 0
        index = 0
        while index < len(tiles):
            value, original_idx = tiles[index]
            if index + 1 < len(tiles) and tiles[index + 1][0] == value:
                moves.append(self._format_move(fixed_index, original_idx, target_index, direction, vertical, value))
                moves.append(
                    self._format_move(fixed_index, tiles[index + 1][1], target_index, direction, vertical, value))
                index += 2
            else:
                moves.append(self._format_move(fixed_index, original_idx, target_index, direction, vertical, value))
                index += 1
            target_index += 1
        return moves

    @staticmethod
    def _format_move(fixed_index, from_idx, to_idx, direction, vertical, value):
        if vertical:
            from_pos = (from_idx, fixed_index)
            if direction == "up":
                to_pos = (to_idx, fixed_index)
            else:
                to_pos = (3 - to_idx, fixed_index)
        else:
            from_pos = (fixed_index, from_idx)
            if direction == "left":
                to_pos = (fixed_index, to_idx)
            else:
                to_pos = (fixed_index, 3 - to_idx)
        return {"from": from_pos, "to": to_pos, "value": value}

    def move(self, direction):
        """Выполнить ход в указанном направлении"""
        if self.is_animating:
            return
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
            moved_board = self.board.copy()
            self.last_board = old_board
            self.last_score = old_score
            self.undo_btn.disabled = False
            self._animate_move(old_board, moved_board, direction)
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

    def _get_parent_screen(self):
        parent = self.parent
        while parent:
            if isinstance(parent, Screen):
                return parent
            parent = parent.parent
        return None

    def _is_active_screen(self):
        screen = self._get_parent_screen()
        if not screen:
            return True
        manager = getattr(screen, "manager", None)
        if not manager:
            return True
        current_screen = getattr(manager, "current_screen", None)
        if current_screen is not None:
            return current_screen == screen
        current_name = getattr(manager, "current", None)
        if current_name is not None:
            return current_name == screen.name
        return True

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Обработка нажатий клавиш"""
        if not self._is_active_screen():
            return False
        focused_widget = getattr(Window, "focused_widget", None)
        if focused_widget is None:
            focused_widget = getattr(FocusBehavior, "_focused_widget", None)
        if isinstance(focused_widget, TextInput):
            return False

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
