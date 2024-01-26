from typing import TYPE_CHECKING

from gameboy.common.errors import UnexpectedFallThroughError
from gameboy.common.typings import U8, U16
from gameboy.core.instructions import InstrType, Instruction, OperandType
from gameboy.hardware.cpu_utils import (
    check_condition, is_value_u8, is_value_u16, log_cpu_status, log_instr,
    pop_stack_u16, push_stack_u16, read_value_u8, read_value_u16,
    write_value_u8, write_value_u16,
)

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU


def execute_call(cpu: 'CPU', instr: Instruction) -> int:  # CALL
    # CALL n16; CALL cc n16;  ZNHC ----
    a16 = cpu.read_u16(cpu.reg_pc + U16(1))
    if (  # CALL condition
        instr.operand0 == OperandType.A16  # CALL a16
        or check_condition(instr.operand0, cpu)  # CALL cc a16
    ):
        cpu.reg_pc += instr.bytes
        push_stack_u16(cpu=cpu, value=cpu.reg_pc)
        cpu.reg_pc = a16
        return instr.cycles[0]
    else:
        cpu.reg_pc += instr.bytes
        return instr.cycles[1]


def execute_cp(cpu: 'CPU', instr: Instruction) -> int:  # CP
    # CP A r8; CP A [HL]; CP A n8;  ZNHC Z1HC
    va = cpu.reg_a
    u8 = read_value_u8(instr.operand1, cpu)
    if va == u8:
        cpu.set_flag_z()
    if (va & 0xF) < (u8 & 0xF):
        cpu.set_flag_h()
    if va < u8:
        cpu.set_flag_c()
    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


def execute_dec(cpu: 'CPU', instr: Instruction) -> int:  # DEC
    # DEC r8; DEC [HL];  ZNHC Z1H-
    # DEC r16; DEC SP;   ZNHC ----
    if is_value_u8(instr.operand0):  # DEC r8; DEC [HL]
        u8 = read_value_u8(instr.operand0, cpu)
        res = u8 - U8(1)
        write_value_u8(instr.operand0, cpu, res)

        if res == U8(0):  # set zero flag if result is 0
            cpu.set_flag_z()
        cpu.set_flag_n()  # set substract flag
        if u8 & 0xF < 1:  # set half carry if borrows from bit 4
            cpu.set_flag_h()

        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    if is_value_u16(instr.operand0):  # DEC r16; DEC SP
        u16 = read_value_u16(instr.operand0, cpu)
        write_value_u16(instr.operand0, cpu, u16 - U16(1))
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    raise UnexpectedFallThroughError


def execute_illegal(cpu: 'CPU', instr: Instruction) -> int:  # ILLEGAL
    # https://gist.github.com/SonoSooS/c0055300670d678b5ae8433e20bea595#opcode-holes-not-implemented-opcodes
    # According to documentation, illegal instructions are invalid, and
    # hard-lock the CPU until the console is powered off. We simply return
    # 0 and do nothing else here.
    cpu.reg_pc += instr.bytes
    return 0


def execute_inc(cpu: 'CPU', instr: Instruction) -> int:  # INC
    # INC r8; INC [HL];  ZNHC Z0H-
    # INC r16; INC SP;   ZNHC ----
    if is_value_u8(instr.operand0):  # INC r8; INC [HL]
        u8 = read_value_u8(instr.operand0, cpu)
        res = u8 + U8(1)
        write_value_u8(instr.operand0, cpu, res)

        if res == 0:  # set zero flag if result is 0
            cpu.set_flag_z()
        cpu.reset_flag_n()  # reset substract flag
        if (u8 & 0xF) + 1 > 0xF:  # set half carry flag if bit 3 overflows
            cpu.set_flag_h()

        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    if is_value_u16(instr.operand0):  # INC r16; INC SP
        u16 = read_value_u16(instr.operand0, cpu)
        write_value_u16(instr.operand0, cpu, u16 + U16(1))
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    raise UnexpectedFallThroughError


