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
