from typing import TYPE_CHECKING

from gameboy.common.loggings import get_logger
from gameboy.common.typings import U8, U16
from gameboy.core.device import BaseDevice

if TYPE_CHECKING:
    from gameboy.hardware.bus import Bus

logger = get_logger(file=__file__)


class DMA(BaseDevice):

    def __init__(self):
        super().__init__()

        self._active = False
        self._delay = 0  # Delay 2 cycles before start
        self._base_addr = U16()
        self._offset = U16()
        self._bus: 'Bus' = None

    def write(self, addr: U8):  # start DMA copy process
        self._active = True
        self._delay = 2
        self._base_addr = U16(addr * 0x100)
        self._offset = U16(0)

        # TODO: move to emu cycle
        while self.step():
            pass

    def step(self):
        if not self._active:
            return False
        if self._delay:
            self._delay -= 1
            return False
        if self._bus is None:
            raise RuntimeError('DMA must connect to the BUS.')

        u8 = self._bus.read(self._base_addr + self._offset)
        self._bus.write(U16(0xFE00) + self._offset, u8)
        self._offset += U16(1)
        if self._offset >= 0xA0:
            self._active = False
        return True
