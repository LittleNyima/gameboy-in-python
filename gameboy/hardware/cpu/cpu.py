from typing import TYPE_CHECKING

from gameboy.common import (
    concat, get_bit, get_hi, get_lo, get_logger, set_bit, set_hi, set_lo,
)
from gameboy.core import InterruptType
from gameboy.hardware.cpu.execute import execute
from gameboy.hardware.cpu.util import fetch_info, fetch_instruction

if TYPE_CHECKING:
    from gameboy.hardware.motherboard import Motherboard


logger = get_logger(file=__file__)


class CPU:

    def __init__(self, motherboard: 'Motherboard'):
        # we skip boot loader at this point
        self.af = 0x01B0
        self.bc = 0x0013
        self.de = 0x00D8
        self.hl = 0x014D
        self.sp = 0xFEFF
        self.pc = 0x100

        self.motherboard = motherboard
        self.bus = motherboard.bus
        self.timer = motherboard.timer

        self.halted: bool = False
        self.int_master_enabled: bool = False
        self.int_enable_register: int = 0
        self.int_flags_register: int = 0
        self.enabling_ime: bool = False
        self.timer.div = 0xABCC

    def tick(self):
        if not self.halted:
            instr = fetch_instruction(cpu=self)
            self.emulate(1)
            info = fetch_info(instr=instr, cpu=self)
            execute(instr=instr, info=info, cpu=self)
        else:  # halted
            self.emulate(1)
            if self.int_flags_register:
                self.halted = False
        if self.int_master_enabled:
            self.handle_interrupts()
            self.enabling_ime = False
        if self.enabling_ime:
            self.int_master_enabled = True

    def handle_interrupt(self, address: int, int_type: InterruptType):
        if (
            self.int_enable_register & int_type.value
            and self.int_flags_register & int_type.value
        ):
            # Jump to interrupt handler
            self.push16(self.reg_pc)
            self.reg_pc = address
            # Set flags
            self.int_flags_register &= ~int_type.value
            self.halted = False
            self.int_master_enabled = False
            return True
        return False

    def handle_interrupts(self):
        if self.handle_interrupt(0x40, InterruptType.VBLANK):
            return
        elif self.handle_interrupt(0x48, InterruptType.LCD_STAT):
            return
        elif self.handle_interrupt(0x50, InterruptType.TIMER):
            return
        elif self.handle_interrupt(0x58, InterruptType.SERIAL):
            return
        elif self.handle_interrupt(0x60, InterruptType.JOYPAD):
            return

    def request_interrupt(self, int_type: InterruptType):
        self.int_flags_register |= int_type.value

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
        self.write(address=address, value=get_lo(value))
        self.write(address=address + 1, value=get_hi(value))

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
        return get_hi(self.reg_af)

    @reg_a.setter
    def reg_a(self, new_value: int):
        self.reg_af = set_hi(hi=new_value, value=self.reg_af)

    @property
    def reg_b(self):
        return get_hi(self.reg_bc)

    @reg_b.setter
    def reg_b(self, new_value: int):
        self.reg_bc = set_hi(hi=new_value, value=self.reg_bc)

    @property
    def reg_c(self):
        return get_lo(self.reg_bc)

    @reg_c.setter
    def reg_c(self, new_value: int):
        self.reg_bc = set_lo(lo=new_value, value=self.reg_bc)

    @property
    def reg_d(self):
        return get_hi(self.reg_de)

    @reg_d.setter
    def reg_d(self, new_value: int):
        self.reg_de = set_hi(hi=new_value, value=self.reg_de)

    @property
    def reg_e(self):
        return get_lo(self.reg_de)

    @reg_e.setter
    def reg_e(self, new_value: int):
        self.reg_de = set_lo(lo=new_value, value=self.reg_de)

    @property
    def reg_h(self):
        return get_hi(self.reg_hl)

    @reg_h.setter
    def reg_h(self, new_value: int):
        self.reg_hl = set_hi(hi=new_value, value=self.reg_hl)

    @property
    def reg_l(self):
        return get_lo(self.reg_hl)

    @reg_l.setter
    def reg_l(self, new_value: int):
        self.reg_hl = set_lo(lo=new_value, value=self.reg_hl)

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
    def flag_z(self, new_value: bool):
        self.af = set_bit(bool(new_value), self.af, 7)

    @property
    def flag_n(self):
        return get_bit(self.af, 6)

    @flag_n.setter
    def flag_n(self, new_value: bool):
        self.af = set_bit(bool(new_value), self.af, 6)

    @property
    def flag_h(self):
        return get_bit(self.af, 5)

    @flag_h.setter
    def flag_h(self, new_value: bool):
        self.af = set_bit(bool(new_value), self.af, 5)

    @property
    def flag_c(self):
        return get_bit(self.af, 4)

    @flag_c.setter
    def flag_c(self, new_value: bool):
        self.af = set_bit(bool(new_value), self.af, 4)
