# applications/ui.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from ui_style import palette, scale_dp, scale_font


class TaskCard(BoxLayout):
    """Карточка задачи"""

    def __init__(self, task_data, show_accept=True, show_complete=False,
                 on_accept=None, on_view=None, on_complete=None, **kwargs):
        super().__init__(**kwargs)
        self.task_data = task_data
        self.on_accept = on_accept
        self.on_view = on_view
        self.on_complete = on_complete

        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = scale_dp(8)
        self.spacing = scale_dp(4)
        self.bind(minimum_height=self.setter('height'))

        # Фон карточки
        with self.canvas.before:
            status = task_data.get('status', 'new')
            if status == 'completed':
                Color(*palette['success'])
            elif status == 'assigned':
                Color(*palette['accent_muted'])
            else:
                Color(*palette['surface_alt'])

            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[scale_dp(8), ]
            )

        self.bind(pos=self._update_bg, size=self._update_bg)

        # Заголовок
        title_row = BoxLayout(size_hint_y=None)
        title_row.bind(minimum_height=title_row.setter('height'))

        title_label = Label(
            text=task_data.get('title', ''),
            color=palette['text_primary'],
            font_size=scale_font(39),
            bold=True,
            halign='left',
            valign='top',
            size_hint_x=0.7,
            size_hint_y=None
        )
        title_label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', max(value[1], scale_dp(50)))
        )

        dept_label = Label(
            text=task_data['department'][:15],
            color=palette['text_muted'],
            font_size=scale_font(26),
            size_hint_x=0.3,
            halign='right',
            valign='top',
            size_hint_y=None
        )
        dept_label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', max(value[1], scale_dp(28)))
        )

        title_row.add_widget(title_label)
        title_row.add_widget(dept_label)
        self.add_widget(title_row)

        # Описание
        desc_label = Label(
            text=task_data.get('description', ''),
            color=palette['text_muted'],
            font_size=scale_font(26),
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        desc_label.bind(
            width=lambda instance, value: setattr(instance, 'text_size', (value, None)),
            texture_size=lambda instance, value: setattr(instance, 'height', max(value[1], scale_dp(40)))
        )
        self.add_widget(desc_label)

        # Информация и кнопки
        info_row = BoxLayout(size_hint_y=None, height=scale_dp(30), spacing=scale_dp(5))

        # Дни
        days_label = Label(
            text=f"Дней на выполнение: {task_data['days']}",
            color=palette['text_primary'],
            font_size=scale_font(24),
            size_hint_x=0.4,
            halign='left'
        )
        days_label.bind(size=days_label.setter('text_size'))
        info_row.add_widget(days_label)

        # Кнопки
        buttons_layout = BoxLayout(size_hint_x=0.6, spacing=scale_dp(8))

        # Кнопка "Подробнее"
        view_btn = Button(
            text='Подробнее',
            size_hint_x=0.45,
            background_color=palette['accent'],
            background_normal='',
            background_down='',
            color=palette['text_primary'],
            font_size=scale_font(24)
        )
        view_btn.bind(on_press=lambda x: self._on_view())
        buttons_layout.add_widget(view_btn)

        # Кнопка "Принять" или "Завершить"
        if show_accept:
            accept_btn = Button(
                text='Принять',
                size_hint_x=0.45,
                background_color=palette['success'],
                background_normal='',
                background_down='',
                color=palette['text_primary'],
                font_size=scale_font(24)
            )
            accept_btn.bind(on_press=lambda x: self._on_accept())
            buttons_layout.add_widget(accept_btn)
        elif show_complete:
            complete_btn = Button(
                text='Завершить',
                size_hint_x=0.3,
                background_color=palette['danger'],
                background_normal='',
                background_down='',
                color=palette['text_primary'],
                font_size=scale_font(24)
            )
            complete_btn.bind(on_press=lambda x: self._on_complete())
            buttons_layout.add_widget(complete_btn)

        # Заполнитель
        buttons_layout.add_widget(Label(size_hint_x=0.1))

        info_row.add_widget(buttons_layout)
        self.add_widget(info_row)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _on_view(self):
        if self.on_view:
            self.on_view(self.task_data['id'])

    def _on_accept(self):
        if self.on_accept:
            self.on_accept(self.task_data['id'])

    def _on_complete(self):
        if self.on_complete:
            self.on_complete(self.task_data['id'])
