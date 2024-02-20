from typing import TYPE_CHECKING, Optional

from gameboy.common import UnexpectedFallThrough, concat, get_hi, get_lo
from gameboy.core import (
    REG_16BIT, REG_LOOKUP, AddrMode, ConditionType, InstrType, Instruction,
    RegType,
)
from gameboy.hardware.cpu.util import (
    ExecuteInfo, check_condition, jump, read_register, read_register_cb,
    set_flags, write_register, write_register_cb,
)

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU


def exec_adc(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    d = info.data
    a = cpu.reg_a
    c = cpu.flag_c
    cpu.reg_a = d + a + c
    flag_z = cpu.reg_a == 0
    flag_h = (d & 0xF) + (a & 0xF) + c > 0xF
    flag_c = d + a + c > 0xFF
    set_flags(flag_z, False, flag_h, flag_c, cpu=cpu)


def exec_add(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    r1 = read_register(instr.reg_1, cpu=cpu)
    value = r1 + info.data
    if instr.reg_1 in REG_16BIT:
        cpu.emulate(1)
    if instr.reg_1 == RegType.SP:
        value = cpu.reg_sp + (info.data ^ 0x80) - 0x80
    flag_z: Optional[bool] = value & 0xFF == 0  # make mypy happy
    flag_h = (r1 & 0xF) + (info.data & 0xF) >= 0x10
    flag_c = (r1 & 0xFF) + (info.data & 0xFF) >= 0x100
    if instr.reg_1 in REG_16BIT and instr.reg_1 != RegType.SP:
        flag_z = None
        flag_h = (r1 & 0xFFF) + (info.data & 0xFFF) >= 0x1000
        flag_c = r1 + info.data >= 0x10000
    if instr.reg_1 == RegType.SP:
        flag_z = False
    write_register(reg_type=instr.reg_1, value=value, cpu=cpu)
    set_flags(flag_z, False, flag_h, flag_c, cpu=cpu)


def exec_and(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.reg_a &= info.data
    set_flags(cpu.reg_a == 0, False, True, False, cpu)


def exec_call(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    address = info.data
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=True, cpu=cpu)


def exec_cb(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    opcode = info.data
    reg_type = REG_LOOKUP[opcode & 0x7]
    bit = (opcode >> 3) & 0x7
    op_type = (opcode >> 6) & 0x3
    reg_val = read_register_cb(reg_type=reg_type, cpu=cpu)
    cycles = 3 if reg_type == RegType.HL else 1
    cpu.emulate(cycles=cycles)
    if op_type == 0x1:  # BIT
        z_flag = reg_val & (1 << bit) == 0
        set_flags(z_flag, False, True, None, cpu=cpu)
    elif op_type == 0x2:  # RES
        reg_val &= ~(1 << bit)
        write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
    elif op_type == 0x3:  # SET
        reg_val |= (1 << bit)
        write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
    else:
        op_type = bit
        flag_c = cpu.flag_c
        msb = (reg_val >> 7) & 0x1
        lsb = reg_val & 0x1
        if op_type == 0x0:  # RLC
            reg_val = ((reg_val << 1) & 0xFE) | msb
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, bool(msb), cpu=cpu)
        elif op_type == 0x1:  # RRC
            reg_val = ((reg_val >> 1) & 0x7F) | (lsb << 7)
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, bool(lsb), cpu=cpu)
        elif op_type == 0x2:  # RL
            reg_val = ((reg_val << 1) & 0xFE) | flag_c
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, bool(msb), cpu=cpu)
        elif op_type == 0x3:  # RR
            reg_val = ((reg_val >> 1) & 0x7F) | (flag_c << 7)
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, bool(lsb), cpu=cpu)
        elif op_type == 0x4:  # SLA
            reg_val = (reg_val << 1) & 0xFE
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, bool(msb), cpu=cpu)
        elif op_type == 0x5:  # SRA
            reg_val = ((reg_val >> 1) & 0x7F) | (reg_val & 0x80)
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, bool(lsb), cpu=cpu)
        elif op_type == 0x6:  # SWAP
            reg_val = concat(hi=get_lo(reg_val), lo=get_hi(reg_val))
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, False, cpu=cpu)
        elif op_type == 0x7:  # SRL
            reg_val >>= 1
            write_register_cb(reg_type=reg_type, value=reg_val, cpu=cpu)
            set_flags(reg_val == 0, False, False, bool(lsb), cpu=cpu)
    raise UnexpectedFallThrough


