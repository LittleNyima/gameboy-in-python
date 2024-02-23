from gameboy.hardware.bus import Bus
from gameboy.hardware.cartridge import Cartridge
from gameboy.hardware.cpu import CPU
from gameboy.hardware.io import IO
from gameboy.hardware.ram import RAM
from gameboy.hardware.timer import Timer


class Motherboard:

    def __init__(self, gamerom: str):
        self.cartridge = Cartridge(filename=gamerom)
        self.ram = RAM()
        self.timer = Timer()
        self.io = IO(motherboard=self)
        self.bus = Bus(motherboard=self)
        self.cpu = CPU(motherboard=self)

        self.timer.cpu = self.cpu
        self.io.cpu = self.cpu

        self.ticks = 0

    def tick(self):
        self.cpu.tick()

    def emulate(self, cycles: int):
        n = cycles * 4
        for _ in range(n):
            self.ticks += 1
            self.timer.tick()
