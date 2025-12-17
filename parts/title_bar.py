from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.graphics import Color, Rectangle

import ctypes
import win32api
import win32con
import win32gui

from ui_style import palette, scale_dp


class TitleBar(BoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        padding = scale_dp(5)
        self.padding = [padding, 0, padding, 0]

        # Размер кнопок (можно настроить под ваш дизайн)
        self.btn_size = scale_dp(32)

        with self.canvas.before:
            Color(*palette['surface'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        self.setup_ui()
        self.setup_drag()

        self._drag_pos = None
        self.bind(on_touch_down=self.start_move)

    def _update_rect(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def setup_ui(self):
        """Создание интерфейса заголовка"""
        # Левая часть: иконка приложения
        self.setup_left_section()

        # Центральная часть: пустое пространство для перетаскивания
        self.add_widget(Widget(size_hint_x=1))

        # Правая часть: кнопки управления окном
        self.setup_right_section()

    def setup_left_section(self):
        """Левая секция с иконкой приложения"""
        icon_anchor = AnchorLayout(
            size_hint=(None, 1),
            width=self.btn_size,
            anchor_x='center',
            anchor_y='center'
        )

        self.icon_btn = Button(
            size_hint=(None, None),
            width=self.btn_size,
            height=self.btn_size,
            background_normal="images/icon.png",
            background_down="images/icon.png",
            border=(0, 0, 0, 0)
        )

        self.icon_btn.bind(on_release=self.on_logo_click)

        icon_anchor.add_widget(self.icon_btn)
        self.add_widget(icon_anchor)

    def setup_right_section(self):
        """Правая секция с кнопками управления"""
        buttons_anchor = AnchorLayout(
            size_hint=(None, 1),
            width=self.btn_size * 2 + scale_dp(5),
            anchor_x='right',
            anchor_y='center'
        )

        buttons_box = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            width=self.btn_size * 2 + scale_dp(5),
            height=self.btn_size,
            spacing=scale_dp(5)
        )

        # Кнопка "Свернуть"
        self.min_btn = Button(
            size_hint=(None, None),
            width=self.btn_size,
            height=self.btn_size,
            background_normal="images/collapse.png",
            background_down="images/collapse.png"
        )
        self.min_btn.bind(on_release=self.minimize_window)
        buttons_box.add_widget(self.min_btn)

        # Кнопка "Закрыть"
        self.close_btn = Button(
            size_hint=(None, None),
            width=self.btn_size,
            height=self.btn_size,
            background_normal="images/close.png",
            background_down="images/close.png"
        )
        self.close_btn.bind(on_release=self.close_app)
        buttons_box.add_widget(self.close_btn)

        buttons_anchor.add_widget(buttons_box)
        self.add_widget(buttons_anchor)

    def setup_drag(self):
        """Настройка перетаскивания окна"""
        self._drag_pos = None

    def start_move(self, instance, touch):
        # Игнорируем клик по кнопкам
        if self.min_btn.collide_point(*touch.pos) or self.close_btn.collide_point(*touch.pos):
            return False
        if self.icon_btn.collide_point(*touch.pos):
            return False

        if self.collide_point(*touch.pos) and touch.button == 'left':
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            win32gui.ReleaseCapture()
            win32api.PostMessage(hwnd, win32con.WM_NCLBUTTONDOWN, win32con.HTCAPTION, 0)
            return True

    def minimize_window(self, instance):
        """Свернуть окно"""
        Window.minimize()

    def close_app(self, instance):
        """Закрыть приложение"""
        App.get_running_app().stop()

    def on_logo_click(self, instance):
        """Обработчик клика по логотипу"""
        if self.screen_manager:
            # Переключаемся на экран default
            self.screen_manager.current = "default"

            # Получаем экран default и показываем сообщение
            default_screen = self.screen_manager.get_screen("default")
            if hasattr(default_screen, 'show_message'):
                default_screen.show_message()

        # Снимаем выделение с кнопок в нижней панели через MainLayout
        if hasattr(self, 'parent') and self.parent:
            # Ищем MainLayout в иерархии
            parent = self.parent
            while parent and not hasattr(parent, 'clear_bottom_panel_selection'):
                parent = parent.parent

            if parent and hasattr(parent, 'clear_bottom_panel_selection'):
                parent.clear_bottom_panel_selection()

    def set_screen_manager(self, screen_manager):
        """Установка screen_manager для навигации"""
        self.screen_manager = screen_manager
