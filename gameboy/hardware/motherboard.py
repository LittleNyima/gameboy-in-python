from gameboy.hardware.bus import Bus
from gameboy.hardware.cartridge import Cartridge
from gameboy.hardware.cpu import CPU
from gameboy.hardware.io import IO
from gameboy.hardware.lcd import LCD
from gameboy.hardware.ppu import PPU
from gameboy.hardware.ram import RAM
from gameboy.hardware.timer import Timer


class Motherboard:

    def __init__(self, gamerom: str):
        self.cartridge = Cartridge(filename=gamerom)
        self.ram = RAM()
        self.lcd = LCD()
        self.ppu = PPU(motherboard=self)
        self.timer = Timer(motherboard=self)
        self.io = IO(motherboard=self)
        self.bus = Bus(motherboard=self)
        self.cpu = CPU(motherboard=self)

        self.ticks = 0

    def tick(self):
        self.cpu.tick()

    def emulate(self, cycles: int):
        for _ in range(cycles):
            for _ in range(4):
                self.ticks += 1
                self.timer.tick()
                self.ppu.tick()
            self.io.dma.tick()
