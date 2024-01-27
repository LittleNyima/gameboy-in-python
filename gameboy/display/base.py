from typing import Tuple

from gameboy.hardware.motherboard import Motherboard


class BaseDisplay:

    def __init__(
        self,  motherboard: Motherboard,
        window_title: str,
        window_size: Tuple[int, int] = (160, 144),
        scale: int = 2,
    ):
        self._motherboard = motherboard
        self._window_title = window_title
        self._window_size = (
            window_size[0],
            window_size[1],
        )
        self._scale = scale

    def render(self):
        raise NotImplementedError
