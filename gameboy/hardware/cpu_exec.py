from typing import TYPE_CHECKING

from gameboy.common.errors import UnexpectedFallThroughError
from gameboy.common.typings import U8, U16
from gameboy.core.instructions import InstrType, Instruction, OperandType
from gameboy.hardware.cpu_utils import (
    check_condition, is_value_u8, is_value_u16, log_cpu_status, log_instr,
    read_value_u8, read_value_u16, write_value_u8, write_value_u16,
)

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU


def execute_jp(cpu: 'CPU', instr: Instruction) -> int:
    if instr.operand0 == OperandType.A16:  # JP a16
        a16 = cpu.read_u16(cpu.reg_pc + U16(1))
        cpu.reg_pc = a16
        return instr.cycles[0]
    raise UnexpectedFallThroughError()


def execute_jr(cpu: 'CPU', instr: Instruction) -> int:
    i8 = cpu.read_i8(cpu.reg_pc + U16(1))
    jump = (
        instr.operand0 == OperandType.E8 or  # JR e8
        check_condition(instr.operand0, cpu)  # JR cc, e8
    )
    cpu.reg_pc += instr.bytes
    if jump:
        cpu.reg_pc = U16(cpu.reg_pc + i8)
        return instr.cycles[0]
    else:
        return instr.cycles[1]


def execute_ld(cpu: 'CPU', instr: Instruction) -> int:  # LD <o0> <o1>
    if is_value_u8(instr.operand0) and is_value_u8(instr.operand1):
        u8 = read_value_u8(instr.operand1, cpu)
        write_value_u8(instr.operand0, cpu, u8)
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    if is_value_u16(instr.operand0) and is_value_u16(instr.operand1):
        u16 = read_value_u16(instr.operand1, cpu)
        write_value_u16(instr.operand0, cpu, u16)
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    raise UnexpectedFallThroughError()


def execute_none(cpu: 'CPU', instr: Instruction):
    raise RuntimeError('Unexpected instruction NONE.')


def execute_nop(cpu: 'CPU', instr: Instruction) -> int:  # NOP
    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


def execute_set(cpu: 'CPU', instr: Instruction) -> int:
    if instr.operand1.value.immediate:  # SET u3, r8
        u8 = read_value_u8(instr.operand1, cpu)
        onehot = U8(1 << int(instr.operand0.value.name))
        write_value_u8(instr.operand1, cpu, u8 | onehot)
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    raise UnexpectedFallThroughError


def execute_xor(cpu: 'CPU', instr: Instruction) -> int:  # XOR
    u8 = read_value_u8(instr.operand1, cpu)
    r = cpu.reg_a ^ u8
    if r == 0x0:
        cpu.set_flag_z()
    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


executor_mapping = {
    InstrType.LD: execute_ld,
    InstrType.JP: execute_jp,
    InstrType.JR: execute_jr,
    InstrType.NONE: execute_none,
    InstrType.NOP: execute_nop,
    InstrType.SET: execute_set,
    InstrType.XOR: execute_xor,
}


def execute(cpu: 'CPU', instr: Instruction):
    log_instr(cpu=cpu, instr=instr)
    log_cpu_status(cpu=cpu, when='before')
    executor = executor_mapping.get(instr.mnemonic)
    if executor is None:
        raise NotImplementedError(f'Not implemented instr {instr}.')
    r = executor(cpu=cpu, instr=instr)
    log_cpu_status(cpu=cpu, when='after')
    return r
