# applications/tabs.py
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import threading

from applications.ui import TaskCard
from ui_style import palette, scale_dp, scale_font


class BaseTasksTab(TabbedPanelItem):
    """Базовая вкладка задач с поддержкой обновления"""

    def __init__(self, task_manager=None, auto_refresher=None, **kwargs):
        super().__init__(**kwargs)
        self.task_manager = task_manager
        self.auto_refresher = auto_refresher
        self.is_loading = False
        self.last_refresh_time = 0

        # Основной контейнер
        self.content = BoxLayout(orientation='vertical')

        # Контейнер для контента
        self.content_container = BoxLayout(orientation='vertical')
        self.content.add_widget(self.content_container)

        # Фон
        with self.content_container.canvas.before:
            Color(*palette['surface_alt'])
            self.bg_rect = Rectangle(
                pos=self.content_container.pos,
                size=self.content_container.size
            )
        self.content_container.bind(
            pos=self._update_bg,
            size=self._update_bg
        )

    def _update_bg(self, *args):
        self.bg_rect.pos = self.content_container.pos
        self.bg_rect.size = self.content_container.size

    def refresh(self, force: bool = False):
        """Обновление данных (переопределить)"""
        pass

    def safe_refresh(self):
        """Безопасное обновление (предотвращает множественные вызовы)"""
        if self.is_loading:
            print(f"⏳ {self.text}: уже обновляется, пропускаем...")
            return

        current_time = Clock.get_time()
        if current_time - self.last_refresh_time < 1:  # Не чаще 1 раза в секунду
            print(f"⏳ {self.text}: слишком часто, пропускаем...")
            return

        self.last_refresh_time = current_time
        self.refresh(force=True)

    def show_loading(self):
        """Показать индикатор загрузки"""
        if self.is_loading:
            return

        self.is_loading = True
        self.content_container.clear_widgets()

        loading_layout = BoxLayout(orientation='vertical', padding=scale_dp(20))

        loading_label = Label(
            text='Загрузка...',
            color=palette['text_muted'],
            font_size=scale_font(18)
        )

        loading_layout.add_widget(loading_label)
        self.content_container.add_widget(loading_layout)

    def hide_loading(self):
        """Скрыть индикатор загрузки"""
        self.is_loading = False

    def show_empty(self, message="Нет данных"):
        """Показать сообщение об отсутствии данных"""
        self.hide_loading()
        self.content_container.clear_widgets()

        empty_label = Label(
            text=message,
            color=palette['text_muted'],
            font_size=scale_font(16),
            halign='center',
            valign='middle'
        )
        empty_label.bind(size=empty_label.setter('text_size'))
        self.content_container.add_widget(empty_label)

    def show_tasks(self, tasks):
        """Показать список задач"""
        self.hide_loading()
        self.content_container.clear_widgets()

        if not tasks:
            self.show_empty("Нет задач для отображения")
            return

        # Создаем прокручиваемый контейнер
        scroll_view = ScrollView(do_scroll_x=False)
        tasks_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=scale_dp(5),
            padding=[scale_dp(10), scale_dp(10), scale_dp(10), scale_dp(10)]
        )
        tasks_layout.bind(minimum_height=tasks_layout.setter('height'))

        for task in tasks:
            card = self.create_task_card(task)
            tasks_layout.add_widget(card)

        tasks_layout.height = len(tasks) * scale_dp(110)
        scroll_view.add_widget(tasks_layout)
        self.content_container.add_widget(scroll_view)

    def create_task_card(self, task):
        """Создать карточку задачи (переопределить)"""
        return Label(text=f"Задача: {task.get('id', '?')}")

    def show_error(self, message="Ошибка загрузки"):
        """Показать сообщение об ошибке"""
        self.hide_loading()
        self.content_container.clear_widgets()

        error_layout = BoxLayout(orientation='vertical', spacing=scale_dp(10), padding=scale_dp(20))

        error_label = Label(
            text=message,
            color=palette['danger'],
            font_size=scale_font(16),
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))

        retry_btn = Button(
            text='Повторить',
            size_hint_y=None,
            height=scale_dp(40),
            background_color=palette['accent'],
            color=palette['text_primary'],
            font_size=scale_font(14),
            on_press=lambda x: self.safe_refresh()
        )

        error_layout.add_widget(error_label)
        error_layout.add_widget(retry_btn)
        self.content_container.add_widget(error_layout)

    def show_message(self, title, text, duration=2):
        """Показать всплывающее сообщение"""
        Clock.schedule_once(lambda dt: self._show_popup(title, text, duration))

    def _show_popup(self, title, text, duration):
        popup = Popup(
            title=title,
            content=Label(text=text, halign='center'),
            size_hint=(0.7, 0.3),
            auto_dismiss=True
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), duration)

    def view_task(self, task_id):
        """Просмотр деталей задачи (базовая реализация)"""
        print(f"👁 Просмотр задачи {task_id}")
        self.show_message("Просмотр задачи", f"Детали задачи #{task_id}")

    def accept_task(self, task_id):
        """Принятие задачи (базовая реализация)"""
        print(f"✅ Принятие задачи {task_id}")
        self.show_message("Принятие", f"Задача #{task_id} принята")

    def complete_task(self, task_id):
        """Завершение задачи (базовая реализация)"""
        print(f"🏁 Завершение задачи {task_id}")
        self.show_message("Завершение", f"Задача #{task_id} завершена")