def execute_jp(cpu: 'CPU', instr: Instruction) -> int:  # JP
    # JP n16; JP cc n16; JP HL;  ZNHC ----
    if instr.operand0 == OperandType.A16:  # JP n16
        a16 = cpu.read_u16(cpu.reg_pc + U16(1))
        cpu.reg_pc = a16
        return instr.cycles[0]
    raise UnexpectedFallThroughError


def execute_jr(cpu: 'CPU', instr: Instruction) -> int:  # JR
    # JR n16; JR cc n16;  ZNHC ----
    i8 = cpu.read_i8(cpu.reg_pc + U16(1))
    if (  # JUMP condition
        instr.operand0 == OperandType.E8 or  # JR n16
        check_condition(instr.operand0, cpu)  # JR cc n16
    ):
        cpu.reg_pc += instr.bytes
        cpu.reg_pc = U16(cpu.reg_pc + i8)
        return instr.cycles[0]
    else:
        cpu.reg_pc += instr.bytes
        return instr.cycles[1]


def execute_ld(cpu: 'CPU', instr: Instruction) -> int:  # LD
    # 8-bit: LD r8 r8; LD r8 n8; LD [HL] r8; LD [HL] n8; Ld r8 [HL];
    #        LD [r16] A; LD [n16] A; LD A [r16]; LD A [n16]; LD [HL+] A;
    #        LD [HL-] A; LD A [HL+]; LD A [HL-]
    # 16-bit: LD r16 n16;
    # Stack Pointer: LD SP n16; LD [n16] SP; LD HL SP+e8; LD SP HL
    # All instructions have no effect on flags except LD HL SP+e8: 00HC
    operand0, operand1 = instr.operand0, instr.operand1
    if operand0 == OperandType.A16_MEM and operand1 == OperandType.SP:
        raise NotImplementedError  # LD [n16] SP
    if operand0 == OperandType.HL and operand1 == OperandType.SP_INC:
        cpu.reset_flag_z()
        cpu.reset_flag_n()
        raise NotImplementedError  # LD HL SP+e8
    if is_value_u8(instr.operand0) and is_value_u8(instr.operand1):  # 8-bit
        u8 = read_value_u8(instr.operand1, cpu)
        write_value_u8(instr.operand0, cpu, u8)
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    if is_value_u16(instr.operand0) and is_value_u16(instr.operand1):
        # LD SP n16 and LD SP HL fall into this branch
        u16 = read_value_u16(instr.operand1, cpu)
        write_value_u16(instr.operand0, cpu, u16)
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    raise UnexpectedFallThroughError


def execute_ldh(cpu: 'CPU', instr: Instruction) -> int:  # LDH
    # LDH [n16] A; LDH [C] A; LDH A [n16]; LDH A, [C];  ZNHC ----
    if instr.operand0 == OperandType.A:  # LDH A [a8]
        a8 = cpu.read_u8(cpu.reg_pc + U16(1))
        cpu.reg_a = cpu.read_u8(U16(a8) + U16(0xFF00))
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    if instr.operand0 == OperandType.A8_MEM:  # LDH [a8] A
        a8 = cpu.read_u8(cpu.reg_pc + U16(1))
        cpu.write(U16(a8) + U16(0xFF00), cpu.reg_a)
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    raise UnexpectedFallThroughError


def execute_none(cpu: 'CPU', instr: Instruction) -> int:  # NONE
    raise RuntimeError('Unexpected instruction NONE.')


def execute_nop(cpu: 'CPU', instr: Instruction) -> int:  # NOP
    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


def execute_pop(cpu: 'CPU', instr: Instruction) -> int:  # POP
    # POP AF;  ZNHC ZNHC (it's implicitly done)
    # POP r16; ZNHC ----
    u16 = pop_stack_u16(cpu)
    write_value_u16(instr.operand0, cpu, u16)

    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


def execute_push(cpu: 'CPU', instr: Instruction) -> int:  # PUSH
    # PUSH AF; PUSH r16;  ZNHC ----
    u16 = read_value_u16(instr.operand0, cpu)
    push_stack_u16(cpu, u16)
    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


def execute_ret(cpu: 'CPU', instr: Instruction) -> int:  # RET
    # RET cc; RET;  ZNHC ----
    if (
        instr.operand0 == OperandType.NONE  # RET
        or check_condition(instr.operand0, cpu)  # RET cc
    ):
        cpu.reg_pc = pop_stack_u16(cpu)
        return instr.cycles[0]
    else:
        cpu.reg_pc += instr.bytes
        return instr.cycles[1]


