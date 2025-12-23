# send/validator.py

class RequestValidator:
    """Класс для валидации данных заявки"""

    @staticmethod
    def validate_request_data(data):
        """Валидация данных заявки"""
        errors = []

        # Проверка отдела
        if data['department'] == 'Выберите отдел':
            errors.append('Выберите отдел')

        # Проверка названия
        if not data['title']:
            errors.append('Введите название задачи')
        elif len(data['title']) > 200:
            errors.append('Название задачи слишком длинное (макс. 200 символов)')

        # Проверка описания
        if not data['description']:
            errors.append('Введите описание задачи')
        elif len(data['description']) > 2000:
            errors.append('Описание задачи слишком длинное (макс. 2000 символов)')

        # Проверка количества дней
        if not data['days']:
            errors.append('Введите количество дней')
        elif not data['days'].isdigit():
            errors.append('Количество дней должно быть числом')
        elif not (1 <= int(data['days']) <= 365):
            errors.append('Количество дней должно быть от 1 до 365')

        return errors