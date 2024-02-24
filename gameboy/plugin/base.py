from typing import TYPE_CHECKING, List

from gameboy.core import EventType

if TYPE_CHECKING:
    from gameboy import GameBoy


class BasePlugin:

    def __init__(self, gameboy: 'GameBoy'):
        self.gameboy = gameboy
        self.motherboard = gameboy.motherboard
        self.enabled = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def handle_events(self, event_queue: List[EventType]):
        pass

    def after_tick(self):
        pass
