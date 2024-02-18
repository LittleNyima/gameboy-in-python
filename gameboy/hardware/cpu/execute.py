from typing import TYPE_CHECKING

from gameboy.core import AddrMode, InstrType, Instruction, Reg16Bit
from gameboy.hardware.cpu.util import (
    ExecuteInfo, check_condition, read_register, set_flags, write_register,
)

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU


def exec_di(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.int_master_enabled = False


def exec_ld(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    if info.write_memory:
        if instr.reg_2 in Reg16Bit:
            cpu.emulate(1)
            cpu.write16(address=info.address, value=info.data)
        else:
            cpu.write(address=info.address, value=info.data)
    if instr.addr_mode == AddrMode.HL_SPR:
        sp = read_register(instr.reg_2, cpu)
        e8 = info.data
        info.data = sp + (e8 ^ 0x80) - 0x80  # sp + e8
        flag_h = ((sp & 0xF) + (e8 & 0xF)) >= 0x10
        flag_c = ((sp & 0xFF) + (e8 & 0xFF)) >= 0x100
        set_flags(False, False, flag_h, flag_c, cpu)
    write_register(instr.reg_1, info.data, cpu)


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
    InstrType.LD: exec_ld,
    InstrType.JP: exec_jp,
    InstrType.NOP: exec_nop,
    InstrType.XOR: exec_xor,
}


def execute(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    handler = handler_mapping.get(instr.instr_type)
    if handler is None:
        raise NotImplementedError(f'{instr.instr_type}')
    return handler(instr, info, cpu)
