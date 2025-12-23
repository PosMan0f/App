from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.metrics import sp
from datetime import datetime
import re
import json
import os

from screens.color_block import ColorBlock
from .database import Database
from .auth_manager import AuthManager
from .session_manager import session_manager

# Регистрируем шрифт Times New Roman
try:
    LabelBase.register(name='TimesNewRoman',
                       fn_regular='times.ttf',
                       fn_bold='timesbd.ttf',
                       fn_italic='timesi.ttf',
                       fn_bolditalic='timesbi.ttf')
except:
    pass  # Используем стандартный шрифт если Times New Roman не найден

# Файл для хранения токена
TOKEN_FILE = 'auth_token.json'


class ProfileLogic:
    def __init__(self):
        self.db = Database()
        self.auth = AuthManager()
        self.current_user = None
        self.is_locked = False

        # Инициализируем шрифты
        self.register_fonts()

        # Создаем виджеты
        self.color_block = ColorBlock(color=(0, 0, 0, 0))
        self.content_container = BoxLayout(orientation='vertical')

        # Проверяем авто-вход
        self.check_auto_login()

        # Загружаем начальную форму
        self.load_initial_form()

    def register_fonts(self):
        """Регистрирует шрифты"""
        try:
            LabelBase.register(name='TimesNewRoman',
                               fn_regular='times.ttf',
                               fn_bold='timesbd.ttf',
                               fn_italic='timesi.ttf',
                               fn_bolditalic='timesbi.ttf')
            return True
        except:
            return False

    def check_auto_login(self):
        """Проверяем автоматический вход по токену"""
        user = self.auth.check_auto_login()
        if user:
            self.current_user = user
            self.is_locked = bool(user.get('locked', 0))
            # Сохраняем в сессию
            session_manager.set_current_user(user)

    def load_initial_form(self):
        """Загружает начальную форму (вход или профиль)"""
        self.content_container.clear_widgets()

        if self.current_user:
            self.load_profile_form()
        else:
            self.load_login_register_form()

    def load_login_register_form(self):
        """Загружает форму входа/регистрации"""
        scroll = ScrollView()
        main_layout = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        # Заголовок
        title = Label(
            text='Авторизация / Регистрация',
            size_hint_y=None,
            height=80,
            halign='center',
            font_size=sp(24),
            bold=True,
            font_name='TimesNewRoman',
            color=(0.8, 0.8, 0.8, 1)
        )
        title.bind(size=title.setter('text_size'))
        main_layout.add_widget(title)

        # Форма входа
        login_form, self.login_email, self.login_password = self.create_login_form()
        main_layout.add_widget(login_form)

        # Разделитель
        separator = Label(
            text='──────── ИЛИ ────────',
            size_hint_y=None,
            height=40,
            halign='center',
            font_size=sp(14),
            font_name='TimesNewRoman',
            color=(0.6, 0.6, 0.6, 1)
        )
        separator.bind(size=separator.setter('text_size'))
        main_layout.add_widget(separator)

        # Форма регистрации
        register_form, self.register_fields = self.create_register_form()
        main_layout.add_widget(register_form)

        scroll.add_widget(main_layout)
        self.content_container.add_widget(scroll)

    def create_login_form(self):
        """Создает форму входа"""
        from kivy.uix.textinput import TextInput

        form = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        # Email
        form.add_widget(Label(text='Email:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        login_email = TextInput(
            multiline=False,
            hint_text='example@mail.com',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(login_email)

        # Пароль
        form.add_widget(Label(text='Пароль:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        login_password = TextInput(
            multiline=False,
            password=True,
            hint_text='Введите пароль',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(login_password)

        # Кнопка входа
        login_btn = Button(
            text='Войти',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 0.8),
            font_name='TimesNewRoman'
        )
        login_btn.bind(on_press=lambda x: self.handle_auth_action('login', {
            'email': login_email.text.strip(),
            'password': login_password.text.strip()
        }))
        form.add_widget(login_btn)

        return form, login_email, login_password

    def create_register_form(self):
        """Создает форму регистрации"""
        from kivy.uix.textinput import TextInput

        form = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        fields = {}

        # Email
        form.add_widget(Label(text='Email*:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['email'] = TextInput(
            multiline=False,
            hint_text='example@mail.com',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(fields['email'])

        # Пароль
        form.add_widget(Label(text='Пароль*:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['password'] = TextInput(
            multiline=False,
            password=True,
            hint_text='Не менее 6 символов',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(fields['password'])

        # Подтверждение пароля
        form.add_widget(Label(text='Подтвердите пароль*:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['confirm_password'] = TextInput(
            multiline=False,
            password=True,
            hint_text='Повторите пароль',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(fields['confirm_password'])

        # Имя
        form.add_widget(Label(text='Имя:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['first_name'] = TextInput(
            multiline=False,
            hint_text='Иван',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(fields['first_name'])

        # Фамилия
        form.add_widget(Label(text='Фамилия:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['last_name'] = TextInput(
            multiline=False,
            hint_text='Иванов',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(fields['last_name'])

        # Отчество
        form.add_widget(Label(text='Отчество:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['middle_name'] = TextInput(
            multiline=False,
            hint_text='Иванович',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        form.add_widget(fields['middle_name'])

        # Кнопка регистрации
        register_btn = Button(
            text='Зарегистрироваться',
            size_hint_y=None,
            height=50,
            background_color=(0.4, 0.8, 0.4, 0.8),
            font_name='TimesNewRoman'
        )
        register_btn.bind(on_press=lambda x: self.handle_auth_action('register', {
            'email': fields['email'].text.strip(),
            'password': fields['password'].text.strip(),
            'confirm_password': fields['confirm_password'].text.strip(),
            'first_name': fields['first_name'].text.strip(),
            'last_name': fields['last_name'].text.strip(),
            'middle_name': fields['middle_name'].text.strip()
        }))
        form.add_widget(register_btn)

        return form, fields

    def handle_auth_action(self, action_type, data):
        """Обрабатывает действия аутентификации"""
        if action_type == 'login':
            self.process_login(data)
        elif action_type == 'register':
            self.process_registration(data)

    def process_login(self, data):
        """Обрабатывает вход пользователя"""
        email = data['email']
        password = data['password']

        if not email or not password:
            self.show_message('Ошибка', 'Заполните все поля для входа')
            return

        user = self.auth.login_user(email, password)
        if user:
            # Сохраняем пользователя в сессии
            session_manager.set_current_user(user)

            self.current_user = user
            self.is_locked = bool(user.get('locked', 0))
            self.load_profile_form()
        else:
            self.show_message('Ошибка', 'Неверный email или пароль')

    def process_registration(self, data):
        """Обрабатывает регистрацию пользователя"""
        # Валидация
        errors = self.validate_registration_data(data)
        if errors:
            self.show_message('Ошибка', errors)
            return

        # Регистрация
        user = self.auth.register_user(
            data['email'],
            data['password'],
            data['first_name'],
            data['last_name'],
            data['middle_name']
        )

        if user:
            # Сохраняем пользователя в сессии
            session_manager.set_current_user(user)

            self.current_user = user
            self.is_locked = bool(user.get('locked', 0))
            self.load_profile_form()

            # Очищаем поля
            for field in self.register_fields.values():
                field.text = ''
        else:
            self.show_message('Ошибка', 'Ошибка при регистрации')

    def validate_registration_data(self, data):
        """Валидирует данные регистрации"""
        if not data['email'] or not data['password']:
            return 'Заполните обязательные поля'

        if len(data['password']) < 6:
            return 'Пароль должен быть не менее 6 символов'

        if data['password'] != data['confirm_password']:
            return 'Пароли не совпадают'

        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', data['email']):
            return 'Неверный формат email'

        if self.db.get_user_by_email(data['email']):
            return 'Пользователь с таким email уже существует'

        return None

    def load_profile_form(self):
        """Загружает форму профиля"""
        self.content_container.clear_widgets()

        scroll = ScrollView()
        form_layout = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        # Проверяем статус блокировки
        self.is_locked = bool(self.current_user.get('locked', 0))

        # Заголовок
        title_text = f'Профиль пользователя\nUID: {self.current_user["uid"]}'
        if self.is_locked:
            title_text += '\n[color=ff0000]ЗАБЛОКИРОВАН[/color]'

        title = Label(
            text=title_text,
            size_hint_y=None,
            height=80,
            halign='center',
            font_size=sp(20),
            bold=True,
            font_name='TimesNewRoman',
            markup=True
        )
        title.bind(size=title.setter('text_size'))
        form_layout.add_widget(title)

        # Email (только для отображения)
        form_layout.add_widget(Label(text='Email:', size_hint_y=None, height=30,
                                     font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        email_label = Label(
            text=self.current_user['email'],
            size_hint_y=None,
            height=40,
            color=(0.8, 0.8, 0.8, 1),
            font_name='TimesNewRoman'
        )
        email_label.bind(size=email_label.setter('text_size'))
        form_layout.add_widget(email_label)

        # Создаем форму профиля
        profile_form, self.profile_fields = self.create_profile_form()
        form_layout.add_widget(profile_form)

        # Кнопки
        if not self.is_locked:
            # Кнопка сохранения
            save_btn = Button(
                text='Сохранить изменения',
                size_hint_y=None,
                height=50,
                background_color=(0.2, 0.6, 1, 0.8),
                font_name='TimesNewRoman'
            )
            save_btn.bind(on_press=self.save_profile)
            form_layout.add_widget(save_btn)

            # Кнопка смены пароля
            change_pass_btn = Button(
                text='Сменить пароль',
                size_hint_y=None,
                height=50,
                background_color=(0.4, 0.8, 0.4, 0.8),
                font_name='TimesNewRoman'
            )
            change_pass_btn.bind(on_press=self.show_change_password)
            form_layout.add_widget(change_pass_btn)

        # Кнопка выхода
        logout_btn = Button(
            text='Выйти',
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.2, 0.2, 0.8),
            font_name='TimesNewRoman'
        )
        logout_btn.bind(on_press=self.logout)
        form_layout.add_widget(logout_btn)

        scroll.add_widget(form_layout)
        self.content_container.add_widget(scroll)

    def create_profile_form(self):
        """Создает форму профиля"""
        from kivy.uix.textinput import TextInput
        from kivy.uix.spinner import Spinner

        form = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        fields = {}

        # Имя
        form.add_widget(Label(text='Имя:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['first_name'] = TextInput(
            text=self.current_user.get('first_name', '') or '',
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman',
            readonly=self.is_locked
        )
        form.add_widget(fields['first_name'])

        # Фамилия
        form.add_widget(Label(text='Фамилия:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['last_name'] = TextInput(
            text=self.current_user.get('last_name', '') or '',
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman',
            readonly=self.is_locked
        )
        form.add_widget(fields['last_name'])

        # Отчество
        form.add_widget(Label(text='Отчество:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['middle_name'] = TextInput(
            text=self.current_user.get('middle_name', '') or '',
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman',
            readonly=self.is_locked
        )
        form.add_widget(fields['middle_name'])

        # Дата рождения
        form.add_widget(Label(text='Дата рождения (ДД.ММ.ГГГГ):', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        birth_date = self.current_user.get('birth_date')
        display_birth_date = ''

        if birth_date:
            try:
                dt = datetime.strptime(birth_date, '%Y-%m-%d')
                display_birth_date = dt.strftime('%d.%m.%Y')
            except:
                display_birth_date = ''

        fields['birth_date'] = TextInput(
            text=display_birth_date,
            multiline=False,
            hint_text='01.01.1990',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman',
            readonly=self.is_locked
        )
        form.add_widget(fields['birth_date'])

        # Отдел
        form.add_widget(Label(text='Отдел:', size_hint_y=None, height=30,
                              font_name='TimesNewRoman', color=(0.8, 0.8, 0.8, 1)))
        fields['department'] = Spinner(
            text=self.current_user.get('department', 'Не выбран') or 'Не выбран',
            values=('Не выбран', 'IT-отдел', 'Юридический отдел', 'HR-отдел'),
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        fields['department'].disabled = self.is_locked
        form.add_widget(fields['department'])

        return form, fields

    def show_change_password(self, instance):
        """Показывает форму смены пароля"""
        from kivy.uix.textinput import TextInput

        popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Старый пароль
        popup_layout.add_widget(Label(text='Старый пароль:', font_name='TimesNewRoman'))
        old_password = TextInput(
            multiline=False,
            password=True,
            hint_text='Введите старый пароль',
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        popup_layout.add_widget(old_password)

        # Новый пароль
        popup_layout.add_widget(Label(text='Новый пароль:', font_name='TimesNewRoman'))
        new_password = TextInput(
            multiline=False,
            password=True,
            hint_text='Введите новый пароль',
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        popup_layout.add_widget(new_password)

        # Подтверждение пароля
        popup_layout.add_widget(Label(text='Подтвердите пароль:', font_name='TimesNewRoman'))
        confirm_password = TextInput(
            multiline=False,
            password=True,
            hint_text='Повторите новый пароль',
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            font_name='TimesNewRoman'
        )
        popup_layout.add_widget(confirm_password)

        # Кнопки
        button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)

        change_btn = Button(
            text='Изменить',
            background_color=(0.2, 0.6, 1, 1),
            font_name='TimesNewRoman'
        )

        def change_password(instance):
            old_pass = old_password.text.strip()
            new_pass = new_password.text.strip()
            confirm_pass = confirm_password.text.strip()

            if not old_pass or not new_pass or not confirm_pass:
                self.show_message('Ошибка', 'Заполните все поля')
                return

            if len(new_pass) < 6:
                self.show_message('Ошибка', 'Новый пароль должен быть не менее 6 символов')
                return

            if new_pass != confirm_pass:
                self.show_message('Ошибка', 'Новые пароли не совпадают')
                return

            success = self.db.update_password(self.current_user['uid'], old_pass, new_pass)
            if success:
                popup.dismiss()
                self.show_message('Успех', 'Пароль успешно изменен')
            else:
                self.show_message('Ошибка', 'Неверный старый пароль или учетная запись заблокирована')

        change_btn.bind(on_press=change_password)

        cancel_btn = Button(
            text='Отмена',
            background_color=(0.8, 0.2, 0.2, 1),
            font_name='TimesNewRoman'
        )
        cancel_btn.bind(on_press=lambda x: popup.dismiss())

        button_layout.add_widget(change_btn)
        button_layout.add_widget(cancel_btn)
        popup_layout.add_widget(button_layout)

        popup = Popup(
            title='Смена пароля',
            content=popup_layout,
            size_hint=(0.7, 0.5),
            title_font='TimesNewRoman'
        )
        popup.open()

    def save_profile(self, instance):
        """Сохраняет изменения профиля"""
        if self.is_locked:
            self.show_message('Ошибка', 'Учетная запись заблокирована')
            return

        # Собираем данные из полей
        data = {
            'first_name': self.profile_fields['first_name'].text.strip(),
            'last_name': self.profile_fields['last_name'].text.strip(),
            'middle_name': self.profile_fields['middle_name'].text.strip(),
            'birth_date': self.profile_fields['birth_date'].text.strip(),
            'department': self.profile_fields['department'].text
        }

        # Валидация даты
        formatted_birth_date = ''
        if data['birth_date']:
            try:
                dt = datetime.strptime(data['birth_date'], '%d.%m.%Y')
                formatted_birth_date = dt.strftime('%Y-%m-%d')
            except ValueError:
                self.show_message('Ошибка', 'Неверный формат даты')
                return

        # Сохранение
        success = self.db.update_user_profile(
            self.current_user['uid'],
            data['first_name'],
            data['last_name'],
            data['middle_name'],
            formatted_birth_date,
            data['department'] if data['department'] != 'Не выбран' else ''
        )

        if success:
            self.current_user = self.db.get_user_by_uid(self.current_user['uid'])
            self.show_message('Успех', 'Данные сохранены')
        else:
            self.show_message('Ошибка', 'Не удалось сохранить данные')

    def logout(self, instance):
        """Выход из аккаунта"""
        if self.current_user:
            self.auth.logout_user(self.current_user['uid'])

        # Очищаем сессию
        session_manager.clear_session()

        self.current_user = None
        self.is_locked = False
        self.load_initial_form()

    def show_message(self, title, message):
        """Показывает сообщение"""
        popup = Popup(
            title=title,
            content=Label(text=message, font_name='TimesNewRoman'),
            size_hint=(0.6, 0.3),
            title_font='TimesNewRoman'
        )
        popup.open()

    def on_enter(self):
        """Вызывается при переходе на экран"""
        # Если нужно обновить данные при каждом входе
        pass

    def cleanup(self):
        """Очистка ресурсов"""
        if self.db:
            self.db.conn.close()