class AllTasksTab(BaseTasksTab):
    """Вкладка "Все задачи" с динамическим обновлением"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_department = None
        self.available_departments = ['IT-отдел', 'Юридический отдел', 'HR-отдел']
        self.setup_ui()
        Clock.schedule_once(lambda dt: self.refresh(), 0.5)

    def setup_ui(self):
        """Настройка UI"""
        # Кнопка обновления
        self.header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=scale_dp(40),
            padding=[scale_dp(10), 0, scale_dp(10), 0]
        )

        self.department_spinner = Spinner(
            text='Выберите отдел',
            values=self.available_departments,
            size_hint_x=0.7,
            height=scale_dp(34),
            background_color=palette['surface_alt'],
            color=palette['text_primary'],
            font_size=scale_font(14)
        )
        self.department_spinner.bind(text=self._on_department_changed)

        refresh_btn = Button(
            text='🔄 Обновить',
            size_hint_x=0.3,
            background_color=palette['accent'],
            color=palette['text_primary'],
            font_size=scale_font(14),
            on_press=lambda x: self.safe_refresh()
        )

        self.header_layout.add_widget(self.department_spinner)
        self.header_layout.add_widget(refresh_btn)
        self.header_layout.add_widget(Label())  # Заполнитель

        self.content.add_widget(self.header_layout)

    def _on_department_changed(self, instance, value):
        self.selected_department = value if value != 'Выберите отдел' else None
        self.safe_refresh()

    def _ensure_department_selected(self):
        """Выбираем отдел из профиля пользователя, если он есть"""
        if self.selected_department or not self.task_manager:
            return

        user = self.task_manager.current_user
        if not user:
            return

        department = (user.get('department') or '').strip()
        if not department:
            return

        if department not in self.available_departments:
            self.available_departments.append(department)
            self.department_spinner.values = self.available_departments

        self.selected_department = department
        self.department_spinner.text = department

    def refresh(self, force: bool = False):
        """Загрузка и отображение всех задач"""
        print(f"🔄 Обновление 'Все задачи' (force={force})...")

        if not self.task_manager:
            self.show_empty("Нет подключения к менеджеру задач")
            return

        # Автоподстановка отдела из профиля
        self._ensure_department_selected()

        if not self.selected_department:
            self.show_empty("Выберите отдел, чтобы увидеть задачи")
            return

        self.show_loading()

        def load_tasks():
            try:
                tasks = self.task_manager.get_all_tasks(
                    force_refresh=force,
                    department=self.selected_department
                )
                Clock.schedule_once(lambda dt: self._display_tasks(tasks))
            except Exception as e:
                print(f"❌ Ошибка при загрузке задач: {e}")
                Clock.schedule_once(lambda dt: self.show_error(f"Ошибка: {str(e)}"))

        threading.Thread(target=load_tasks, daemon=True).start()

    def _display_tasks(self, tasks):
        """Отображение задач"""
        print(f"📊 Отображение {len(tasks)} задач")

        if not tasks:
            self.show_empty("Нет доступных задач")
            return

        self.show_tasks(tasks)

    def create_task_card(self, task):
        """Создать карточку задачи"""
        is_assigned = task.get('is_assigned', 0) == 1

        return TaskCard(
            task_data=task,
            show_accept=not is_assigned,
            on_accept=self.accept_task,
            on_view=self.view_task  # Теперь этот метод есть в базовом классе
        )

    def accept_task(self, task_id):
        """Принятие задачи"""
        print(f"🎯 Принятие задачи {task_id}")

        if not self.task_manager:
            return

        def assign_task():
            try:
                success = self.task_manager.assign_task(task_id)
                Clock.schedule_once(lambda dt: self._on_task_assigned(success, task_id))
            except Exception as e:
                print(f"❌ Ошибка при принятии задачи: {e}")
                Clock.schedule_once(lambda dt: self.show_message("Ошибка", f"Не удалось принять задачу: {str(e)}"))

        threading.Thread(target=assign_task, daemon=True).start()

    def _on_task_assigned(self, success, task_id):
        """Обработка результата назначения задачи"""
        if success:
            self.show_message("Успех", "Задача успешно принята!", 1.5)
            # Автоматически обновляем через 0.5 секунды
            Clock.schedule_once(lambda dt: self.safe_refresh(), 0.5)
        else:
            self.show_message("Ошибка", "Не удалось принять задачу", 2)

    def view_task(self, task_id):
        """Просмотр деталей задачи"""
        print(f"👁 Подробнее о задаче {task_id}")

        if not self.task_manager:
            self.show_message("Ошибка", "Нет подключения к менеджеру задач")
            return

        def load_task_details():
            try:
                task_details = self.task_manager.get_task_details(task_id)
                Clock.schedule_once(lambda dt: self._show_task_details(task_details, task_id))
            except Exception as e:
                print(f"❌ Ошибка при загрузке деталей задачи: {e}")
                Clock.schedule_once(lambda dt: self.show_message("Ошибка", f"Не удалось загрузить детали: {str(e)}"))

        threading.Thread(target=load_task_details, daemon=True).start()

    def _show_task_details(self, task_details, task_id):
        """Показать детали задачи"""
        if not task_details:
            self.show_message("Ошибка", f"Задача #{task_id} не найдена")
            return

        from kivy.uix.modalview import ModalView

        modal = ModalView(size_hint=(0.8, 0.8))
        layout = BoxLayout(orientation='vertical', padding=scale_dp(20), spacing=scale_dp(10))

        # Заголовок
        layout.add_widget(Label(
            text=task_details.get('title', 'Без названия'),
            font_size=scale_font(20),
            bold=True,
            color=palette['text_primary'],
            size_hint_y=None,
            height=scale_dp(40)
        ))

        # Отдел и статус
        info_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=scale_dp(30))
        info_layout.add_widget(Label(
            text=f"Отдел: {task_details.get('department', 'Не указан')}",
            color=palette['text_muted'],
            font_size=scale_font(14)
        ))
        info_layout.add_widget(Label(
            text=f"Статус: {task_details.get('status', 'new')}",
            color=palette['text_muted'],
            font_size=scale_font(14)
        ))
        layout.add_widget(info_layout)

        # Срок
        layout.add_widget(Label(
            text=f"Дней на выполнение: {task_details.get('days', 0)}",
            color=palette['text_muted'],
            font_size=scale_font(14),
            size_hint_y=None,
            height=scale_dp(25)
        ))

        # Описание
        from kivy.uix.scrollview import ScrollView as KivyScrollView
        scroll = KivyScrollView()
        desc_label = Label(
            text=task_details.get('description', 'Нет описания'),
            color=palette['text_primary'],
            font_size=scale_font(14),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        desc_label.bind(
            texture_size=lambda instance, value: setattr(desc_label, 'height', desc_label.texture_size[1])
        )
        scroll.add_widget(desc_label)
        layout.add_widget(scroll)

        # Кнопка закрытия
        close_btn = Button(
            text='Закрыть',
            size_hint_y=None,
            height=scale_dp(50),
            background_color=palette['danger'],
            color=palette['text_primary'],
            font_size=scale_font(16),
            on_press=modal.dismiss
        )
        layout.add_widget(close_btn)

        modal.add_widget(layout)
        modal.open()


class MyTasksTab(BaseTasksTab):
    """Вкладка "Мои задачи" с динамическим обновлением"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()
        Clock.schedule_once(lambda dt: self.refresh(), 0.5)

    def setup_ui(self):
        """Настройка UI"""
        # Кнопка обновления
        self.header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=scale_dp(40),
            padding=[scale_dp(10), 0, scale_dp(10), 0]
        )

        refresh_btn = Button(
            text='🔄 Обновить',
            size_hint_x=0.3,
            background_color=palette['accent'],
            color=palette['text_primary'],
            font_size=scale_font(14),
            on_press=lambda x: self.safe_refresh()
        )

        self.header_layout.add_widget(refresh_btn)
        self.header_layout.add_widget(Label())  # Заполнитель

        self.content.add_widget(self.header_layout)

    def refresh(self, force: bool = False):
        """Загрузка задач пользователя"""
        print(f"🔄 Обновление 'Мои задачи' (force={force})...")

        if not self.task_manager or not self.task_manager.current_user:
            self.show_empty("Войдите в систему для просмотра ваших задач")
            return

        self.show_loading()

        def load_tasks():
            try:
                tasks = self.task_manager.get_user_tasks(force_refresh=force)
                Clock.schedule_once(lambda dt: self._display_tasks(tasks))
            except Exception as e:
                print(f"❌ Ошибка при загрузке задач пользователя: {e}")
                Clock.schedule_once(lambda dt: self.show_error(f"Ошибка: {str(e)}"))

        threading.Thread(target=load_tasks, daemon=True).start()

    def _display_tasks(self, tasks):
        """Отображение задач пользователя"""
        print(f"📊 Отображение {len(tasks)} моих задач")

        if not tasks:
            self.show_empty("У вас нет принятых задач")
            return

        self.show_tasks(tasks)

    def create_task_card(self, task):
        """Создать карточку задачи пользователя"""
        return TaskCard(
            task_data=task,
            show_accept=False,
            show_complete=True,
            on_view=self.view_task,
            on_complete=self.complete_task
        )

    def complete_task(self, task_id):
        """Завершение задачи"""
        print(f"✅ Завершение задачи {task_id}")

        if not self.task_manager:
            return

        def complete():
            try:
                success = self.task_manager.complete_task(task_id)
                Clock.schedule_once(lambda dt: self._on_task_completed(success, task_id))
            except Exception as e:
                print(f"❌ Ошибка при завершении задачи: {e}")
                Clock.schedule_once(lambda dt: self.show_message("Ошибка", f"Не удалось завершить задачу: {str(e)}"))

        threading.Thread(target=complete, daemon=True).start()

    def _on_task_completed(self, success, task_id):
        """Обработка результата завершения задачи"""
        if success:
            self.show_message("Успех", "Задача завершена!", 1.5)
            # Автоматически обновляем через 0.5 секунды
            Clock.schedule_once(lambda dt: self.safe_refresh(), 0.5)
        else:
            self.show_message("Ошибка", "Не удалось завершить задачу", 2)
