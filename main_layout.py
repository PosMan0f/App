from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.graphics import Rectangle, Color
from kivy.core.window import Window
from kivy.clock import Clock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'screens'))

from screens.color_block import ColorBlock
from screens.default_screen import DefaultScreen
from screens.chat_screen import ChatScreen
from screens.send_screen import SendScreen
from screens.applications_screen import ApplicationsScreen
from screens.profile_screen import ProfileScreen

sys.path.append(os.path.join(os.path.dirname(__file__), 'parts'))
from parts.title_bar import TitleBar
from parts.bottom_panel import BottomPanel
from ui_style import palette


class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        self.setup_window()

        # Добавляем фон до создания остального UI
        self.setup_background()
        self.setup_ui()

    # ДОБАВИТЬ этот метод:
    def setup_window(self):
        Window.clearcolor = palette['background']
        Clock.schedule_once(self.create_rounded_corners, 0.1)

    # ДОБАВИТЬ этот метод:
    def create_rounded_corners(self, dt):
        try:
            # Получаем HWND для SDL окна
            import ctypes
            from ctypes import wintypes

            # Получаем HWND через SDL
            hwnd = ctypes.windll.user32.GetActiveWindow()

            if hwnd:
                corner_radius = 15
                region = ctypes.windll.gdi32.CreateRoundRectRgn(
                    0, 0,
                    int(Window.width), int(Window.height),
                    corner_radius, corner_radius
                )
                ctypes.windll.user32.SetWindowRgn(hwnd, region, True)
            else:
                print("Не удалось получить HWND окна")

        except Exception as e:
            print(f"Не удалось создать скругленные углы: {e}")

    def setup_background(self):
        """Установка фона для всего layout"""
        with self.canvas.before:
            Color(*palette['background'])
            # Создаем прямоугольник с фоновым изображением
            self.bg_rect = Rectangle(
                pos=self.pos,
                size=self.size
            )

        # Привязываем обновление позиции и размера фона
        self.bind(pos=self._update_bg_rect, size=self._update_bg_rect)

    def _update_bg_rect(self, instance, value):
        """Обновление позиции и размера фона при изменении layout"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def setup_ui(self):
        blocks = {
            "top_panel": 0.07,
            "line1": 0.01,
            "main_area": 0.75,
            "line2": 0.01,
            "bottom_panel": 0.16
        }

        # Инициализируем screen_manager
        self.screen_manager = ScreenManager(size_hint_y=blocks["main_area"])

        # Верхняя панель с TitleBar
        self.title_bar = TitleBar(size_hint_y=blocks["top_panel"])
        self.title_bar.set_screen_manager(self.screen_manager)

        # Основная часть с ScreenManager
        self.setup_screens()

        # Нижняя панель с кнопками навигации
        self.bottom_panel = BottomPanel(size_hint_y=blocks["bottom_panel"])
        # Устанавливаем screen_manager для навигации
        self.bottom_panel.set_screen_manager(self.screen_manager)
        # Устанавливаем обработчик нажатия на кнопки
        self.bottom_panel.on_tab_pressed = self.on_tab_pressed

        # Добавляем на экран все модули
        self.add_widget(self.title_bar)

        # Разделитель
        self.add_widget(ColorBlock(color=palette['surface_alt'], size_hint_y=blocks["line1"]))

        self.add_widget(self.screen_manager)

        # Разделитель
        self.add_widget(ColorBlock(color=palette['surface_alt'], size_hint_y=blocks["line2"]))

        self.add_widget(self.bottom_panel)



    def setup_screens(self):
        """Добавляем все экраны в ScreenManager"""
        self.screen_manager.add_widget(DefaultScreen())
        self.screen_manager.add_widget(ChatScreen())
        self.screen_manager.add_widget(SendScreen())
        self.screen_manager.add_widget(ApplicationsScreen())
        self.screen_manager.add_widget(ProfileScreen())
        print(self.screen_manager.screen_names)

        # Устанавливаем начальный экран
        self.screen_manager.current = "default"

    def on_tab_pressed(self, tab_name):
        """Обработка нажатия на кнопку в нижней панели"""
        self.screen_manager.current = tab_name

    def switch_screen(self, screen_name):
        """Метод для смены экрана"""
        if screen_name in self.screen_manager.screen_names:
            self.screen_manager.current = screen_name

    def get_current_screen(self):
        """Получить имя текущего экрана"""
        return self.screen_manager.current

    def clear_bottom_panel_selection(self):
        """Снимает выделение с кнопок в нижней панели"""
        if hasattr(self, 'bottom_panel'):
            self.bottom_panel.clear_selection()
