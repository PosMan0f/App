from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from datetime import datetime
import colorsys
from ui_style import palette, scale_dp, scale_font
from .utils import truncate, LAST_MESSAGE_PREVIEW_LIMIT


class ChatBubble(BoxLayout):
    def __init__(self, message, is_own=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (1, None)
        self.padding = [dp(12), dp(6), dp(12), dp(6)]
        self.spacing = dp(8)

        self.is_own = is_own
        self.bubble_padding = [dp(12), dp(8), dp(12), dp(8)]
        self.max_bubble_width = Window.width * 0.7

        self.message_layout = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            padding=self.bubble_padding,
            spacing=dp(4)
        )

        self.message_label = Label(
            text=message.get('text', ''),
            size_hint_y=None,
            halign='left',
            valign='top',
            color=(1, 1, 1, 1) if is_own else (0.1, 0.1, 0.1, 1)
        )
        self.message_label.bind(texture_size=self._update_message_size)

        time_text = self._format_time(message.get('timestamp', ''))
        self.time_label = Label(
            text=time_text,
            size_hint_y=None,
            font_size=dp(10),
            color=(0.85, 0.85, 0.85, 1) if is_own else (0.5, 0.5, 0.5, 1),
            halign='right' if is_own else 'left',
            valign='bottom'
        )
        self.time_label.bind(texture_size=self._update_time_size)

        self.message_layout.add_widget(self.message_label)
        self.message_layout.add_widget(self.time_label)

        if is_own:
            self.add_widget(BoxLayout(size_hint_x=1))
            self.add_widget(self.message_layout)
        else:
            self.add_widget(self.message_layout)
            self.add_widget(BoxLayout(size_hint_x=1))

        with self.message_layout.canvas.before:
            self._bubble_color = Color(0.2, 0.6, 1, 1) if is_own else Color(0.92, 0.92, 0.92, 1)
            self._bubble_rect = RoundedRectangle(pos=self.message_layout.pos, size=self.message_layout.size,
                                                 radius=[dp(12)] * 4)

        self.message_layout.bind(pos=self._update_bubble_rect, size=self._update_bubble_rect)
        Window.bind(on_resize=self._on_window_resize)
        self._update_text_sizes()

    def _format_time(self, timestamp):
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime('%H:%M')
        except:
            return timestamp

    def _on_window_resize(self, *args):
        self.max_bubble_width = Window.width * 0.7
        self._update_text_sizes()

    def _update_text_sizes(self):
        inner_width = self.max_bubble_width - (self.bubble_padding[0] + self.bubble_padding[2])
        self.message_label.text_size = (inner_width, None)
        self.time_label.text_size = (inner_width, None)

    def _update_message_size(self, instance, size):
        instance.height = size[1]
        self._update_bubble_size()

    def _update_time_size(self, instance, size):
        instance.height = size[1]
        self._update_bubble_size()

    def _update_bubble_size(self):
        max_text_width = max(self.message_label.texture_size[0], self.time_label.texture_size[0])
        width = min(self.max_bubble_width, max_text_width + self.bubble_padding[0] + self.bubble_padding[2])
        self.message_layout.width = width
        self.message_layout.height = (
            self.message_label.texture_size[1]
            + self.time_label.texture_size[1]
            + self.bubble_padding[1]
            + self.bubble_padding[3]
            + dp(4)
        )
        self.height = self.message_layout.height + self.padding[1] + self.padding[3]

    def _update_bubble_rect(self, *args):
        self._bubble_rect.pos = self.message_layout.pos
        self._bubble_rect.size = self.message_layout.size


