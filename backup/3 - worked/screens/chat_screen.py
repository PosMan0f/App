from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle

from chats.chat_logic import ChatLogic
from logining.database import Database  # Используем Database вместо db_manager
from logining.session_manager import session_manager
from ui_style import palette, scale_dp, scale_font


class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "messages"

        # Инициализируем логику чата
        self.logic = ChatLogic(self)

        # Создаем Database экземпляр
        self.users_db = Database()

        # Верхняя панель
        top_panel = BoxLayout(size_hint_y=None, height=scale_dp(50))
        with top_panel.canvas.before:
            Color(*palette['surface_alt'])
            self._top_rect = Rectangle(pos=top_panel.pos, size=top_panel.size)
        top_panel.bind(pos=self._update_top_rect, size=self._update_top_rect)

        self.title_label = Label(text='Чаты', font_size=scale_font(20), color=palette['text_primary'])
        new_chat_btn = Button(
            text='+ Новый чат',
            size_hint_x=0.3,
            background_color=palette['accent'],
            color=palette['text_primary'],
            font_size=scale_font(14),
            on_press=lambda x: self.logic.show_new_chat()
        )
        top_panel.add_widget(self.title_label)
        top_panel.add_widget(new_chat_btn)

        # Добавляем виджеты на экран
        main_layout = BoxLayout(orientation='vertical')
        main_layout.add_widget(top_panel)
        main_layout.add_widget(self.logic.main_layout)

        self.add_widget(main_layout)

    def _update_top_rect(self, instance, value):
        if hasattr(self, '_top_rect'):
            self._top_rect.pos = instance.pos
            self._top_rect.size = instance.size

    def on_enter(self, *args):
        """При входе на экран"""
        super().on_enter(*args)

        # Получаем текущего пользователя из сессии
        current_user = session_manager.get_current_user()

        if current_user:
            print(f"ChatScreen: User from session - UID: {current_user.get('uid')}")
            self.logic.set_current_user(current_user)
            self.logic.on_enter()
        else:
            print("ChatScreen: No user in session")
            self.logic.show_not_authorized_message()

    def on_leave(self, *args):
        """При уходе с экрана"""
        super().on_leave(*args)
        self.logic.on_leave()
