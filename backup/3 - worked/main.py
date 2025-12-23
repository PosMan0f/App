from config import *

from kivy.app import App
from kivy.core.window import Window
from main_layout import MainLayout


class MyApp(App):
    def build(self):
        Window.size = (win_width, win_height)
        Window.borderless = True
        return MainLayout()

if __name__ == "__main__":
    MyApp().run()