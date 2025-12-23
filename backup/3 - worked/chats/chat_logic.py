from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.metrics import dp

from .components import ChatBubble, ChatItem, NewChatPopup
from .chat_manager import ChatManager


class ChatLogic:
    def __init__(self, screen):
        self.screen = screen
        self.chat_manager = ChatManager()
        self.db_manager = None
        self.current_chat_id = None

        self.main_layout = BoxLayout(orientation='vertical')
        self.content_container = BoxLayout(orientation='vertical')

        self.main_layout.add_widget(self.content_container)

    def set_db_manager(self, db_manager):
        """Устанавливает менеджер базы данных"""
        self.db_manager = db_manager

    def set_current_user(self, user):
        self.chat_manager.set_current_user(user)

    def on_enter(self):
        self.load_chats()
        # Используем Clock для обновления
        self._schedule_updates()

    def _schedule_updates(self):
        """Планирует обновления чатов"""
        # Отменяем предыдущие обновления
        self._unschedule_updates()

        # Планируем новые
        if not self.current_chat_id:
            self.update_chats_event = Clock.schedule_interval(self.update_chats, 5)
        else:
            self.update_messages_event = Clock.schedule_interval(self.update_messages, 2)

    def _unschedule_updates(self):
        """Отменяет запланированные обновления"""
        if hasattr(self, 'update_chats_event'):
            Clock.unschedule(self.update_chats_event)
        if hasattr(self, 'update_messages_event'):
            Clock.unschedule(self.update_messages_event)

    def on_leave(self):
        self._unschedule_updates()

    def load_chats(self):
        """Загружает список чатов"""
        self.content_container.clear_widgets()

        if not self.chat_manager.current_user:
            self.show_not_authorized_message()
            return

        chats_scroll = ScrollView()
        chats_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        chats_layout.bind(minimum_height=chats_layout.setter('height'))
        chats_scroll.add_widget(chats_layout)

        chats = self.chat_manager.get_user_chats()

        if not chats:
            chats_layout.add_widget(Label(
                text='У вас пока нет чатов.\nНажмите "+ Новый чат" чтобы начать общение.',
                size_hint_y=None,
                height=dp(100),
                halign='center',
                valign='middle',
                color=(0.8, 0.8, 0.8, 1)
            ))
            chats_layout.height = dp(100)
        else:
            for chat_data in chats:
                other_uid = chat_data['other_uid']
                user_info = self.db_manager.get_user_by_uid(other_uid) if self.db_manager else None

                if user_info:
                    name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
                    if not name:
                        name = user_info.get('email', 'Unknown')
                    chat_data['name'] = name
                    chat_data['other_user_info'] = user_info
                else:
                    chat_data['name'] = f"UID: {other_uid}"

                # Создаем элемент чата
                from .components import ChatItem
                chat_item = ChatItem(chat_data)

                # ПРИВЯЗЫВАЕМ ОБРАБОТЧИК ПРАВИЛЬНО
                def create_handler(chat_data_copy):
                    return lambda x: self.open_chat(chat_data_copy)

                chat_item.bind(on_press=create_handler(chat_data))
                chats_layout.add_widget(chat_item)

            chats_layout.height = len(chats) * dp(85)

        self.content_container.add_widget(chats_scroll)

    def show_new_chat(self):
        """Показывает попап для создания нового чата"""
        if not self.chat_manager.current_user:
            print("ERROR: No current user in chat manager!")
            self.show_message('Ошибка', 'Для создания чата необходимо войти в аккаунт')
            return

        try:
            # Передаем Database экземпляр вместо db_manager
            from logining.database import Database
            users_db = Database()

            popup = NewChatPopup(
                on_user_selected=self.start_chat,
                current_uid=self.chat_manager.current_user['uid'],
                db_manager=users_db,  # Изменено: было users_db, стало db_manager
                chats_db=self.chat_manager.chats_db
            )
            popup.open()
        except Exception as e:
            print(f"ERROR opening popup: {e}")
            import traceback
            traceback.print_exc()

    def show_message(self, title, text):
        """Показывает сообщение"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label

        popup = Popup(
            title=title,
            content=Label(text=text),
            size_hint=(0.6, 0.3)
        )
        popup.open()

    def start_chat(self, user):
        chat_id = self.chat_manager.create_chat(user['uid'])
        if chat_id:
            self.open_chat_by_id(chat_id, user)

    def open_chat(self, chat_data):
        self.open_chat_by_id(chat_data['chat_id'], chat_data.get('other_user_info'))

    def open_chat_by_id(self, chat_id, other_user_info=None):
        self.current_chat_id = chat_id
        self.content_container.clear_widgets()

        chat_top = BoxLayout(size_hint_y=None, height=dp(50))
        back_btn = Button(
            text='← Назад',
            size_hint_x=0.2,
            on_press=lambda x: self.show_chat_list()
        )

        if other_user_info:
            name = f"{other_user_info.get('first_name', '')} {other_user_info.get('last_name', '')}".strip()
            if not name:
                name = other_user_info.get('email', 'Unknown')
        else:
            name = 'Собеседник'

        name_label = Label(text=name, font_size=dp(18), color=(1, 1, 1, 1))

        chat_top.add_widget(back_btn)
        chat_top.add_widget(name_label)

        self.messages_scroll = ScrollView()
        self.messages_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        self.messages_layout.bind(minimum_height=self.messages_layout.setter('height'))
        self.messages_scroll.add_widget(self.messages_layout)

        input_panel = BoxLayout(size_hint_y=None, height=dp(50))
        self.message_input = TextInput(
            hint_text='Введите сообщение...',
            multiline=False,
            size_hint_x=0.8
        )
        send_btn = Button(
            text='Отправить',
            size_hint_x=0.2,
            background_color=(0.2, 0.6, 1, 1),
            on_press=self.send_message
        )

        input_panel.add_widget(self.message_input)
        input_panel.add_widget(send_btn)

        self.content_container.add_widget(chat_top)
        self.content_container.add_widget(self.messages_scroll)
        self.content_container.add_widget(input_panel)

        self.load_messages()
        self._schedule_updates()

    def load_messages(self):
        if not self.current_chat_id:
            return

        self.messages_layout.clear_widgets()
        messages = self.chat_manager.get_chat_messages(self.current_chat_id)

        for message in messages:
            is_own = message['sender_uid'] == self.chat_manager.current_user['uid']
            bubble = ChatBubble(message, is_own)
            self.messages_layout.add_widget(bubble)

        self.messages_layout.height = len(messages) * dp(65)
        Clock.schedule_once(lambda dt: setattr(self.messages_scroll, 'scroll_y', 0))

    def send_message(self, instance):
        if not self.current_chat_id or not self.message_input.text.strip():
            return

        self.chat_manager.send_message(self.current_chat_id, self.message_input.text.strip())
        self.message_input.text = ''
        self.load_messages()

    def show_chat_list(self):
        self.current_chat_id = None
        self._schedule_updates()
        self.load_chats()

    def update_chats(self, dt):
        if not self.current_chat_id:
            self.load_chats()

    def update_messages(self, dt):
        if self.current_chat_id:
            self.load_messages()

    def show_not_authorized_message(self):
        """Показывает сообщение о необходимости авторизации"""
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout

        self.content_container.clear_widgets()

        message_layout = BoxLayout(orientation='vertical')
        message_label = Label(
            text='Для использования чатов необходимо войти в аккаунт\n\nПерейдите в профиль для входа',
            size_hint_y=None,
            height=200,
            halign='center',
            valign='middle',
            color=(0.8, 0.8, 0.8, 1),
            font_size=20
        )
        message_label.bind(size=message_label.setter('text_size'))

        message_layout.add_widget(message_label)
        self.content_container.add_widget(message_layout)