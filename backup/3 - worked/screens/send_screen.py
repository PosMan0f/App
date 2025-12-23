# screens/send_screen.py
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Rectangle
from send.request_form import RequestForm
from send.database import RequestDatabase
from send.validator import RequestValidator
from kivy.clock import Clock
from ui_style import palette


class SendScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "send_request"

        # Инициализация базы данных
        self.database = RequestDatabase()
        self.validator = RequestValidator()

        # Создаем форму
        self.form = RequestForm(on_submit_callback=self.submit_request)

        # Устанавливаем фон
        with self.form.canvas.before:
            Color(*palette['surface'])
            self.rect = Rectangle(size=self.form.size, pos=self.form.pos)

        # Привязка изменения размера
        self.form.bind(size=self._update_rect, pos=self._update_rect)

        self.add_widget(self.form)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def submit_request(self, data):
        """Обработка отправки заявки"""
        # Валидация
        errors = self.validator.validate_request_data(data)

        if errors:
            self.form.show_status('Ошибка: ' + ', '.join(errors), is_error=True)
            return

        # Сохранение в БД
        success = self.database.save_request(
            data['department'],
            data['title'],
            data['description'],
            int(data['days'])
        )

        if success:
            self.form.show_status(
                f'Заявка успешно отправлена в {data["department"]}!',
                is_error=False
            )
            # Очищаем форму с задержкой для отображения статуса
            Clock.schedule_once(self._clear_form_delayed, 1.5)
        else:
            self.form.show_status('Ошибка при сохранении в базу данных', is_error=True)

    def _clear_form_delayed(self, dt):
        """Очистка формы с задержкой"""
        self.form.clear_form()
