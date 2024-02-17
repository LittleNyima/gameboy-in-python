from enum import StrEnum, auto
from typing import Dict


class AddrMode(StrEnum):
    A16_R = auto()
    A8_R = auto()
    D16 = auto()
    D16_R = auto()
    D8 = auto()
    HLD_R = auto()
    HLI_R = auto()
    HL_SPR = auto()
    IMP = auto()
    MR = auto()
    MR_D8 = auto()
    MR_R = auto()
    R = auto()
    R_A16 = auto()
    R_A8 = auto()
    R_D16 = auto()
    R_D8 = auto()
    R_HLD = auto()
    R_HLI = auto()
    R_MR = auto()
    R_R = auto()


class ConditionType(StrEnum):
    NONE = auto()
    NZ = auto()
    Z = auto()
    NC = auto()
    C = auto()


class InstrType(StrEnum):
    ADC = auto()
    ADD = auto()
    AND = auto()
    BIT = auto()
    CALL = auto()
    CB = auto()
    CCF = auto()
    CP = auto()
    CPL = auto()
    DAA = auto()
    DEC = auto()
    DI = auto()
    EI = auto()
    ERR = auto()
    HALT = auto()
    INC = auto()
    JP = auto()
    JPHL = auto()
    JR = auto()
    LD = auto()
    LDH = auto()
    NONE = auto()
    NOP = auto()
    OR = auto()
    POP = auto()
    PUSH = auto()
    RES = auto()
    RET = auto()
    RETI = auto()
    RL = auto()
    RLA = auto()
    RLC = auto()
    RLCA = auto()
    RR = auto()
    RRA = auto()
    RRC = auto()
    RRCA = auto()
    RST = auto()
    SBC = auto()
    SCF = auto()
    SET = auto()
    SLA = auto()
    SRA = auto()
    SRL = auto()
    STOP = auto()
    SUB = auto()
    SWAP = auto()
    XOR = auto()


class RegType(StrEnum):
    NONE = auto()
    A = auto()
    F = auto()
    B = auto()
    C = auto()
    D = auto()
    E = auto()
    H = auto()
    L = auto()
    AF = auto()
    BC = auto()
    DE = auto()
    HL = auto()
    SP = auto()
    PC = auto()


class Instruction:

    def __init__(
        self,
        instr_type: InstrType,
        addr_mode: AddrMode = AddrMode.IMP,
        reg_1: RegType = RegType.NONE,
        reg_2: RegType = RegType.NONE,
        cond_type: ConditionType = ConditionType.NONE,
        param: int = 0,
    ):
        self.instr_type = instr_type
        self.addr_mode = addr_mode
        self.reg_1 = reg_1
        self.reg_2 = reg_2
        self.cond_type = cond_type
        self.param = param

    def __str__(self) -> str:
        return f'{self.instr_type}'

    def __repr__(self) -> str:
        return str(self)


def build(mapping: Dict):
    for key, value in mapping.items():
        mapping[key] = Instruction(*value)
    return mapping


IT = InstrType
AM = AddrMode
CT = ConditionType
RT = RegType

instructions: Dict[int, Instruction] = build({
    0x00: (IT.NOP,),
    0x05: (IT.DEC, AM.R, RT.B),
    0x0E: (IT.LD, AM.R_D8, RT.C),
    0xAF: (IT.XOR, AM.R, RT.A),
    0xC3: (IT.JP, AM.D16),
    0xF3: (IT.DI,),
})


def decode_instruction(opcode: int) -> Instruction:
    return instructions.get(opcode, Instruction(IT.NONE))
