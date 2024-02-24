# from gameboy.common import UnexpectedFallThrough
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gameboy.hardware import Motherboard


class DMA:

    def __init__(self, motherboard: 'Motherboard'):
        self.active = False
        self.offset = 0
        self.base = 0
        self.start_delay = 0

        self.motherboard = motherboard

    def write(self, value: int):
        self.active = True
        self.offset = 0
        self.base = value
        self.start_delay = 2

    def tick(self):
        if self.active:
            if self.start_delay:
                self.start_delay -= 1
                return
            addr = self.base * 0x100 + self.offset
            value = self.motherboard.bus.read(address=addr)
            self.motherboard.ppu.oam[self.offset] = value
            self.offset += 1
            self.active = self.offset < 0xA0


class Serial:

    def __init__(self):
        self.data = 0
        self.control = 0


class IO:

    def __init__(self, motherboard: 'Motherboard'):
        self.serial = Serial()
        self.dma = DMA(motherboard=motherboard)
        self.motherboard = motherboard
        self.timer = motherboard.timer

    def read(self, address: int) -> int:
        if address == 0xFF01:
            return self.serial.data
        elif address == 0xFF02:
            return self.serial.control
        elif 0xFF04 <= address <= 0xFF07:
            return self.timer.read(address=address)
        elif address == 0xFF0F:
            return self.motherboard.cpu.int_flags_register
        return 0
        # raise UnexpectedFallThrough

    def write(self, address: int, value: int) -> None:
        if address == 0xFF01:
            self.serial.data = value
            return
        elif address == 0xFF02:
            self.serial.control = value
            return
        elif 0xFF04 <= address <= 0xFF07:
            self.timer.write(address=address, value=value)
            return
        elif address == 0xFF0F:
            self.motherboard.cpu.int_flags_register = value
            return
        elif address == 0xFF46:
            self.dma.write(value=value)
            return
        return
        # raise UnexpectedFallThrough(f'{address:04X}: {value:02X}')
