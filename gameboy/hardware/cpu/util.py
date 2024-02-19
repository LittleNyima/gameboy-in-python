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
    address: int = 0
    write_memory: bool = False


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


def write_register(reg_type: RegType, value: int, cpu: 'CPU') -> None:
    if reg_type == RegType.A:
        cpu.reg_a = value
    elif reg_type == RegType.AF:
        cpu.reg_af = value
    elif reg_type == RegType.B:
        cpu.reg_b = value
    elif reg_type == RegType.BC:
        cpu.reg_bc = value
    elif reg_type == RegType.C:
        cpu.reg_c = value
    elif reg_type == RegType.D:
        cpu.reg_d = value
    elif reg_type == RegType.DE:
        cpu.reg_de = value
    elif reg_type == RegType.E:
        cpu.reg_e = value
    elif reg_type == RegType.H:
        cpu.reg_h = value
    elif reg_type == RegType.HL:
        cpu.reg_hl = value
    elif reg_type == RegType.L:
        cpu.reg_l = value
    elif reg_type == RegType.PC:
        cpu.reg_pc = value
    elif reg_type == RegType.SP:
        cpu.reg_sp = value
    elif reg_type != RegType.NONE:
        raise UnexpectedFallThrough(f'{reg_type}')


def fetch_info(instr: Instruction, cpu: 'CPU') -> ExecuteInfo:
    if instr.addr_mode == AddrMode.IMP:
        return ExecuteInfo()
    elif instr.addr_mode == AddrMode.A8_R:
        address = cpu.read(cpu.reg_pc) | 0xFF00
        cpu.emulate(1)
        cpu.reg_pc += 1
        return ExecuteInfo(address=address, write_memory=True)
    elif instr.addr_mode in (AddrMode.A16_R, AddrMode.D16_R):
        lo = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        hi = cpu.read(cpu.reg_pc + 1)
        cpu.emulate(1)
        address = concat(hi=hi, lo=lo)
        cpu.reg_pc += 2
        data = read_register(reg_type=instr.reg_2, cpu=cpu)
        return ExecuteInfo(data=data, address=address, write_memory=True)
    elif instr.addr_mode == AddrMode.D8:
        data = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        cpu.reg_pc += 1
        return ExecuteInfo(data=data)
    elif instr.addr_mode in (AddrMode.D16, AddrMode.R_D16):
        lo = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        hi = cpu.read(cpu.reg_pc + 1)
        cpu.emulate(1)
        data = concat(hi=hi, lo=lo)
        cpu.reg_pc += 2
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.HL_SPR:
        data = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        cpu.reg_pc += 1
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.HLD_R:
        data = read_register(reg_type=instr.reg_2, cpu=cpu)
        address = read_register(reg_type=instr.reg_1, cpu=cpu)
        cpu.reg_hl -= 1
        return ExecuteInfo(data=data, address=address, write_memory=True)
    elif instr.addr_mode == AddrMode.HLI_R:
        data = read_register(reg_type=instr.reg_2, cpu=cpu)
        address = read_register(reg_type=instr.reg_1, cpu=cpu)
        cpu.reg_hl += 1
        return ExecuteInfo(data=data, address=address, write_memory=True)
    elif instr.addr_mode == AddrMode.MR:
        address = read_register(reg_type=instr.reg_1, cpu=cpu)
        data = cpu.read(address=address)
        cpu.emulate(1)
        return ExecuteInfo(data=data, address=address, write_memory=True)
    elif instr.addr_mode == AddrMode.MR_D8:
        data = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        cpu.reg_pc += 1
        address = read_register(reg_type=instr.reg_1, cpu=cpu)
        return ExecuteInfo(data=data, address=address, write_memory=True)
    elif instr.addr_mode == AddrMode.MR_R:
        data = read_register(reg_type=instr.reg_2, cpu=cpu)
        address = read_register(reg_type=instr.reg_1, cpu=cpu)
        if instr.reg_1 == RegType.C:
            address |= 0xFF00
        return ExecuteInfo(data=data, address=address, write_memory=True)
    elif instr.addr_mode == AddrMode.R:
        data = read_register(reg_type=instr.reg_1, cpu=cpu)
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_A8:
        data = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        cpu.reg_pc += 1
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_A16:
        lo = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        hi = cpu.read(cpu.reg_pc + 1)
        cpu.emulate(1)
        address = concat(hi=hi, lo=lo)
        cpu.reg_pc += 2
        data = cpu.read(address=address)
        cpu.emulate(1)
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_D8:
        data = cpu.read(cpu.reg_pc)
        cpu.emulate(1)
        cpu.reg_pc += 1
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_HLD:
        address = read_register(reg_type=instr.reg_2, cpu=cpu)
        data = cpu.read(address=address)
        cpu.emulate(1)
        cpu.reg_hl -= 1
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_HLI:
        address = read_register(reg_type=instr.reg_2, cpu=cpu)
        data = cpu.read(address=address)
        cpu.emulate(1)
        cpu.reg_hl += 1
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_MR:
        address = read_register(reg_type=instr.reg_2, cpu=cpu)
        if instr.reg_2 == RegType.C:
            address |= 0xFF00
        data = cpu.read(address=address)
        cpu.emulate(1)
        return ExecuteInfo(data=data)
    elif instr.addr_mode == AddrMode.R_R:
        data = read_register(reg_type=instr.reg_2, cpu=cpu)
        return ExecuteInfo(data=data)
    raise UnexpectedFallThrough


def jump(
    address: int,
    condition: ConditionType,
    save_context: bool,
    cpu: 'CPU',
) -> None:
    if check_condition(cond_type=condition, cpu=cpu):
        if save_context:
            cpu.emulate(2)
            cpu.push16(cpu.reg_pc)
        cpu.reg_pc = address
        cpu.emulate(1)


def fetch_instruction(cpu: 'CPU') -> Instruction:
    opcode = cpu.read(cpu.reg_pc)
    cpu.reg_pc += 1
    return decode_instruction(opcode=opcode)