class ChatItem(ButtonBehavior, BoxLayout):
    def __init__(self, chat_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(84)
        self.padding = [dp(12), dp(10), dp(12), dp(10)]
        self.spacing = dp(12)

        self.chat_data = chat_data

        avatar_layout = RelativeLayout(size_hint=(None, 1), width=dp(52))
        with avatar_layout.canvas:
            Color(*self._get_avatar_color())
            RoundedRectangle(
                pos=(dp(6), dp(10)),
                size=(dp(40), dp(40)),
                radius=[dp(12)] * 4
            )

        avatar_text = self._get_avatar_letter()
        avatar_label = Label(
            text=avatar_text,
            pos=(dp(6), dp(10)),
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            color=(1, 1, 1, 1),
            font_size=dp(18),
            halign='center',
            valign='middle'
        )
        avatar_label.bind(size=avatar_label.setter('text_size'))
        avatar_layout.add_widget(avatar_label)

        info_layout = BoxLayout(orientation='vertical', spacing=dp(4))
        name_label = Label(
            text=chat_data.get('name', 'Unknown'),
            size_hint_y=None,
            height=dp(22),
            halign='left',
            valign='center',
            color=(0.95, 0.95, 0.95, 1),
            font_size=dp(16),
            bold=True,
            shorten=True,
            shorten_from='right'
        )
        name_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

        last_msg = truncate(chat_data.get('last_message', ''), LAST_MESSAGE_PREVIEW_LIMIT)

        last_msg_label = Label(
            text=last_msg,
            size_hint_y=None,
            height=dp(20),
            halign='left',
            valign='center',
            color=(0.8, 0.8, 0.8, 1),
            font_size=dp(14),
            shorten=True,
            shorten_from='right'
        )
        last_msg_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

        time_label = Label(
            text=self._format_time(chat_data.get('last_message_time', '')),
            size_hint=(None, None),
            width=dp(64),
            height=dp(18),
            halign='right',
            valign='middle',
            color=(0.6, 0.6, 0.6, 1),
            font_size=dp(12)
        )
        time_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))

        main_info = BoxLayout(orientation='horizontal')
        main_info.add_widget(info_layout)
        main_info.add_widget(time_label)

        info_layout.add_widget(name_label)
        info_layout.add_widget(last_msg_label)

        self.add_widget(avatar_layout)
        self.add_widget(main_info)

        with self.canvas.before:
            self._bg_color = Color(0.2, 0.2, 0.2, 0.25)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)] * 4)

        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(state=self._update_state)

    def _get_avatar_letter(self):
        first_name = (self.chat_data.get('first_name') or '').strip()
        if first_name:
            return first_name[0].upper()

        name = (self.chat_data.get('name') or '').strip()
        if name:
            name_parts = name.split()
            if len(name_parts) > 1:
                return name_parts[1][0].upper()
            return name[0].upper()

        return '?'

    def _get_avatar_color(self):
        letter = self._get_avatar_letter()
        if letter.isalpha():
            index = ord(letter.upper()) - ord('A')
            hue = (index % 26) / 26.0
        else:
            hue = 0.0

        r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.9)
        return (r, g, b, 1)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _update_state(self, *args):
        if self.state == 'down':
            self._bg_color.rgba = (0.3, 0.3, 0.3, 0.35)
        else:
            self._bg_color.rgba = (0.2, 0.2, 0.2, 0.25)

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
        self.background = ''
        self.background_color = (0, 0, 0, 0)
        self.on_user_selected = on_user_selected
        self.current_uid = current_uid
        self.db_manager = db_manager  # Сохраняем db_manager
        self.chats_db = chats_db

        layout = BoxLayout(orientation='vertical', padding=scale_dp(12), spacing=scale_dp(10))
        with layout.canvas.before:
            Color(*palette['surface'])
            self._popup_bg = RoundedRectangle(pos=layout.pos, size=layout.size,
                                              radius=[scale_dp(16)] * 4)
        layout.bind(
            pos=lambda *args: setattr(self._popup_bg, 'pos', layout.pos),
            size=lambda *args: setattr(self._popup_bg, 'size', layout.size)
        )

        search_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=scale_dp(48),
                                  spacing=scale_dp(8))
        self.search_input = TextInput(
            hint_text='Поиск по UID или email...',
            multiline=False,
            size_hint_x=0.8,
            background_color=palette['surface_alt'],
            foreground_color=palette['text_primary'],
            hint_text_color=palette['text_muted'],
            background_normal='',
            background_active='',
            font_size=scale_font(25)
        )
        search_btn = Button(
            text='Найти',
            background_color=palette['accent'],
            background_normal='',
            background_down='',
            color=palette['text_primary'],
            font_size=scale_font(25),
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
                    height=scale_dp(64),
                    padding=scale_dp(10),
                    spacing=scale_dp(8)
                )
                with user_item.canvas.before:
                    Color(*palette['surface_alt'])
                    item_bg = RoundedRectangle(pos=user_item.pos, size=user_item.size,
                                               radius=[scale_dp(10)] * 4)
                user_item.bind(
                    pos=lambda *args: setattr(item_bg, 'pos', user_item.pos),
                    size=lambda *args: setattr(item_bg, 'size', user_item.size)
                )

                info_layout = BoxLayout(orientation='vertical')
                name_label = Label(
                    text=user['name'],
                    halign='left',
                    color=palette['text_primary'],
                    font_size=scale_font(15)
                )
                name_label.bind(size=name_label.setter('text_size'))

                uid_label = Label(
                    text=f"UID: {user['uid']}",
                    halign='left',
                    color=palette['text_muted'],
                    font_size=scale_font(12)
                )
                uid_label.bind(size=uid_label.setter('text_size'))

                info_layout.add_widget(name_label)
                info_layout.add_widget(uid_label)

                select_btn = Button(
                    text='Написать',
                    size_hint_x=0.3,
                    background_color=palette['accent_muted'],
                    background_normal='',
                    background_down='',
                    color=palette['text_primary'],
                    font_size=scale_font(13),
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
