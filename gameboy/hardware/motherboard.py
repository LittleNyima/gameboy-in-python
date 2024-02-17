from gameboy.hardware.bus import Bus
from gameboy.hardware.cartridge import Cartridge
from gameboy.hardware.cpu import CPU


class Motherboard:

    def __init__(self, gamerom: str):
        self.cartridge = Cartridge(filename=gamerom)
        self.bus = Bus(cartridge=self.cartridge)
        self.cpu = CPU(motherboard=self)

    def tick(self):
        self.cpu.tick()

    def emulate(self, cycles: int):
        pass
