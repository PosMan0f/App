# applications/main_screen.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label

from applications.tabs import AllTasksTab, MyTasksTab
from applications.task_manager import TaskManager
from applications.auto_refresher import AutoRefresher
from ui_style import palette, scale_dp, scale_font


class ApplicationsMainScreen(BoxLayout):
    """Главный экран приложений с динамическим обновлением"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        # Фон
        with self.canvas.before:
            Color(*palette['surface'])
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Менеджер задач
        self.task_manager = TaskManager()

        # Автообновление
        self.auto_refresher = AutoRefresher(self.task_manager)
        self.auto_refresher.set_ui_callback(self._trigger_tab_refresh)

        # Создаем вкладки
        self.create_tabs()

        # Панель управления
        self.create_control_panel()

        # Запускаем проверку пользователя
        Clock.schedule_once(lambda dt: self.check_user(), 1)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def create_tabs(self):
        """Создание панели с вкладками"""
        self.tab_panel = TabbedPanel(
            do_default_tab=False,
            tab_width=scale_dp(120),
            background_color=palette['surface_alt'],
            size_hint=(1, 1)
        )

        # Вкладка "Все задачи"
        self.all_tasks_tab = AllTasksTab(
            text='Все задачи',
            task_manager=self.task_manager,
            auto_refresher=self.auto_refresher
        )
        self.tab_panel.add_widget(self.all_tasks_tab)

        # Вкладка "Мои задачи"
        self.my_tasks_tab = MyTasksTab(
            text='Мои задачи',
            task_manager=self.task_manager,
            auto_refresher=self.auto_refresher
        )
        self.tab_panel.add_widget(self.my_tasks_tab)

        self.add_widget(self.tab_panel)

    def create_control_panel(self):
        """Создание панели управления"""
        control_panel = BoxLayout(
            size_hint_y=None,
            height=scale_dp(50),
            padding=scale_dp(5),
            spacing=scale_dp(5)
        )

        # Кнопка обновления всех
        refresh_all_btn = Button(
            text='🔄 Обновить все',
            background_color=palette['accent'],
            color=palette['text_primary'],
            font_size=scale_font(14),
            on_press=lambda x: self.refresh_all_tabs()
        )

        # Кнопка автообновления
        self.auto_refresh_btn = Button(
            text='▶ Авто',
            background_color=palette['success'],
            color=palette['text_primary'],
            font_size=scale_font(14),
            on_press=self.toggle_auto_refresh
        )

        # Индикатор пользователя
        self.user_label = Label(
            text='Пользователь: ...',
            color=palette['text_primary'],
            halign='right',
            size_hint_x=0.5,
            font_size=scale_font(14)
        )

        control_panel.add_widget(refresh_all_btn)
        control_panel.add_widget(self.auto_refresh_btn)
        control_panel.add_widget(self.user_label)

        self.add_widget(control_panel)

    def _trigger_tab_refresh(self, tab_type: str):
        """Обработчик обновления вкладок"""
        print(f"🔄 Триггер обновления для: {tab_type}")

        if tab_type == 'all' and hasattr(self, 'all_tasks_tab'):
            Clock.schedule_once(lambda dt: self.all_tasks_tab.safe_refresh(), 0.1)

        elif tab_type == 'user' and hasattr(self, 'my_tasks_tab'):
            Clock.schedule_once(lambda dt: self.my_tasks_tab.safe_refresh(), 0.1)

        elif tab_type == 'both':
            Clock.schedule_once(lambda dt: self.refresh_all_tabs(), 0.1)

    def check_user(self):
        """Проверка и отображение информации о пользователе"""
        if self.task_manager.current_user:
            user = self.task_manager.current_user
            self.user_label.text = f"👤 {user['uid'][:10]}..."
        else:
            self.user_label.text = "👤 Не авторизован"

    def on_enter(self):
        """При входе на экран"""
        print("\n" + "=" * 50)
        print("🚪 ВХОД НА ЭКРАН ЗАДАЧ")
        print("=" * 50)

        # Перезагружаем пользователя
        self.task_manager.load_current_user()
        self.check_user()

        # Обновляем обе вкладки
        if hasattr(self, 'all_tasks_tab'):
            print("🔄 Обновление вкладки 'Все задачи'...")
            self.all_tasks_tab.safe_refresh()

        if hasattr(self, 'my_tasks_tab'):
            print("🔄 Обновление вкладки 'Мои задачи'...")
            self.my_tasks_tab.safe_refresh()

        # Запускаем автообновление
        self.start_auto_refresh()

    def on_leave(self):
        """При выходе с экрана"""
        print("\n" + "=" * 50)
        print("🚪 ВЫХОД С ЭКРАНА ЗАДАЧ")
        print("=" * 50)
        self.stop_auto_refresh()

    def start_auto_refresh(self):
        """Запуск автоматического обновления"""
        self.auto_refresher.start()
        self.auto_refresh_btn.text = '⏹ Авто'
        self.auto_refresh_btn.background_color = palette['danger']
        print("✅ Автообновление запущено")

    def stop_auto_refresh(self):
        """Остановка автоматического обновления"""
        self.auto_refresher.stop()
        self.auto_refresh_btn.text = '▶ Авто'
        self.auto_refresh_btn.background_color = palette['success']
        print("⏹ Автообновление остановлено")

    def toggle_auto_refresh(self, instance=None):
        """Переключение автообновления"""
        if self.auto_refresher.is_active:
            self.stop_auto_refresh()
        else:
            self.start_auto_refresh()

    def refresh_all_tabs(self, instance=None):
        """Обновление всех вкладок"""
        print("🔄 Ручное обновление всех вкладок...")

        if hasattr(self, 'all_tasks_tab'):
            self.all_tasks_tab.safe_refresh()

        if hasattr(self, 'my_tasks_tab'):
            self.my_tasks_tab.safe_refresh()
