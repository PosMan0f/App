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
        self.height = scale_dp(105)
        self.padding = scale_dp(8)
        self.spacing = scale_dp(4)

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
        title_row = BoxLayout(size_hint_y=None, height=scale_dp(25))
        title_label = Label(
            text=task_data['title'][:30] + ('...' if len(task_data['title']) > 30 else ''),
            color=palette['text_primary'],
            font_size=scale_font(15),
            bold=True,
            halign='left',
            size_hint_x=0.7
        )
        title_label.bind(size=title_label.setter('text_size'))

        dept_label = Label(
            text=task_data['department'][:15],
            color=palette['text_muted'],
            font_size=scale_font(13),
            size_hint_x=0.3,
            halign='right'
        )
        dept_label.bind(size=dept_label.setter('text_size'))

        title_row.add_widget(title_label)
        title_row.add_widget(dept_label)
        self.add_widget(title_row)

        # Описание
        desc_text = task_data['description']
        if len(desc_text) > 60:
            desc_text = desc_text[:57] + '...'

        desc_label = Label(
            text=desc_text,
            color=palette['text_muted'],
            font_size=scale_font(13),
            size_hint_y=None,
            height=scale_dp(35),
            halign='left'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        self.add_widget(desc_label)

        # Информация и кнопки
        info_row = BoxLayout(size_hint_y=None, height=scale_dp(30), spacing=scale_dp(5))

        # Дни
        days_label = Label(
            text=f"📅 {task_data['days']} дн.",
            color=palette['text_primary'],
            font_size=scale_font(12),
            size_hint_x=0.4
        )
        info_row.add_widget(days_label)

        # Кнопки
        buttons_layout = BoxLayout(size_hint_x=0.6, spacing=scale_dp(3))

        # Кнопка "Подробнее"
        view_btn = Button(
            text='👁',
            size_hint_x=0.3,
            background_color=palette['accent'],
            color=palette['text_primary'],
            font_size=scale_font(12)
        )
        view_btn.bind(on_press=lambda x: self._on_view())
        buttons_layout.add_widget(view_btn)

        # Кнопка "Принять" или "Завершить"
        if show_accept:
            accept_btn = Button(
                text='✅',
                size_hint_x=0.3,
                background_color=palette['success'],
                color=palette['text_primary'],
                font_size=scale_font(12)
            )
            accept_btn.bind(on_press=lambda x: self._on_accept())
            buttons_layout.add_widget(accept_btn)
        elif show_complete:
            complete_btn = Button(
                text='🏁',
                size_hint_x=0.3,
                background_color=palette['danger'],
                color=palette['text_primary'],
                font_size=scale_font(12)
            )
            complete_btn.bind(on_press=lambda x: self._on_complete())
            buttons_layout.add_widget(complete_btn)

        # Заполнитель
        buttons_layout.add_widget(Label())

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
