# send/request_form.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from send.ui_components import *
from ui_style import scale_dp, palette


class RequestForm(BoxLayout):
    """Форма отправки заявки"""

    def __init__(self, on_submit_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_submit_callback = on_submit_callback
        self.orientation = 'vertical'
        self.padding = scale_dp(15)
        self.spacing = scale_dp(10)  # Уменьшенные отступы

        # Заголовок
        self.add_widget(TitleLabel(
            text='Отправка заявки',
            height=scale_dp(35)
        ))

        # Контейнер формы с прокруткой
        scroll_view = ScrollView()
        form_layout = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=scale_dp(8),  # Уменьшенные отступы между элементами
            padding=scale_dp(5)
        )
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Поле выбора отдела
        form_layout.add_widget(FieldLabel(text='Выбор отдела:'))
        self.dept_spinner = DepartmentSpinner()
        form_layout.add_widget(self.dept_spinner)

        # Поле названия задачи
        form_layout.add_widget(FieldLabel(text='Название задачи:'))
        self.title_input = BaseTextInput(hint_text='Введите название задачи')
        form_layout.add_widget(self.title_input)

        # Поле описания задачи
        form_layout.add_widget(FieldLabel(text='Описание задачи:'))
        self.desc_input = MultilineTextInput(hint_text='Введите описание задачи')
        form_layout.add_widget(self.desc_input)

        # Поле количества дней
        form_layout.add_widget(FieldLabel(
            text='Сколько дней на выполнение задачи:'))
        self.days_input = BaseTextInput(
            hint_text='Введите количество дней',
            input_filter='int')
        form_layout.add_widget(self.days_input)

        scroll_view.add_widget(form_layout)
        self.add_widget(scroll_view)

        # Кнопка отправки
        self.submit_button = SubmitButton(text='Отправить задачу')
        self.submit_button.bind(on_press=self._on_submit)
        self.add_widget(self.submit_button)

        # Метка статуса
        self.status_label = StatusLabel()
        self.add_widget(self.status_label)

    def _on_submit(self, instance):
        """Обработка нажатия кнопки отправки"""
        if self.on_submit_callback:
            data = self.get_form_data()
            self.on_submit_callback(data)

    def get_form_data(self):
        """Получение данных из формы"""
        return {
            'department': self.dept_spinner.text,
            'title': self.title_input.text.strip(),
            'description': self.desc_input.text.strip(),
            'days': self.days_input.text.strip()
        }

    def clear_form(self):
        """Очистка формы"""
        self.dept_spinner.text = 'Выберите отдел'
        self.title_input.text = ''
        self.desc_input.text = ''
        self.days_input.text = ''

    def show_status(self, message, is_error=False):
        """Показать статус"""
        self.status_label.text = message
        self.status_label.height = scale_dp(35)
        self.status_label.opacity = 1

        if is_error:
            self.status_label.color = palette['danger']  # Красный
        else:
            self.status_label.color = palette['success']  # Зеленый

        # Автоматическое скрытие
        from kivy.clock import Clock
        Clock.schedule_once(self._hide_status, 3)

    def _hide_status(self, dt):
        """Скрыть статус"""
        self.status_label.height = scale_dp(0)
        self.status_label.opacity = 0
