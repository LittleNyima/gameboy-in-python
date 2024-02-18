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
    0x01: (IT.LD, AM.R_D16, RT.BC),
    0x02: (IT.LD, AM.MR_R, RT.BC, RT.A),
    0x05: (IT.DEC, AM.R, RT.B),
    0x06: (IT.LD, AM.R_D8, RT.B),
    0x08: (IT.LD, AM.A16_R, RT.NONE, RT.SP),
    0x0A: (IT.LD, AM.R_MR, RT.A, RT.BC),
    0x0E: (IT.LD, AM.R_D8, RT.C),
    0x11: (IT.LD, AM.R_D16, RT.DE),
    0x12: (IT.LD, AM.MR_R, RT.DE, RT.A),
    0x16: (IT.LD, AM.R_D8, RT.D),
    0x1A: (IT.LD, AM.R_MR, RT.A, RT.DE),
    0x1E: (IT.LD, AM.R_D8, RT.E),
    0x21: (IT.LD, AM.R_D16, RT.HL),
    0x22: (IT.LD, AM.HLI_R, RT.HL, RT.A),
    0x26: (IT.LD, AM.R_D8, RT.H),
    0x2A: (IT.LD, AM.R_HLI, RT.A, RT.HL),
    0x2E: (IT.LD, AM.R_D8, RT.L),
    0x31: (IT.LD, AM.R_D16, RT.SP),
    0x32: (IT.LD, AM.HLD_R, RT.HL, RT.A),
    0x36: (IT.LD, AM.MR_D8, RT.HL),
    0x3A: (IT.LD, AM.R_HLD, RT.A, RT.HL),
    0x3E: (IT.LD, AM.R_D8, RT.A),
    0x40: (IT.LD, AM.R_R, RT.B, RT.B),
    0x41: (IT.LD, AM.R_R, RT.B, RT.C),
    0x42: (IT.LD, AM.R_R, RT.B, RT.D),
    0x43: (IT.LD, AM.R_R, RT.B, RT.E),
    0x44: (IT.LD, AM.R_R, RT.B, RT.H),
    0x45: (IT.LD, AM.R_R, RT.B, RT.L),
    0x46: (IT.LD, AM.R_MR, RT.B, RT.HL),
    0x47: (IT.LD, AM.R_R, RT.B, RT.A),
    0x48: (IT.LD, AM.R_R, RT.C, RT.B),
    0x49: (IT.LD, AM.R_R, RT.C, RT.C),
    0x4A: (IT.LD, AM.R_R, RT.C, RT.D),
    0x4B: (IT.LD, AM.R_R, RT.C, RT.E),
    0x4C: (IT.LD, AM.R_R, RT.C, RT.H),
    0x4D: (IT.LD, AM.R_R, RT.C, RT.L),
    0x4E: (IT.LD, AM.R_MR, RT.C, RT.HL),
    0x4F: (IT.LD, AM.R_R, RT.C, RT.A),
    0x50: (IT.LD, AM.R_R,  RT.D, RT.B),
    0x51: (IT.LD, AM.R_R,  RT.D, RT.C),
    0x52: (IT.LD, AM.R_R,  RT.D, RT.D),
    0x53: (IT.LD, AM.R_R,  RT.D, RT.E),
    0x54: (IT.LD, AM.R_R,  RT.D, RT.H),
    0x55: (IT.LD, AM.R_R,  RT.D, RT.L),
    0x56: (IT.LD, AM.R_MR, RT.D, RT.HL),
    0x57: (IT.LD, AM.R_R,  RT.D, RT.A),
    0x58: (IT.LD, AM.R_R,  RT.E, RT.B),
    0x59: (IT.LD, AM.R_R,  RT.E, RT.C),
    0x5A: (IT.LD, AM.R_R,  RT.E, RT.D),
    0x5B: (IT.LD, AM.R_R,  RT.E, RT.E),
    0x5C: (IT.LD, AM.R_R,  RT.E, RT.H),
    0x5D: (IT.LD, AM.R_R,  RT.E, RT.L),
    0x5E: (IT.LD, AM.R_MR, RT.E, RT.HL),
    0x5F: (IT.LD, AM.R_R,  RT.E, RT.A),
    0x60: (IT.LD, AM.R_R,  RT.H, RT.B),
    0x61: (IT.LD, AM.R_R,  RT.H, RT.C),
    0x62: (IT.LD, AM.R_R,  RT.H, RT.D),
    0x63: (IT.LD, AM.R_R,  RT.H, RT.E),
    0x64: (IT.LD, AM.R_R,  RT.H, RT.H),
    0x65: (IT.LD, AM.R_R,  RT.H, RT.L),
    0x66: (IT.LD, AM.R_MR, RT.H, RT.HL),
    0x67: (IT.LD, AM.R_R,  RT.H, RT.A),
    0x68: (IT.LD, AM.R_R,  RT.L, RT.B),
    0x69: (IT.LD, AM.R_R,  RT.L, RT.C),
    0x6A: (IT.LD, AM.R_R,  RT.L, RT.D),
    0x6B: (IT.LD, AM.R_R,  RT.L, RT.E),
    0x6C: (IT.LD, AM.R_R,  RT.L, RT.H),
    0x6D: (IT.LD, AM.R_R,  RT.L, RT.L),
    0x6E: (IT.LD, AM.R_MR, RT.L, RT.HL),
    0x6F: (IT.LD, AM.R_R,  RT.L, RT.A),
    0x70: (IT.LD, AM.MR_R,  RT.HL, RT.B),
    0x71: (IT.LD, AM.MR_R,  RT.HL, RT.C),
    0x72: (IT.LD, AM.MR_R,  RT.HL, RT.D),
    0x73: (IT.LD, AM.MR_R,  RT.HL, RT.E),
    0x74: (IT.LD, AM.MR_R,  RT.HL, RT.H),
    0x75: (IT.LD, AM.MR_R,  RT.HL, RT.L),
    0x77: (IT.LD, AM.MR_R,  RT.HL, RT.A),
    0x78: (IT.LD, AM.R_R,  RT.A, RT.B),
    0x79: (IT.LD, AM.R_R,  RT.A, RT.C),
    0x7A: (IT.LD, AM.R_R,  RT.A, RT.D),
    0x7B: (IT.LD, AM.R_R,  RT.A, RT.E),
    0x7C: (IT.LD, AM.R_R,  RT.A, RT.H),
    0x7D: (IT.LD, AM.R_R,  RT.A, RT.L),
    0x7E: (IT.LD, AM.R_MR, RT.A, RT.HL),
    0x7F: (IT.LD, AM.R_R,  RT.A, RT.A),
    0xAF: (IT.XOR, AM.R, RT.A),
    0xC3: (IT.JP, AM.D16),
    0xE2: (IT.LD, AM.MR_R, RT.C, RT.A),
    0xEA: (IT.LD, AM.A16_R, RT.NONE, RT.A),
    0xF2: (IT.LD, AM.R_MR, RT.A, RT.C),
    0xF3: (IT.DI,),
    0xFA: (IT.LD, AM.R_A16, RT.A),
})


Reg8Bit = (RT.A, RT.B, RT.C, RT.D, RT.E, RT.F, RT.H, RT.L)
Reg16Bit = (RT.AF, RT.BC, RT.DE, RT.HL, RT.PC, RT.SP)


def decode_instruction(opcode: int) -> Instruction:
    return instructions.get(opcode, Instruction(IT.NONE))
