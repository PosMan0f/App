# screens/applications_screen.py
from kivy.uix.screenmanager import Screen
from applications.main_screen import ApplicationsMainScreen


class ApplicationsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "applications"

        # Создаем основной экран
        self.main_screen = ApplicationsMainScreen()
        self.add_widget(self.main_screen)

    def on_enter(self):
        """При входе на экран"""
        if hasattr(self.main_screen, 'on_enter'):
            self.main_screen.on_enter()

    def on_leave(self):
        """При выходе с экрана"""
        if hasattr(self.main_screen, 'on_leave'):
            self.main_screen.on_leave()