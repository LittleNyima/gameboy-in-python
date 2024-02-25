from typing import TYPE_CHECKING, List

from gameboy.core import EventType

from .base import BasePlugin
from .debugging import DebuggingSerial, DebuggingTileView
from .window import GameSDL2Window

if TYPE_CHECKING:
    from gameboy import GameBoy


class Plugins:

    def __init__(self, gameboy: 'GameBoy'):
        self.debugging_serial = DebuggingSerial(gameboy=gameboy)
        self.debugging_tile_view = DebuggingTileView(
            gameboy=gameboy, title='Tile View', scale=2,
        )
        self.game_view = GameSDL2Window(
            gameboy=gameboy, title='Game View', scale=2,
        )
        self.game_view.enable()

    def handle_events(self, event_queue: List[EventType]):
        for attr in self.__dict__.values():
            if isinstance(attr, BasePlugin) and attr.enabled:
                attr.handle_events(event_queue=event_queue)

    def after_tick(self):
        for attr in self.__dict__.values():
            if isinstance(attr, BasePlugin) and attr.enabled:
                attr.after_tick()


__all__ = ['Plugins']
