from . import Cartridge


class Motherboard:

    def __init__(self, gamerom: str):
        self.gamerom = Cartridge(filename=gamerom)

    def tick(self):
        pass
