from gameboy.common.typings import U8, U16
from gameboy.hardware.cpu_utils import get_hi, get_lo, set_hi, set_lo


class Register:

    def __init__(self, value: U16 = U16(0x0)):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: U16):
        self._value = U16(new_value)


class Register8Bit:

    def __init__(self, value: U8 = U8(0x0)):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value: U8):
        self._value = U8(new_value)


class InterruptRegister(Register):
    '''Register for interrupt support.

    Layout
    ------
        +----------------------------------------------+
        |             IF - Interrupt Flag              |
        | FED |   C    |    B   |   A   |  9  |   8    |
        |     | Joypad | Serial | Timer | LCD | VBlank |
        +----------------------------------------------+
        |            IE - Interrupt Enable             |
        | 765 |   4    |    3   |   2   |  1  |   0    |
        |     | Joypad | Serial | Timer | LCD | VBlank |
        +----------------------------------------------+
    '''

    def __init__(self, value: U16 = U16(0x0)):
        super().__init__(value)

    @property
    def int_flag(self):
        return get_hi(self.value)

    @int_flag.setter
    def int_flag(self, new_value: U8):
        self.value = set_hi(self.value, new_value)

    @property
    def int_enable(self):
        return get_lo(self.value)

    @int_enable.setter
    def int_enable(self, new_value: U8):
        self.value = set_lo(self.value, new_value)


class LCDC(Register8Bit):

    @property
    def lcd_ppu_enable(self):
        return U8((self.value >> 7) & 0x1)

    @property
    def window_tile_map(self):
        return U8((self.value >> 6) & 0x1)

    @property
    def window_enable(self):
        return U8((self.value >> 5) & 0x1)

    @property
    def bg_window_tiles(self):
        return U8((self.value >> 4) & 0x1)

    @property
    def bg_tile_map(self):
        return U8((self.value >> 3) & 0x1)

    @property
    def obj_size(self):
        return U8((self.value >> 2) & 0x1)

    @property
    def obj_enable(self):
        return U8((self.value >> 1) & 0x1)

    @property
    def bg_window_enable(self):
        return U8(self.value & 0x1)

    @property
    def bg_window_priority(self):
        return self.bg_window_enable


class STAT(Register8Bit):

    @property
    def lyc_int_select(self):
        return U8((self.value >> 6) & 0x1)

    @property
    def mode_2_int_select(self):
        return U8((self.value >> 5) & 0x1)

    @property
    def mode_1_int_select(self):
        return U8((self.value >> 4) & 0x1)

    @property
    def mode_0_int_select(self):
        return U8((self.value >> 3) & 0x1)

    @property
    def lyc_equals_ly(self):
        return U8((self.value >> 2) & 0x1)

    def set_lyc_equals_ly(self):
        self.value |= U8(0b0000_0100)

    def reset_lyc_equals_ly(self):
        self.value &= U8(0b1111_1011)

    @property
    def ppu_mode(self):
        return U8(self.value & 0x3)
