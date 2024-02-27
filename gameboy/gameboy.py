import time
from typing import List

from gameboy.core import Event, EventType
from gameboy.hardware import Motherboard
from gameboy.plugin import Plugins


class GameBoy:

    def __init__(self, gamerom: str):
        self.paused = False
        self.running = True

        self.motherboard = Motherboard(
            gamerom=gamerom,
        )

        self.event_queue: List[Event] = []
        self.plugins = Plugins(gameboy=self)

    def handle_events(self):
        self.plugins.handle_events(self.event_queue)
        for event in self.event_queue:
            if event.type == EventType.QUIT:
                self.running = False
            elif event.type in {
                EventType.PRESS_ARROW_UP,
                EventType.PRESS_ARROW_DOWN,
                EventType.PRESS_ARROW_RIGHT,
                EventType.PRESS_ARROW_LEFT,
                EventType.PRESS_BUTTON_A,
                EventType.PRESS_BUTTON_B,
                EventType.PRESS_BUTTON_START,
                EventType.PRESS_BUTTON_SELECT,
                EventType.RELEASE_ARROW_UP,
                EventType.RELEASE_ARROW_DOWN,
                EventType.RELEASE_ARROW_RIGHT,
                EventType.RELEASE_ARROW_LEFT,
                EventType.RELEASE_BUTTON_A,
                EventType.RELEASE_BUTTON_B,
                EventType.RELEASE_BUTTON_START,
                EventType.RELEASE_BUTTON_SELECT,
            }:
                self.motherboard.io.joypad.handle_event(event)
        self.event_queue.clear()

    def tick(self) -> bool:
        if self.paused:
            time.sleep(1 / 60)
            return True

        self.handle_events()

        self.motherboard.tick()
        self.plugins.after_tick()

        return self.running

    @property
    def ticks(self):
        return self.motherboard.ticks

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.running = False
