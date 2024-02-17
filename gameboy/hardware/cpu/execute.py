from typing import TYPE_CHECKING

from gameboy.core import InstrType, Instruction
from gameboy.hardware.cpu.util import ExecuteInfo, check_condition, set_flags

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU


def exec_di(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.int_master_enabled = False


def exec_jp(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    if check_condition(instr.cond_type, cpu):
        cpu.reg_pc = info.data
        cpu.emulate(1)


def exec_nop(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    pass


def exec_xor(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.reg_a ^= info.data
    set_flags(cpu.reg_a == 0, False, False, False, cpu)


handler_mapping = {
    InstrType.DI: exec_di,
    InstrType.JP: exec_jp,
    InstrType.NOP: exec_nop,
    InstrType.XOR: exec_xor,
}


def execute(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    handler = handler_mapping.get(instr.instr_type)
    if handler is None:
        raise NotImplementedError(f'{instr.instr_type}')
    return handler(instr, info, cpu)
