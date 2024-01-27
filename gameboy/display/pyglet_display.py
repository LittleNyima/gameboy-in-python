from typing import Tuple

import pyglet

from gameboy.display.base import BaseDisplay
from gameboy.hardware.motherboard import Motherboard
from gameboy.hardware.ppu import X_RESOLUTION


class PygletDisplay(BaseDisplay):

    def __init__(
        self, motherboard: Motherboard,
        window_title: str,
        window_size: Tuple[int, int] = (160, 144),
        scale: int = 2,
    ):
        super().__init__(
            motherboard=motherboard,
            window_title=window_title,
            window_size=window_size,
            scale=scale,
        )

        self._window = pyglet.window.Window(
            width=window_size[0] * scale,
            height=window_size[1] * scale,
            caption=window_title,
            resizable=False,
            vsync=True,
            visible=True,
        )

        self._window.set_handler('on_close', self.on_close)
        self._window.set_handler('on_draw', self.on_draw)
        self._window.set_handler('on_key_press', self.on_key_press)
        self._window.set_handler('on_key_release', self.on_key_release)
        self._window.set_handler('on_mouse_press', self.on_mouse_press)
        self._window.set_handler('on_mouse_release', self.on_mouse_release)
        self._window.set_handler('on_mouse_motion', self.on_mouse_motion)
        self._window.set_handler('on_mouse_drag', self.on_mouse_drag)
        self._window.set_handler('on_resize', self.on_resize)

    def tick(self):
        self._window.switch_to()
        self._window.dispatch_events()

    def render(self):
        self._window.switch_to()
        self._window.dispatch_events()
        self._window.dispatch_event('on_draw')
        self._window.flip()

    def on_draw(self):
        self._window.clear()
        color_depth = 4
        buffer = self._motherboard._ppu._video_buffer.tobytes()
        image = pyglet.image.ImageData(
            width=self._window_size[0],
            height=self._window_size[1],
            fmt='ARGB',
            data=buffer,
            pitch=-X_RESOLUTION * color_depth,
        )
        sprite = pyglet.sprite.Sprite(image)
        sprite.scale = self._scale
        sprite.draw()

    def on_close(self):
        self._motherboard._stopped = True

    def on_key_press(self, symbol, modifiers):
        pass

    def on_key_release(self, symbol, modifiers):
        pass

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_release(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_resize(self, width, height):
        pass


class PygletDebugDisplay(PygletDisplay):

    def __init__(
        self,
        motherboard: Motherboard,
        window_title: str,
        window_size: Tuple[int, int] = (160, 144),
        scale: int = 2,
    ):
        super().__init__(
            motherboard=motherboard,
            window_title=window_title,
            window_size=window_size,
            scale=scale,
        )

        self._rows = 24
        self._columns = 16

    def on_draw(self):
        self._window.clear()
