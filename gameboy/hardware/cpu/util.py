from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from gameboy.common import UnexpectedFallThrough, concat
from gameboy.core import (
    AddrMode, ConditionType, Instruction, RegType, decode_instruction,
)

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU


@dataclass
class ExecuteInfo:
    data: int = 0


def check_condition(cond_type: ConditionType, cpu: 'CPU') -> bool:
    if cond_type == ConditionType.NONE:
        return True
    elif cond_type == ConditionType.C:
        return cpu.flag_c
    elif cond_type == ConditionType.NC:
        return not cpu.flag_c
    elif cond_type == ConditionType.Z:
        return cpu.flag_z
    elif cond_type == ConditionType.NZ:
        return not cpu.flag_z
    raise UnexpectedFallThrough


def set_flags(
    z: Optional[bool],
    n: Optional[bool],
    h: Optional[bool],
    c: Optional[bool],
    cpu: 'CPU',
) -> None:
    if z is not None:
        cpu.flag_z = z
    if n is not None:
        cpu.flag_n = n
    if h is not None:
        cpu.flag_h = h
    if c is not None:
        cpu.flag_c = c


def read_register(reg_type: RegType, cpu: 'CPU') -> int:
    if reg_type == RegType.A:
        return cpu.reg_a
    elif reg_type == RegType.AF:
        return cpu.reg_af
    elif reg_type == RegType.B:
        return cpu.reg_b
    elif reg_type == RegType.BC:
        return cpu.reg_bc
    elif reg_type == RegType.C:
        return cpu.reg_c
    elif reg_type == RegType.D:
        return cpu.reg_d
    elif reg_type == RegType.DE:
        return cpu.reg_de
    elif reg_type == RegType.E:
        return cpu.reg_e
    elif reg_type == RegType.H:
        return cpu.reg_h
    elif reg_type == RegType.HL:
        return cpu.reg_hl
    elif reg_type == RegType.L:
        return cpu.reg_l
    elif reg_type == RegType.PC:
        return cpu.reg_pc
    elif reg_type == RegType.SP:
        return cpu.reg_sp
    raise UnexpectedFallThrough


def fetch_info(instr: Instruction, cpu: 'CPU') -> ExecuteInfo:
    if instr.addr_mode == AddrMode.IMP:
        return ExecuteInfo()
    elif instr.addr_mode == AddrMode.R:
        data = read_register(reg_type=instr.reg_1, cpu=cpu)
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_D8:
        data = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        cpu.reg_pc += 1
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.D16:
        lo = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        hi = cpu.read(cpu.reg_pc + 1)
        cpu.emulate(1)
        data = concat(hi=hi, lo=lo)
        cpu.reg_pc += 2
        return ExecuteInfo(data=data)
    raise UnexpectedFallThrough


def fetch_instruction(cpu: 'CPU'):
    opcode = cpu.read(cpu.reg_pc)
    cpu.reg_pc += 1
    return decode_instruction(opcode=opcode)
