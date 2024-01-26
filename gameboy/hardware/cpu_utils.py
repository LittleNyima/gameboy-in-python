from typing import TYPE_CHECKING

from gameboy.common.errors import UnexpectedFallThroughError
from gameboy.common.loggings import get_logger
from gameboy.common.typings import U8, U16
from gameboy.core.instructions import Instruction, OperandType

if TYPE_CHECKING:
    from gameboy.hardware.cpu import CPU

REG_8BIT_NAMES = set('ABCDEHL')
REG_16BIT_NAMES = {'AF', 'BC', 'DE', 'HL', 'SP', 'PC'}
REG_NAMES = REG_8BIT_NAMES | REG_16BIT_NAMES

logger = get_logger(file=__file__)


def log_instr(cpu: 'CPU', instr: Instruction):
    logger.debug(f'>>> Instruction - {instr}')
    logger.debug(f'Bytes - {instr.bytes}')
    logger.debug(f'Cycles - {instr.cycles}')
    logger.debug(f'Immediate - {instr.immediate}')
    logger.debug(
        f'Flags - {instr.flag_z.value}{instr.flag_n.value}'
        f'{instr.flag_h.value}{instr.flag_c.value}',
    )


def log_cpu_status(cpu: 'CPU', when: str):
    logger.debug(f'>>> CPU status {when} execution')
    logger.debug(f'AF - 0x{cpu.reg_af:04X}    BC - 0x{cpu.reg_bc:04X}')
    logger.debug(f'DE - 0x{cpu.reg_de:04X}    HL - 0x{cpu.reg_hl:04X}')
    logger.debug(f'SP - 0x{cpu.reg_sp:04X}    PC - 0x{cpu.reg_pc:04X}')
    logger.debug('FLAGS:')
    logger.debug(f'ZNHC - {cpu.flag_z}{cpu.flag_n}{cpu.flag_h}{cpu.flag_c}')


def get_hi(value: U16) -> U8:
    return U8(value >> 8)


def get_lo(value: U16) -> U8:
    return U8(value)


def set_hi(value: U16, hi: U8) -> U16:
    _hi = U16(hi) << 8
    _lo = value & 0xFF
    return U16(_lo | _hi)


def set_lo(value: U16, lo: U8) -> U16:
    hi = value & 0xFF00
    return U16(hi | U16(lo))


def concat_bytes(hi: U8, lo: U8) -> U16:
    return U16((U16(hi) << 8) | U16(lo))


def handle_inc_dec(operand_type: OperandType, cpu: 'CPU'):
    '''Increment and decrement flags are set only for 16-bit registers, so
    we implicitly assume that the variable type is U16.
    '''
    operand = operand_type.value
    if operand.increment or operand.decrement:
        attr_name = f'reg_{operand.name.lower()}'
        original_value = getattr(cpu, attr_name)
        if operand.increment:
            setattr(cpu, attr_name, original_value + U16(1))
        if operand.decrement:
            setattr(cpu, attr_name, original_value - U16(1))


def is_value_u8(operand_type: OperandType) -> bool:
    operand = operand_type.value
    return (
        operand.name.upper() in REG_8BIT_NAMES
        or not operand.immediate
        or operand_type == OperandType.N8
    )


def is_value_u16(operand_type: OperandType) -> bool:
    operand = operand_type.value
    return (
        operand.name.upper() in REG_16BIT_NAMES
        or not operand.immediate
        or operand_type == OperandType.A16
        or operand_type == OperandType.N16
    )


def read_value_u8(operand_type: OperandType, cpu: 'CPU') -> U8:
    operand = operand_type.value
    r = None
    if operand.name.upper() in REG_8BIT_NAMES and operand.immediate:  # reg
        attr_name = f'reg_{operand.name.lower()}'
        r = getattr(cpu, attr_name)
    elif operand.name.upper() in REG_NAMES and not operand.immediate:  # [reg]
        attr_name = f'reg_{operand.name.lower()}'
        reg_value = getattr(cpu, attr_name)
        r = cpu.read_u8(reg_value)
    elif operand_type == OperandType.N8:  # immediate
        r = cpu.read_u8(cpu.reg_pc + U16(1))
    handle_inc_dec(operand_type=operand_type, cpu=cpu)
    if r is not None:
        return r
    raise UnexpectedFallThroughError


def write_value_u8(operand_type: OperandType, cpu: 'CPU', value: U8):
    operand = operand_type.value
    if operand.name.upper() in REG_8BIT_NAMES and operand.immediate:  # reg
        attr_name = f'reg_{operand.name.lower()}'
        setattr(cpu, attr_name, value)
        return handle_inc_dec(operand_type=operand_type, cpu=cpu)
    if operand.name.upper() in REG_NAMES and not operand.immediate:  # [reg]
        attr_name = f'reg_{operand.name.lower()}'
        reg_value = getattr(cpu, attr_name)
        cpu.write(reg_value, value)
        return handle_inc_dec(operand_type=operand_type, cpu=cpu)
    if operand_type == OperandType.A16_MEM:
        u16 = cpu.read_u16(cpu.reg_pc + U16(1))
        cpu.write(u16, value)
        return handle_inc_dec(operand_type=operand_type, cpu=cpu)
    raise UnexpectedFallThroughError


def read_value_u16(operand_type: OperandType, cpu: 'CPU') -> U16:
    operand = operand_type.value
    r = None
    if operand.name.upper() in REG_16BIT_NAMES and operand.immediate:  # reg
        attr_name = f'reg_{operand.name.lower()}'
        r = getattr(cpu, attr_name)
    elif operand_type in (OperandType.A16, OperandType.N16):  # immediate
        r = cpu.read_u16(cpu.reg_pc + U16(1))
    handle_inc_dec(operand_type=operand_type, cpu=cpu)
    if r is not None:
        return r
    raise UnexpectedFallThroughError


def write_value_u16(operand_type: OperandType, cpu: 'CPU', value: U16):
    operand = operand_type.value
    if operand.name.upper() in REG_16BIT_NAMES and operand.immediate:  # reg
        attr_name = f'reg_{operand.name.lower()}'
        setattr(cpu, attr_name, value)
        return handle_inc_dec(operand_type=operand_type, cpu=cpu)
    raise UnexpectedFallThroughError


def pop_stack_u8(cpu: 'CPU') -> U8:
    r = cpu.read_u8(cpu.reg_sp)
    cpu.reg_sp += U16(1)
    return r


def push_stack_u8(cpu: 'CPU', value: U8):
    cpu.reg_sp -= U16(1)
    cpu.write(cpu.reg_sp, value)


def pop_stack_u16(cpu: 'CPU') -> U16:
    lo = pop_stack_u8(cpu=cpu)
    hi = pop_stack_u8(cpu=cpu)
    return concat_bytes(hi=hi, lo=lo)


def push_stack_u16(cpu: 'CPU', value: U16):
    push_stack_u8(cpu=cpu, value=get_hi(value))
    push_stack_u8(cpu=cpu, value=get_lo(value))


def check_condition(operand_type: OperandType, cpu: 'CPU') -> bool:
    if operand_type == OperandType.Z:
        return bool(cpu.flag_z)
    if operand_type == OperandType.NZ:
        return not bool(cpu.flag_z)
    if operand_type == OperandType.C:
        return bool(cpu.flag_c)
    if operand_type == OperandType.NC:
        return not bool(cpu.flag_c)
    raise UnexpectedFallThroughError
