from array import array

from gameboy.common import UnexpectedFallThrough


class PPU:

    def __init__(self):
        self.vram = array('B', [0] * 0x2000)
        self.oam = array('B', [0] * 0xA0)

    def read(self, address: int) -> int:
        if 0x8000 <= address <= 0x9FFF:
            return self.vram[address - 0x8000]
        elif 0xFE00 <= address <= 0xFE9F:
            return self.oam[address - 0xFE00]
        raise UnexpectedFallThrough

    def write(self, address: int, value: int) -> None:
        if 0x8000 <= address <= 0x9FFF:
            self.vram[address - 0x8000] = value
            return
        elif 0xFE00 <= address <= 0xFE9F:
            self.oam[address - 0xFE00] = value
            return
        raise UnexpectedFallThrough