def exec_ccf(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    set_flags(None, False, False, not cpu.flag_c, cpu=cpu)


def exec_cp(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cmp = cpu.reg_a - info.data
    flag_z = cmp == 0
    flag_h = (cpu.reg_a & 0xF) < (info.data & 0xF)
    flag_c = cmp < 0
    set_flags(flag_z, True, flag_h, flag_c, cpu=cpu)


def exec_cpl(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.reg_a = ~cpu.reg_a
    set_flags(None, True, True, None, cpu=cpu)


def exec_daa(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    """
    Decimal Adjust Accumulator (DAA) is used to get a correct binary-coded
    decimal representation after an arithemetic instruction. The method is
    to force the carry of a hexadecimal number by adding 6 to the position
    where it needs to be carried, resulting in the correct decimal number.

    For example, an arithemetic operation results in 53, which is supposed
    to be represented as 0x53. However, the operation produces 0x4D.So we
    add 6 (16 - 10) to this result to convert it to 0x53, which is the
    expected BCD representation.
    """
    add = 0
    flag_c = False
    if cpu.flag_h or (not cpu.flag_n and (cpu.reg_a & 0xF) > 0x9):
        add = 0x6
    if cpu.flag_c or (not cpu.flag_n and cpu.reg_a > 0x99):
        add |= 0x60
        flag_c = True
    cpu.reg_a += -add if cpu.flag_n else add
    set_flags(cpu.reg_a == 0, None, False, flag_c, cpu=cpu)


def exec_dec(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    value = read_register(reg_type=instr.reg_1, cpu=cpu) - 1
    if instr.reg_1 in REG_16BIT:
        cpu.emulate(1)
    if instr.reg_1 == RegType.HL and instr.addr_mode == AddrMode.MR:
        value = cpu.read(cpu.reg_hl) - 1
        cpu.write(cpu.reg_hl, value)
    else:
        write_register(reg_type=instr.reg_1, value=value, cpu=cpu)
        value = read_register(reg_type=instr.reg_1, cpu=cpu)
    if instr.opcode & 0xB != 0xB:  # Not DEC BC/DE/HL/SP
        set_flags(value == 0, False, value & 0xF == 0, None, cpu=cpu)


def exec_di(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.int_master_enabled = False


def exec_ei(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.enabling_ime = True


def exec_halt(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.halted = True


def exec_inc(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    value = read_register(reg_type=instr.reg_1, cpu=cpu) + 1
    if instr.reg_1 in REG_16BIT:
        cpu.emulate(1)
    if instr.reg_1 == RegType.HL and instr.addr_mode == AddrMode.MR:
        value = cpu.read(cpu.reg_hl) + 1
        cpu.write(cpu.reg_hl, get_lo(value))
    else:
        write_register(reg_type=instr.reg_1, value=value, cpu=cpu)
        value = read_register(reg_type=instr.reg_1, cpu=cpu)
    if instr.opcode & 0x3 != 0x3:  # Not INC BC/DE/HL/SP
        set_flags(value == 0, False, value & 0xF == 0, None, cpu=cpu)


def exec_jp(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    address = info.data
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=False, cpu=cpu)


def exec_jr(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    offset = ((info.data & 0xFF) ^ 0x80) - 0x80
    address = cpu.reg_pc + offset
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=False, cpu=cpu)


def exec_ld(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    if info.write_memory:
        if instr.reg_2 in REG_16BIT:
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


def exec_nop(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    pass


def exec_or(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.reg_a |= info.data
    set_flags(cpu.reg_a == 0, False, False, False, cpu)


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


def exec_rla(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    reg_val = cpu.reg_a
    msb = reg_val >> 7
    cpu.reg_a = (reg_val << 1) | cpu.flag_c
    set_flags(False, False, False, bool(msb), cpu=cpu)


def exec_rlca(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    reg_val = cpu.reg_a
    msb = reg_val >> 7
    cpu.reg_a = (reg_val << 1) | msb
    set_flags(False, False, False, bool(msb), cpu=cpu)


def exec_rra(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    reg_val = cpu.reg_a
    lsb = reg_val & 0x1
    cpu.reg_a = (reg_val >> 1) | (cpu.flag_c << 7)
    set_flags(False, False, False, bool(lsb), cpu=cpu)


def exec_rrca(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    reg_val = cpu.reg_a
    lsb = reg_val & 0x1
    cpu.reg_a = (reg_val >> 1) | (lsb << 7)
    set_flags(False, False, False, bool(lsb), cpu=cpu)


def exec_rst(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    address = instr.param
    condition = instr.cond_type
    jump(address=address, condition=condition, save_context=True, cpu=cpu)


def exec_sbc(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    r1 = read_register(instr.reg_1, cpu=cpu)
    value = r1 - info.data - cpu.flag_c
    flag_z = value == 0
    flag_h = (r1 & 0xF) - (info.data & 0xF) - cpu.flag_c < 0
    flag_c = value < 0
    write_register(instr.reg_1, value, cpu)
    set_flags(flag_z, True, flag_h, flag_c, cpu=cpu)


def exec_scf(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    set_flags(None, False, False, True, cpu=cpu)


def exec_stop(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    # TODO: switch speed here
    pass


def exec_sub(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    r1 = read_register(instr.reg_1, cpu=cpu)
    value = r1 - info.data
    flag_z = value == 0
    flag_h = (r1 & 0xF) < (info.data & 0xF)
    flag_c = r1 < info.data
    write_register(instr.reg_1, value, cpu)
    set_flags(flag_z, True, flag_h, flag_c, cpu=cpu)


def exec_xor(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    cpu.reg_a ^= info.data
    set_flags(cpu.reg_a == 0, False, False, False, cpu)


handler_mapping = {
    InstrType.ADC: exec_adc,
    InstrType.ADD: exec_add,
    InstrType.AND: exec_and,
    InstrType.CALL: exec_call,
    InstrType.CB: exec_cb,
    InstrType.CCF: exec_ccf,
    InstrType.CP: exec_cp,
    InstrType.CPL: exec_cpl,
    InstrType.DAA: exec_daa,
    InstrType.DEC: exec_dec,
    InstrType.DI: exec_di,
    InstrType.EI: exec_ei,
    InstrType.HALT: exec_halt,
    InstrType.INC: exec_inc,
    InstrType.JP: exec_jp,
    InstrType.JR: exec_jr,
    InstrType.LD: exec_ld,
    InstrType.LDH: exec_ldh,
    InstrType.NOP: exec_nop,
    InstrType.OR: exec_or,
    InstrType.POP: exec_pop,
    InstrType.PUSH: exec_push,
    InstrType.RET: exec_ret,
    InstrType.RETI: exec_reti,
    InstrType.RLA: exec_rla,
    InstrType.RLCA: exec_rlca,
    InstrType.RRA: exec_rra,
    InstrType.RRCA: exec_rrca,
    InstrType.RST: exec_rst,
    InstrType.SBC: exec_sbc,
    InstrType.SCF: exec_scf,
    InstrType.STOP: exec_stop,
    InstrType.SUB: exec_sub,
    InstrType.XOR: exec_xor,
}


def execute(instr: Instruction, info: ExecuteInfo, cpu: 'CPU'):
    handler = handler_mapping.get(instr.instr_type)
    if handler is None:
        raise NotImplementedError(f'{instr.instr_type}')
    return handler(instr, info, cpu)
