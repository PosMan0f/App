from kivy.uix.screenmanager import Screen
from logining.profile_logic import ProfileLogic


class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "profile"

        # Инициализируем логику профиля (без аргументов)
        self.logic = ProfileLogic()

        # Добавляем виджеты из логики
        self.add_widget(self.logic.color_block)
        self.add_widget(self.logic.content_container)

    def on_enter(self, *args):
        """Вызывается при переходе на этот экран"""
        super().on_enter(*args)
        self.logic.on_enter()