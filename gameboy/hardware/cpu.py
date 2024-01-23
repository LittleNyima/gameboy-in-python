from gameboy.common.loggings import get_logger
from gameboy.common.typings import U8, U16
from gameboy.core.device import BaseDevice
from gameboy.core.instructions import decode_opcode
from gameboy.hardware.bus import Bus

logger = get_logger(file=__file__)


def get_hi(value: U16) -> U8:
    return U8(value >> 8)


def get_lo(value: U16) -> U8:
    return U8(value)


def set_hi(value: U16, hi: U8) -> U16:
    _hi = U16(hi) << 8
    _lo = value & 0xFF
    return U16(_lo | _hi)


def set_lo(value: U16, lo: U8) -> U16:
    hi = value & 0xFF00
    return U16(hi | U16(lo))


class CPU(BaseDevice):

    def __init__(self, bus: Bus):
        # registers
        self._reg_af = U16()
        self._reg_bc = U16()
        self._reg_de = U16()
        self._reg_hl = U16()
        self._reg_sp = U16()
        self._reg_pc = U16()

        self._bus = bus

    def fetch_and_execute(self):
        opcode = self._bus.read(self.reg_pc)
        if opcode == 0xCB:
            opcode = self._bus.read(self.reg_pc)
            instr = decode_opcode(opcode, True)
        else:
            instr = decode_opcode(opcode, False)
        logger.debug(f'Read {instr} ({opcode:08b}) at {self.reg_pc}')

    def step(self):
        self.fetch_and_execute()

    @property
    def reg_af(self) -> U16:
        return self._reg_af

    @reg_af.setter
    def reg_af(self, value: U16):
        self._reg_af = value

    @property
    def reg_bc(self) -> U16:
        return self._reg_bc

    @reg_bc.setter
    def reg_bc(self, value: U16):
        self._reg_bc = value

    @property
    def reg_de(self) -> U16:
        return self._reg_de

    @reg_de.setter
    def reg_de(self, value: U16):
        self._reg_de = value

    @property
    def reg_hl(self) -> U16:
        return self._reg_hl

    @reg_hl.setter
    def reg_hl(self, value: U16):
        self._reg_hl = value

    @property
    def reg_sp(self) -> U16:
        return self._reg_sp

    @reg_sp.setter
    def reg_sp(self, value: U16):
        self._reg_sp = value

    @property
    def reg_pc(self) -> U16:
        return self._reg_pc

    @reg_pc.setter
    def reg_pc(self, value: U16):
        self._reg_pc = value

    @property
    def reg_a(self) -> U8:
        return get_hi(self.reg_af)

    @reg_a.setter
    def reg_a(self, value: U8):
        self.reg_af = set_hi(self.reg_af, value)

    @property
    def reg_f(self) -> U8:
        return get_lo(self.reg_af)

    @reg_f.setter
    def reg_f(self, value: U8):
        self.reg_af = set_lo(self.reg_af, value)

    @property
    def reg_b(self) -> U8:
        return get_hi(self.reg_bc)

    @reg_b.setter
    def reg_b(self, value: U8):
        self.reg_bc = set_hi(self.reg_bc, value)

    @property
    def reg_c(self) -> U8:
        return get_lo(self.reg_bc)

    @reg_c.setter
    def reg_c(self, value: U8):
        self.reg_bc = set_lo(self.reg_bc, value)

    @property
    def reg_d(self) -> U8:
        return get_hi(self.reg_de)

    @reg_d.setter
    def reg_d(self, value: U8):
        self.reg_de = set_hi(self.reg_de, value)

    @property
    def reg_e(self) -> U8:
        return get_lo(self.reg_de)

    @reg_e.setter
    def reg_e(self, value: U8):
        self.reg_de = set_lo(self.reg_de, value)

    @property
    def reg_h(self) -> U8:
        return get_hi(self.reg_hl)

    @reg_h.setter
    def reg_h(self, value: U8):
        self.reg_hl = set_hi(self.reg_hl, value)

    @property
    def reg_l(self) -> U8:
        return get_lo(self.reg_hl)

    @reg_l.setter
    def reg_l(self, value: U8):
        self.reg_hl = set_lo(self.reg_hl, value)

    @property
    def flag_z(self) -> U8:
        return U8((self.reg_f >> 7) & 0x1)

    def set_flag_z(self):
        self.reg_f |= 0b1000_0000

    def reset_flag_z(self):
        self.reg_f &= 0b0111_1111

    @property
    def flag_n(self) -> U8:
        return U8((self.reg_f >> 6) & 0x1)

    def set_flag_n(self):
        self.reg_f |= 0b0100_0000

    def reset_flag_n(self):
        self.reg_f &= 0b1011_1111

    @property
    def flag_h(self) -> U8:
        return U8((self.reg_f >> 5) & 0x1)

    def set_flag_h(self):
        self.reg_f |= 0b0010_0000

    def reset_flag_h(self):
        self.reg_f &= 0b1101_1111

    @property
    def flag_c(self) -> U8:
        return U8((self.reg_f >> 4) & 0x1)

    def set_flag_c(self):
        self.reg_f |= 0b0001_0000

    def reset_flag_c(self):
        self.reg_f &= 0b1110_1111
