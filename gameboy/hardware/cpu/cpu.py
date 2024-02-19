from typing import TYPE_CHECKING, Any

from gameboy.common import (
    concat, get_bit, get_hi, get_lo, get_logger, set_bit, set_hi, set_lo,
)
from gameboy.hardware.cpu.execute import execute
from gameboy.hardware.cpu.util import fetch_info, fetch_instruction

if TYPE_CHECKING:
    from gameboy.hardware.motherboard import Motherboard


logger = get_logger(file=__file__)


class CPU:

    def __init__(self, motherboard: 'Motherboard'):
        self.af = 0
        self.bc = 0
        self.de = 0
        self.hl = 0
        self.sp = 0
        self.pc = 0x100

        self.motherboard = motherboard
        self.bus = motherboard.bus

        self.halted: bool = False
        self.int_master_enabled: bool = False
        self.int_enable_register: int = 0

    def tick(self):
        if not self.halted:
            opcode = self.read(self.reg_pc)
            pc = self.reg_pc
            lo = self.read(self.reg_pc + 1)
            hi = self.read(self.reg_pc + 2)
            instr = fetch_instruction(cpu=self)
            self.emulate(1)
            logger.debug(
                f'{pc:04X}: {str(instr):4s} '
                f'({opcode=:02X}, {lo=:02X}, {hi=:02X}) '
                f'A: {self.reg_a:02X} BC: {self.reg_bc:04X} '
                f'DE: {self.reg_de:04X} HL: {self.reg_hl:04X}',
            )
            info = fetch_info(instr=instr, cpu=self)
            execute(instr=instr, info=info, cpu=self)

    def emulate(self, cycles: int) -> None:
        return self.motherboard.emulate(cycles=cycles)

    def read(self, address: int) -> int:
        return self.bus.read(address=address)

    def read16(self, address: int) -> int:
        lo = self.read(address=address)
        hi = self.read(address=address + 1)
        return concat(hi=hi, lo=lo)

    def write(self, address: int, value: int) -> None:
        return self.bus.write(address=address, value=value)

    def write16(self, address: int, value: int) -> None:
        self.write(address=address, value=get_hi(value))
        self.write(address=address + 1, value=get_lo(value))

    def pop(self) -> int:
        value = self.read(self.reg_sp)
        self.reg_sp += 1
        return value

    def pop16(self) -> int:
        lo = self.pop()
        hi = self.pop()
        return concat(hi=hi, lo=lo)

    def push(self, value: int) -> None:
        self.reg_sp -= 1
        self.write(address=self.reg_sp, value=value)

    def push16(self, value: int) -> None:
        self.push(get_hi(value))
        self.push(get_lo(value))

    @property
    def reg_a(self):
        return get_hi(self.af)

    @reg_a.setter
    def reg_a(self, new_value: int):
        self.af = set_hi(hi=new_value, value=self.af)

    @property
    def reg_b(self):
        return get_hi(self.bc)

    @reg_b.setter
    def reg_b(self, new_value: int):
        self.bc = set_hi(hi=new_value, value=self.bc)

    @property
    def reg_c(self):
        return get_lo(self.bc)

    @reg_c.setter
    def reg_c(self, new_value: int):
        self.bc = set_lo(lo=new_value, value=self.bc)

    @property
    def reg_d(self):
        return get_hi(self.de)

    @reg_d.setter
    def reg_d(self, new_value: int):
        self.de = set_hi(hi=new_value, value=self.de)

    @property
    def reg_e(self):
        return get_lo(self.de)

    @reg_e.setter
    def reg_e(self, new_value: int):
        self.de = set_lo(lo=new_value, value=self.de)

    @property
    def reg_h(self):
        return get_hi(self.hl)

    @reg_h.setter
    def reg_h(self, new_value: int):
        self.hl = set_hi(hi=new_value, value=self.hl)

    @property
    def reg_l(self):
        return get_lo(self.hl)

    @reg_l.setter
    def reg_l(self, new_value: int):
        self.hl = set_lo(lo=new_value, value=self.hl)

    @property
    def reg_af(self):
        return self.af

    @reg_af.setter
    def reg_af(self, new_value: int):
        self.af = new_value & 0xFFFF

    @property
    def reg_bc(self):
        return self.bc

    @reg_bc.setter
    def reg_bc(self, new_value: int):
        self.bc = new_value & 0xFFFF

    @property
    def reg_de(self):
        return self.de

    @reg_de.setter
    def reg_de(self, new_value: int):
        self.de = new_value & 0xFFFF

    @property
    def reg_hl(self):
        return self.hl

    @reg_hl.setter
    def reg_hl(self, new_value: int):
        self.hl = new_value & 0xFFFF

    @property
    def reg_sp(self):
        return self.sp

    @reg_sp.setter
    def reg_sp(self, new_value: int):
        self.sp = new_value & 0xFFFF

    @property
    def reg_pc(self):
        return self.pc

    @reg_pc.setter
    def reg_pc(self, new_value: int):
        self.pc = new_value & 0xFFFF

    @property
    def flag_z(self):
        return get_bit(self.af, 7)

    @flag_z.setter
    def flag_z(self, new_value: Any):
        self.af = set_bit(bool(new_value), self.af, 7)

    @property
    def flag_n(self):
        return get_bit(self.af, 7)

    @flag_n.setter
    def flag_n(self, new_value: Any):
        self.af = set_bit(bool(new_value), self.af, 6)

    @property
    def flag_h(self):
        return get_bit(self.af, 7)

    @flag_h.setter
    def flag_h(self, new_value: Any):
        self.af = set_bit(bool(new_value), self.af, 5)

    @property
    def flag_c(self):
        return get_bit(self.af, 7)

    @flag_c.setter
    def flag_c(self, new_value: Any):
        self.af = set_bit(bool(new_value), self.af, 4)
