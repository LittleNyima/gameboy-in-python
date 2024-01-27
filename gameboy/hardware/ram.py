import numpy as np

from gameboy.common.typings import U8, U16
from gameboy.hardware.memory import MemoryLike


class RAM(MemoryLike):

    def __init__(self, base_addr: U16, size: U16):
        super().__init__()
        self.base_addr = base_addr
        self.size = size

    def startup(self):
        self._memory = np.zeros((self.size,), dtype=U8)

    def read(self, address: U16) -> U8:
        if self.base_addr <= address <= self.base_addr + self.size:
            offset = address - self.base_addr
            return super().read(offset)
        raise RuntimeError(f'Invalid address {address:04X}.')

    def write(self, address: U16, value: U8):
        if self.base_addr <= address <= self.base_addr + self.size:
            offset = address - self.base_addr
            return super().write(offset, value)
        raise RuntimeError(f'Invalid address {address:04X}.')


class VRAM(RAM):
    """The VRAM Object.

    Memory Mapping
    --------------
    +-----+------------+---------------------------------------------------+\\
    |Block|VRAM Address|               Corresponding Tile IDs              |\\
    +-----+------------+---------+--------------------+--------------------+\\
    |     |            | Objects | BG/Win if LCDC.4=1 | BG/Win if LCDC.4=0 |\\
    |  0  |$8000-$87FF |  0-127  |   0-127            |                    |\\
    |  1  |$8800-$8FFF | 128-255 |  128-255           | 128-255 or -128--1 |\\
    |  2  |$9000-$97FF | Unusable|                    |  0-127             |\\
    +-----+------------+---------+--------------------+--------------------+
    """

    def __init__(self, base_addr: U16 = U16(0x8000), size: U16 = U16(0x1800)):
        super().__init__(base_addr, size)

        # each tile is 16 bytes
        self._dirty = np.ones((size // 16), dtype=bool)

    def write(self, address: U16, value: U8):
        offset = address - self.base_addr
        if value != self.read(offset):
            tile_index = offset // 16
            self._dirty[tile_index] = True
        return super().write(address, value)