def execute_rla(cpu: 'CPU', instr: Instruction) -> int:  # RLA
    # RLA;  ZNHC 000C
    c = cpu.flag_c
    msb = U8(cpu.reg_a >> 7)  # most significant bit
    cpu.reg_a = U8((cpu.reg_a << 1) + c)

    cpu.reset_flag_z()
    cpu.reset_flag_n()
    cpu.reset_flag_h()
    _ = cpu.set_flag_c() if msb else cpu.reset_flag_c()

    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


def execute_set(cpu: 'CPU', instr: Instruction) -> int:  # SET
    # SET u3 r8; SET u3 [HL];  ZNHC ----
    if instr.operand1.value.immediate:  # SET u3 r8
        u8 = read_value_u8(instr.operand1, cpu)
        onehot = U8(1 << int(instr.operand0.value.name))
        write_value_u8(instr.operand1, cpu, u8 | onehot)
        cpu.reg_pc += instr.bytes
        return instr.cycles[0]
    raise UnexpectedFallThroughError


def execute_xor(cpu: 'CPU', instr: Instruction) -> int:  # XOR
    # XOR A r8; XOR A [HL]; XOR A n8;  ZNHC Z000
    u8 = read_value_u8(instr.operand1, cpu)
    res = cpu.reg_a ^ u8
    if res == 0x0:
        cpu.set_flag_z()
    cpu.reset_flag_n()
    cpu.reset_flag_h()
    cpu.reset_flag_c()
    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


def execute_sub(cpu: 'CPU', instr: Instruction) -> int:  # SUB
    # SUB A r8; SUB A [HL]; SUB A n8;  ZNHC Z1HC
    u8 = read_value_u8(instr.operand1, cpu)
    res = cpu.reg_a - u8
    if res == 0x0:
        cpu.set_flag_z()
    cpu.set_flag_n()
    if (cpu.reg_a & 0xF) < (u8 & 0xF):
        cpu.set_flag_h()
    if cpu.reg_a < u8:
        cpu.set_flag_c()
    cpu.reg_pc += instr.bytes
    return instr.cycles[0]


executor_mapping = {
    InstrType.CALL: execute_call,
    InstrType.CP: execute_cp,
    InstrType.DEC: execute_dec,
    InstrType.ILLEGAL_D3: execute_illegal,
    InstrType.ILLEGAL_DB: execute_illegal,
    InstrType.ILLEGAL_DD: execute_illegal,
    InstrType.ILLEGAL_E3: execute_illegal,
    InstrType.ILLEGAL_E4: execute_illegal,
    InstrType.ILLEGAL_EB: execute_illegal,
    InstrType.ILLEGAL_EC: execute_illegal,
    InstrType.ILLEGAL_ED: execute_illegal,
    InstrType.ILLEGAL_F4: execute_illegal,
    InstrType.ILLEGAL_FC: execute_illegal,
    InstrType.ILLEGAL_FD: execute_illegal,
    InstrType.INC: execute_inc,
    InstrType.LD: execute_ld,
    InstrType.LDH: execute_ldh,
    InstrType.JP: execute_jp,
    InstrType.JR: execute_jr,
    InstrType.NONE: execute_none,
    InstrType.NOP: execute_nop,
    InstrType.POP: execute_pop,
    InstrType.PUSH: execute_push,
    InstrType.RET: execute_ret,
    InstrType.RLA: execute_rla,
    InstrType.SET: execute_set,
    InstrType.SUB: execute_sub,
    InstrType.XOR: execute_xor,
}


def execute(cpu: 'CPU', instr: Instruction) -> int:
    log_instr(cpu=cpu, instr=instr)
    log_cpu_status(cpu=cpu, when='before')
    executor = executor_mapping.get(instr.mnemonic)
    if executor is None:
        raise NotImplementedError(f'Not implemented instr {instr}.')
    r = executor(cpu=cpu, instr=instr)
    log_cpu_status(cpu=cpu, when='after')
    return r
