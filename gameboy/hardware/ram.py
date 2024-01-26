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
