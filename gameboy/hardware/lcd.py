import numpy as np

from gameboy.common.errors import UnexpectedFallThroughError
from gameboy.common.typings import U8, U16, U8Array
from gameboy.core import IODevice
from gameboy.hardware.register import LCDC, STAT


class LCD(IODevice):

    def __init__(self):
        super().__init__()

        self._lcdc = LCDC(0x91)  # FF40: LCD Control (R/W)
        self._stat = STAT()  # FF41: LCD Status (Mixed)
        self._scy = U8()  # FF42: Bg viewport Y position (R/W)
        self._scx = U8()  # FF43: Bg viewport X position (R/W)
        self._ly = U8()  # FF44: LCD Y coordinate (R)
        self._lyc = U8()  # FF45: LY compare (R/W)
        self._bgp = U8(0xFC)  # FF47: BG palette data (R/W, DMG only)
        # FF48: OBJ palette 0 data (R/W, DMG only)
        self._obp0 = U8(0xFF)
        # FF49: OBJ palette 1 data (R/W, DMG only)
        self._obp1 = U8(0xFF)
        self._winy = U8()  # FF4A: Window Y position (R/W)
        self._winx = U8()  # FF4B: Window X position (R/W)
        self._bgp_index = np.array([0x11, 0x11, 0x11, 0x00], dtype=U8)
        self._obp_index0 = np.array([0x11, 0x11, 0x11, 0x11], dtype=U8)
        self._obp_index1 = np.array([0x11, 0x11, 0x11, 0x11], dtype=U8)

    def update_palette(self, value: U8, palette: U8Array):
        palette[3] = (value >> 6) & 3
        palette[2] = (value >> 4) & 3
        palette[1] = (value >> 2) & 3
        palette[0] = value & 3

    def read(self, address: U16) -> U8:
        if address == 0xFF40:
            return self._lcdc.value
        elif address == 0xFF41:
            return self._stat.value
        elif address == 0xFF42:
            return self._scy
        elif address == 0xFF43:
            return self._scx
        elif address == 0xFF44:
            return self._ly
        elif address == 0xFF45:
            return self._lyc
        elif address == 0xFF47:
            return self._bgp
        elif address == 0xFF48:
            return self._obp0
        elif address == 0xFF49:
            return self._obp1
        elif address == 0xFF4A:
            return self._winy
        elif address == 0xFF4B:
            return self._winx
        raise UnexpectedFallThroughError

    def write(self, address: U16, value: U8):
        if address == 0xFF40:
            self._lcdc.value = value
        elif address == 0xFF41:
            self._stat.value = value
        elif address == 0xFF42:
            self._scy = value
        elif address == 0xFF43:
            self._scx = value
        elif address == 0xFF44:
            raise ValueError('0xFF44 (LY) is readonly.')
        elif address == 0xFF45:
            self._lyc = value
        elif address == 0xFF47:
            self._bgp = value
            self.update_palette(value, self._bgp_index)
        elif address == 0xFF48:
            self._obp0 = value
            self.update_palette(value & U8(0xFC), self._obp_index0)
        elif address == 0xFF49:
            self._obp1 = value
            self.update_palette(value & U8(0xFC), self._obp_index1)
        elif address == 0xFF4A:
            self._winy = value
        elif address == 0xFF4B:
            self._winx = value
        else:
            raise UnexpectedFallThroughError(f'{address:04X} is not writable.')
