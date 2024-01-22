from typing import Optional

import numpy as np

from gameboy.common.ioutils import load_u8_binary_file
from gameboy.common.typings import U8, U16, Int, U8Array
from gameboy.core import BaseDevice

EMPTY_MEMORY = np.empty((0,), dtype=U8)


class MemoryLike(BaseDevice):

    def __init__(self, file: Optional[str] = None):
        self._file = file
        self._memory = EMPTY_MEMORY

    def startup(self):
        self._memory = load_u8_binary_file(self._file)

    def shutdown(self):
        self._memory = EMPTY_MEMORY

    def read(self, address: U16) -> U8:
        return self._memory[address]

    def read_many(self, address: U16, size: Int) -> U8Array:
        return self._memory[address:address + size]

    def read_range(self, lowerbound: U16, upperbound: U16) -> U8Array:
        return self._memory[lowerbound:upperbound]

    def write(self, address: U16, value: U8):
        self._memory[address] = value
