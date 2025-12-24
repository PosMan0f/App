# send/request_form.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from send.ui_components import *
from ui_style import palette, scale_dp, scale_font


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

        # Уведомление статуса
        self.notice_bar = None
        self.notice_event = None

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
        self._clear_notice()
        base_color = palette['danger'] if is_error else palette['success']
        self.notice_bar = BoxLayout(
            size_hint_y=None,
            height=scale_dp(42),
            padding=[scale_dp(12), scale_dp(8)]
        )
        with self.notice_bar.canvas.before:
            Color(*base_color)
            bg = RoundedRectangle(pos=self.notice_bar.pos, size=self.notice_bar.size,
                                  radius=[scale_dp(10)] * 4)
        self.notice_bar.bind(
            pos=lambda *args: setattr(bg, 'pos', self.notice_bar.pos),
            size=lambda *args: setattr(bg, 'size', self.notice_bar.size)
        )
        notice_label = FieldLabel(
            text=message,
            color=palette['text_primary'],
            font_size=scale_font(14),
            halign='center',
            valign='middle'
        )
        notice_label.bind(size=notice_label.setter('text_size'))
        self.notice_bar.add_widget(notice_label)
        self.add_widget(self.notice_bar)
        from kivy.clock import Clock
        self.notice_event = Clock.schedule_once(self._hide_status, 3)

    def _hide_status(self, dt):
        """Скрыть статус"""
        if self.notice_event:
            from kivy.clock import Clock
            Clock.unschedule(self.notice_event)
            self.notice_event = None
        if self.notice_bar and self.notice_bar.parent:
            self.remove_widget(self.notice_bar)
        self.notice_bar = None

    def _clear_notice(self):
        if self.notice_event:
            from kivy.clock import Clock
            Clock.unschedule(self.notice_event)
            self.notice_event = None
        if self.notice_bar and self.notice_bar.parent:
            self.remove_widget(self.notice_bar)
        self.notice_bar = None
