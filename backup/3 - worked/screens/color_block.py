from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

class ColorBlock(Widget):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size