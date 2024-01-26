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
        self._value = new_value


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
