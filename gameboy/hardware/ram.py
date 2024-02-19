from array import array

from gameboy.common import UnexpectedFallThrough


class RAM:

    def __init__(self):
        self.wram = array('B', [0] * 0x2000)
        self.hram = array('B', [0] * 0x80)

    def read(self, address: int) -> int:
        if 0xC000 <= address <= 0xDFFF:  # Working RAM
            return self.wram[address - 0xC000]
        elif 0xFF80 <= address <= 0xFFFE:  # Zero Page / High RAM
            return self.hram[address - 0xFF80]
        raise UnexpectedFallThrough(f'{address:04X}')

    def write(self, address: int, value: int) -> None:
        if 0xC000 <= address <= 0xDFFF:  # Working RAM
            self.wram[address - 0xC000] = value
            return
        elif 0xFF80 <= address <= 0xFFFE:  # Zero Page / High RAM
            self.hram[address - 0xFF80] = value
            return
        raise UnexpectedFallThrough(f'{address:04X}: {value:04X}')
