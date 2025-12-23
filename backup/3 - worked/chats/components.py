from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from datetime import datetime


class ChatBubble(BoxLayout):
    def __init__(self, message, is_own=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.height = dp(60)
        self.padding = [dp(10), dp(5)]

        self.message_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(200), dp(50))
        )

        self.message_label = Label(
            text=message.get('text', ''),
            size_hint_y=0.7,
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1) if is_own else (0, 0, 0, 1)
        )
        self.message_label.bind(size=self.message_label.setter('text_size'))

        time_text = self._format_time(message.get('timestamp', ''))
        self.time_label = Label(
            text=time_text,
            size_hint_y=0.3,
            font_size=dp(10),
            color=(0.8, 0.8, 0.8, 1),
            halign='right'
        )
        self.time_label.bind(size=self.time_label.setter('text_size'))

        self.message_layout.add_widget(self.message_label)
        self.message_layout.add_widget(self.time_label)

        if is_own:
            self.add_widget(BoxLayout(size_hint_x=1))
            self.add_widget(self.message_layout)
            self.message_layout.canvas.before.clear()
            with self.message_layout.canvas.before:
                Color(0.2, 0.6, 1, 1)
                RoundedRectangle(
                    pos=self.message_layout.pos,
                    size=self.message_layout.size,
                    radius=[dp(10), dp(10), dp(2), dp(10)]
                )
        else:
            self.add_widget(self.message_layout)
            self.add_widget(BoxLayout(size_hint_x=1))
            self.message_layout.canvas.before.clear()
            with self.message_layout.canvas.before:
                Color(0.9, 0.9, 0.9, 1)
                RoundedRectangle(
                    pos=self.message_layout.pos,
                    size=self.message_layout.size,
                    radius=[dp(10), dp(10), dp(10), dp(2)]
                )

    def _format_time(self, timestamp):
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime('%H:%M')
        except:
            return timestamp


class ChatItem(ButtonBehavior, BoxLayout):
    def __init__(self, chat_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)

        self.chat_data = chat_data

        avatar_layout = RelativeLayout(size_hint=(None, 1), width=dp(50))
        with avatar_layout.canvas:
            Color(0.2, 0.6, 1, 1)
            RoundedRectangle(
                pos=(dp(5), dp(5)),
                size=(dp(40), dp(40)),
                radius=[dp(20), dp(20), dp(20), dp(20)]
            )

        avatar_text = chat_data.get('name', '?')[0].upper()
        avatar_label = Label(
            text=avatar_text,
            pos=(dp(25), dp(25)),
            size_hint=(None, None),
            color=(1, 1, 1, 1),
            font_size=dp(18)
        )
        avatar_layout.add_widget(avatar_label)

        info_layout = BoxLayout(orientation='vertical')
        name_label = Label(
            text=chat_data.get('name', 'Unknown'),
            size_hint_y=0.5,
            halign='left',
            valign='middle',
            color=(1, 1, 1, 1),
            font_size=dp(16),
            bold=True
        )
        name_label.bind(size=name_label.setter('text_size'))

        last_msg = chat_data.get('last_message', '')
        if len(last_msg) > 40:
            last_msg = last_msg[:37] + '...'

        last_msg_label = Label(
            text=last_msg,
            size_hint_y=0.5,
            halign='left',
            valign='middle',
            color=(0.8, 0.8, 0.8, 1),
            font_size=dp(14)
        )
        last_msg_label.bind(size=last_msg_label.setter('text_size'))

        time_label = Label(
            text=self._format_time(chat_data.get('last_message_time', '')),
            size_hint=(None, 1),
            width=dp(60),
            halign='right',
            valign='top',
            color=(0.6, 0.6, 0.6, 1),
            font_size=dp(12)
        )
        time_label.bind(size=time_label.setter('text_size'))

        main_info = BoxLayout(orientation='horizontal')
        main_info.add_widget(info_layout)
        main_info.add_widget(time_label)

        info_layout.add_widget(name_label)
        info_layout.add_widget(last_msg_label)

        self.add_widget(avatar_layout)
        self.add_widget(main_info)

        with self.canvas.before:
            Color(0.3, 0.3, 0.3, 0.1)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _format_time(self, timestamp):
        try:
            dt = datetime.fromisoformat(timestamp)
            now = datetime.now()

            if dt.date() == now.date():
                return dt.strftime('%H:%M')
            elif (now.date() - dt.date()).days == 1:
                return 'вчера'
            else:
                return dt.strftime('%d.%m')
        except:
            return ''


class NewChatPopup(Popup):
    def __init__(self, on_user_selected, current_uid, db_manager, chats_db, **kwargs):  # Заменили users_db на db_manager
        super().__init__(**kwargs)
        self.title = 'Новый чат'
        self.size_hint = (0.9, 0.8)
        self.on_user_selected = on_user_selected
        self.current_uid = current_uid
        self.db_manager = db_manager  # Сохраняем db_manager
        self.chats_db = chats_db

        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        self.search_input = TextInput(
            hint_text='Поиск по UID или email...',
            multiline=False,
            size_hint_x=0.8
        )
        search_btn = Button(
            text='Найти',
            size_hint_x=0.2,
            on_press=self.search_users
        )
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        layout.add_widget(search_layout)

        self.results_scroll = ScrollView()
        self.results_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.results_scroll.add_widget(self.results_layout)
        layout.add_widget(self.results_scroll)

        self.content = layout

    def search_users(self, instance):
        self.results_layout.clear_widgets()
        search_term = self.search_input.text.strip()

        if not search_term:
            return

        try:
            # Используем поиск из базы данных пользователей
            users = self.db_manager.search_users(search_term, self.current_uid)

            if not users:
                self.results_layout.add_widget(Label(
                    text='Пользователи не найдены',
                    size_hint_y=None,
                    height=dp(40),
                    color=(0.8, 0.8, 0.8, 1)
                ))
                return

            for user in users:
                user_item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(60),
                    padding=dp(10)
                )

                info_layout = BoxLayout(orientation='vertical')
                name_label = Label(
                    text=user['name'],
                    halign='left',
                    color=(1, 1, 1, 1)
                )
                name_label.bind(size=name_label.setter('text_size'))

                uid_label = Label(
                    text=f"UID: {user['uid']}",
                    halign='left',
                    color=(0.8, 0.8, 0.8, 1),
                    font_size=dp(12)
                )
                uid_label.bind(size=uid_label.setter('text_size'))

                info_layout.add_widget(name_label)
                info_layout.add_widget(uid_label)

                select_btn = Button(
                    text='Написать',
                    size_hint_x=0.3,
                    on_press=lambda x, u=user: self.select_user(u)
                )

                user_item.add_widget(info_layout)
                user_item.add_widget(select_btn)
                self.results_layout.add_widget(user_item)

        except Exception as e:
            print(f"Error searching users: {e}")
            self.results_layout.add_widget(Label(
                text=f'Ошибка поиска: {str(e)}',
                size_hint_y=None,
                height=dp(40),
                color=(1, 0, 0, 1)
            ))

    def select_user(self, user):
        self.dismiss()
        self.on_user_selected(user)