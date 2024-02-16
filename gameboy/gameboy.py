import time

from .hardware import Motherboard


class GameBoy:

    def __init__(self, gamerom: str):
        self.paused = False
        self.running = True
        self.ticks = 0

        self.motherboard = Motherboard(
            gamerom=gamerom,
        )

    def tick(self):
        if self.paused:
            time.sleep(1 / 60)
            return True

        self.motherboard.tick()

        self.ticks += 1
        return self.running

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.running = False
