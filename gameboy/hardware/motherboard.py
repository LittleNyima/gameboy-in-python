from gameboy.hardware.bus import Bus
from gameboy.hardware.cartridge import Cartridge
from gameboy.hardware.cpu import CPU
from gameboy.hardware.ram import RAM


class Motherboard:

    def __init__(self, gamerom: str):
        self.cartridge = Cartridge(filename=gamerom)
        self.ram = RAM()
        self.bus = Bus(motherboard=self)
        self.cpu = CPU(motherboard=self)

        self.ticks = 0

    def tick(self):
        self.cpu.tick()
        self.ticks += 1

    def emulate(self, cycles: int):
        pass
