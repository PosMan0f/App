from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.metrics import sp
from datetime import datetime
import re


class LoginRegisterForm:
    """Класс для создания формы входа/регистрации"""

    @staticmethod
    def create_login_form(callback):
        """Создает форму входа"""
        form = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        # Email для входа
        form.add_widget(Label(text='Email:', size_hint_y=None, height=30))
        login_email = TextInput(
            multiline=False,
            hint_text='example@mail.com',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(login_email)

        # Пароль для входа
        form.add_widget(Label(text='Пароль:', size_hint_y=None, height=30))
        login_password = TextInput(
            multiline=False,
            password=True,
            hint_text='Введите пароль',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(login_password)

        # Кнопка входа
        login_btn = Button(
            text='Войти',
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 1, 0.8)
        )

        def on_login(instance):
            callback('login', {
                'email': login_email.text.strip(),
                'password': login_password.text.strip()
            })

        login_btn.bind(on_press=on_login)
        form.add_widget(login_btn)

        return form, login_email, login_password

    @staticmethod
    def create_register_form(callback):
        """Создает форму регистрации"""
        form = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        # Поля для регистрации
        fields = {}

        # Email
        form.add_widget(Label(text='Email*:', size_hint_y=None, height=30))
        fields['email'] = TextInput(
            multiline=False,
            hint_text='example@mail.com',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(fields['email'])

        # Пароль
        form.add_widget(Label(text='Пароль*:', size_hint_y=None, height=30))
        fields['password'] = TextInput(
            multiline=False,
            password=True,
            hint_text='Не менее 6 символов',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(fields['password'])

        # Подтверждение пароля
        form.add_widget(Label(text='Подтвердите пароль*:', size_hint_y=None, height=30))
        fields['confirm_password'] = TextInput(
            multiline=False,
            password=True,
            hint_text='Повторите пароль',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(fields['confirm_password'])

        # Имя
        form.add_widget(Label(text='Имя:', size_hint_y=None, height=30))
        fields['first_name'] = TextInput(
            multiline=False,
            hint_text='Иван',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(fields['first_name'])

        # Фамилия
        form.add_widget(Label(text='Фамилия:', size_hint_y=None, height=30))
        fields['last_name'] = TextInput(
            multiline=False,
            hint_text='Иванов',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(fields['last_name'])

        # Отчество
        form.add_widget(Label(text='Отчество:', size_hint_y=None, height=30))
        fields['middle_name'] = TextInput(
            multiline=False,
            hint_text='Иванович',
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1)
        )
        form.add_widget(fields['middle_name'])

        # Кнопка регистрации
        register_btn = Button(
            text='Зарегистрироваться',
            size_hint_y=None,
            height=50,
            background_color=(0.4, 0.8, 0.4, 0.8)
        )

        def on_register(instance):
            data = {k: v.text.strip() for k, v in fields.items()}
            callback('register', data)

        register_btn.bind(on_press=on_register)
        form.add_widget(register_btn)

        return form, fields


class ProfileForm:
    """Класс для создания формы профиля"""

    @staticmethod
    def create_profile_form(user_data, is_locked=False):
        """Создает форму профиля"""
        form = BoxLayout(orientation='vertical', spacing=15, padding=20, size_hint_y=None)
        form.bind(minimum_height=form.setter('height'))

        # Поля формы
        fields = {}

        # Имя
        form.add_widget(Label(text='Имя:', size_hint_y=None, height=30))
        fields['first_name'] = TextInput(
            text=user_data.get('first_name', '') or '',
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            readonly=is_locked
        )
        form.add_widget(fields['first_name'])

        # Фамилия
        form.add_widget(Label(text='Фамилия:', size_hint_y=None, height=30))
        fields['last_name'] = TextInput(
            text=user_data.get('last_name', '') or '',
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            readonly=is_locked
        )
        form.add_widget(fields['last_name'])

        # Отчество
        form.add_widget(Label(text='Отчество:', size_hint_y=None, height=30))
        fields['middle_name'] = TextInput(
            text=user_data.get('middle_name', '') or '',
            multiline=False,
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            foreground_color=(1, 1, 1, 1),
            readonly=is_locked
        )
        form.add_widget(fields['middle_name'])

        # Дата рождения
        form.add_widget(Label(text='Дата рождения (ДД.ММ.ГГГГ):', size_hint_y=None, height=30))
        birth_date = user_data.get('birth_date')
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
            readonly=is_locked
        )
        form.add_widget(fields['birth_date'])

        # Отдел
        form.add_widget(Label(text='Отдел:', size_hint_y=None, height=30))
        fields['department'] = Spinner(
            text=user_data.get('department', 'Не выбран') or 'Не выбран',
            values=('Не выбран', 'IT-отдел', 'Юридический отдел', 'HR-отдел'),
            size_hint_y=None,
            height=40,
            background_color=(1, 1, 1, 0.1),
            color=(1, 1, 1, 1),
            disabled=is_locked
        )
        form.add_widget(fields['department'])

        return form, fields