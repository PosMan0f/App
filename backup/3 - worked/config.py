import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
import ctypes

from kivy.config import Config
Config.set("graphics", "resizable", 0)

user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)

win_height = int(screen_height * 0.5)
win_width = int(win_height * 9 / 16)