from typing import TYPE_CHECKING

from gameboy.common import concat, get_hi, get_lo
from gameboy.core import (
    AddrMode, ConditionType, InstrType, Instruction, Reg16Bit, RegType,
)
from gameboy.hardware.cpu.util import (
    ExecuteInfo, check_condition, jump, read_register, set_flags,
    write_register,
)

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU


def exec_call(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    address = info.data
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=True, cpu=cpu)


def exec_di(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.int_master_enabled = False


def exec_ld(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    if info.write_memory:
        if instr.reg_2 in Reg16Bit:
            cpu.emulate(1)
            cpu.write16(address=info.address, value=info.data)
        else:
            cpu.write(address=info.address, value=info.data)
        return
    if instr.addr_mode == AddrMode.HL_SPR:
        sp = read_register(instr.reg_2, cpu)
        e8 = info.data
        info.data = sp + (e8 ^ 0x80) - 0x80  # sp + e8
        flag_h = ((sp & 0xF) + (e8 & 0xF)) >= 0x10
        flag_c = ((sp & 0xFF) + (e8 & 0xFF)) >= 0x100
        set_flags(False, False, flag_h, flag_c, cpu)
        return
    write_register(instr.reg_1, info.data, cpu)


def exec_ldh(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    if instr.reg_1 == RegType.A:
        data = 0xFF00 | info.data
        cpu.reg_a = data
    else:
        cpu.write(address=info.address, value=cpu.reg_a)
    cpu.emulate(1)


def exec_jp(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    address = info.data
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=False, cpu=cpu)


def exec_jr(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    offset = ((info.data & 0xFF) ^ 0x80) - 0x80
    address = cpu.reg_pc + offset
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=False, cpu=cpu)


def exec_nop(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    pass


def exec_pop(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    lo = cpu.pop()
    cpu.emulate(1)
    hi = cpu.pop()
    cpu.emulate(1)
    value = concat(hi=hi, lo=lo)
    if instr.reg_1 == RegType.AF:
        cpu.reg_af = value & 0xFFF0
    else:
        write_register(reg_type=instr.reg_1, value=value, cpu=cpu)


def exec_push(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    hi = get_hi(read_register(reg_type=instr.reg_1, cpu=cpu))
    cpu.emulate(1)
    cpu.push(hi)
    lo = get_lo(read_register(reg_type=instr.reg_1, cpu=cpu))
    cpu.emulate(1)
    cpu.push(lo)
    cpu.emulate(1)


def exec_ret(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    if instr.cond_type != ConditionType.NONE:
        cpu.emulate(1)
    if check_condition(instr.cond_type, cpu=cpu):
        lo = cpu.pop()
        cpu.emulate(1)
        hi = cpu.pop()
        cpu.emulate(1)
        cpu.reg_pc = concat(hi=hi, lo=lo)
        cpu.emulate(1)


def exec_reti(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.int_master_enabled = True
    exec_ret(instr=instr, info=info, cpu=cpu)


def exec_rst(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    address = instr.param
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=True, cpu=cpu)


def exec_xor(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.reg_a ^= info.data
    set_flags(cpu.reg_a == 0, False, False, False, cpu)


handler_mapping = {
    InstrType.CALL: exec_call,
    InstrType.DI: exec_di,
    InstrType.LD: exec_ld,
    InstrType.LDH: exec_ldh,
    InstrType.JP: exec_jp,
    InstrType.JR: exec_jr,
    InstrType.NOP: exec_nop,
    InstrType.POP: exec_pop,
    InstrType.PUSH: exec_push,
    InstrType.RET: exec_ret,
    InstrType.RETI: exec_reti,
    InstrType.RST: exec_rst,
    InstrType.XOR: exec_xor,
}


def execute(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    handler = handler_mapping.get(instr.instr_type)
    if handler is None:
        raise NotImplementedError(f'{instr.instr_type}')
    return handler(instr, info, cpu)
