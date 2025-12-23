from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Color, Rectangle
from square_button import SquareButton
from ui_style import palette, scale_dp

class BottomPanel(BoxLayout):
    screen_manager = ObjectProperty(None)
    button_size = NumericProperty(50)
    current_active = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.button_size = scale_dp(50)
        self.create_panel()
        self.bind(size=self.update_button_size)
        self.update_button_size()

    def create_panel(self):
        # Создаем затемненный фон
        with self.canvas.before:
            Color(*palette['surface_alt'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg_rect, size=self.update_bg_rect)

        # Создаем AnchorLayout для центрирования кнопок
        anchor_layout = AnchorLayout(
            anchor_x='center',
            anchor_y='center',
            size_hint=(1, 1)
        )

        # Создаем контейнер для кнопок
        self.buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            spacing=scale_dp(20)  # Расстояние между кнопками
        )

        # Создаем кнопки используя SquareButton
        buttons_data = [
            {
                "tab_name": "messages",
                "background_normal": 'images/msg.png',
                "background_down": 'images/msg.png'
            },
            {
                "tab_name": "send_request",
                "background_normal": 'images/send_request.png',
                "background_down": 'images/send_request.png'
            },
            {
                "tab_name": "applications",
                "background_normal": 'images/applications.png',
                "background_down": 'images/applications.png'
            },
            {
                "tab_name": "profile",
                "background_normal": 'images/profile.png',
                "background_down": 'images/profile.png'
            }
        ]

        for btn_data in buttons_data:
            button = SquareButton(
                tab_name=btn_data["tab_name"],
                background_normal=btn_data["background_normal"],
                background_down=btn_data["background_down"],
                size_hint=(None, None),
            )
            # Привязываем обработчик события on_release
            button.bind(on_release=lambda instance, tab=btn_data["tab_name"]: self.set_active_tab(instance, tab))
            self.buttons_layout.add_widget(button)

        anchor_layout.add_widget(self.buttons_layout)
        self.add_widget(anchor_layout)

    def update_bg_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_button_size(self, *args):
        if self.width > 0:
            # Рассчитываем доступную ширину с учетом расстояний между кнопками
            available_width = self.width - (self.buttons_layout.spacing * 3)
            # Делим на 5 чтобы кнопки были немного меньше чем доступное пространство
            new_button_size = max(available_width / 4.5, scale_dp(40))

            if new_button_size != self.button_size:
                self.button_size = new_button_size
                self.update_buttons_size()

    def update_buttons_size(self):
        # Обновляем размер всех кнопок
        for button in self.buttons_layout.children:
            button.size = (self.button_size, self.button_size)

        # Обновляем размер контейнера кнопок
        total_width = (self.button_size * 4) + (self.buttons_layout.spacing * 3)
        self.buttons_layout.size = (total_width, self.button_size)

    def set_active_tab(self, button, tab_name):
        # Снимаем выделение с предыдущей активной кнопки
        if self.current_active:
            self.current_active.is_active = False
            self.current_active.progress = 0  # Сбрасываем анимацию

        # Устанавливаем выделение на текущую кнопку
        button.is_active = True
        button.animate_border()  # Запускаем анимацию обводки
        self.current_active = button

        # Переключаем экран если screen_manager установлен
        if self.screen_manager:
            self.screen_manager.current = tab_name

        #print(f"Активирована вкладка: {tab_name}")

    def set_screen_manager(self, screen_manager):
        """Устанавливает screen_manager для навигации"""
        self.screen_manager = screen_manager

    def clear_selection(self):
        """Снимает выделение со всех кнопок"""
        if self.current_active:
            self.current_active.is_active = False
            self.current_active.progress = 0  # Сбрасываем анимацию
            self.current_active = None
