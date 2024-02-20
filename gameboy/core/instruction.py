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
    HALT = auto()
    INC = auto()
    JP = auto()
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
        opcode: int,
        instr_type: InstrType,
        addr_mode: AddrMode = AddrMode.IMP,
        reg_1: RegType = RegType.NONE,
        reg_2: RegType = RegType.NONE,
        cond_type: ConditionType = ConditionType.NONE,
        param: int = 0,
    ):
        self.opcode = opcode
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
        mapping[key] = Instruction(key, *value)
    return mapping


IT = InstrType
AM = AddrMode
CT = ConditionType
RT = RegType

instructions: Dict[int, Instruction] = build({
    0x00: (IT.NOP,),
    0x01: (IT.LD, AM.R_D16, RT.BC),
    0x02: (IT.LD, AM.MR_R, RT.BC, RT.A),
    0x03: (IT.INC, AM.R, RT.BC),
    0x04: (IT.INC, AM.R, RT.B),
    0x05: (IT.DEC, AM.R, RT.B),
    0x06: (IT.LD, AM.R_D8, RT.B),
    0x07: (IT.RLCA,),
    0x08: (IT.LD, AM.A16_R, RT.NONE, RT.SP),
    0x09: (IT.ADD, AM.R_R, RT.HL, RT.BC),
    0x0A: (IT.LD, AM.R_MR, RT.A, RT.BC),
    0x0B: (IT.DEC, AM.R, RT.BC),
    0x0C: (IT.INC, AM.R, RT.C),
    0x0D: (IT.DEC, AM.R, RT.C),
    0x0E: (IT.LD, AM.R_D8, RT.C),
    0x0F: (IT.RRCA,),
    0x10: (IT.STOP,),
    0x11: (IT.LD, AM.R_D16, RT.DE),
    0x12: (IT.LD, AM.MR_R, RT.DE, RT.A),
    0x13: (IT.INC, AM.R, RT.DE),
    0x14: (IT.INC, AM.R, RT.D),
    0x15: (IT.DEC, AM.R, RT.D),
    0x16: (IT.LD, AM.R_D8, RT.D),
    0x17: (IT.RLA,),
    0x18: (IT.JR, AM.D8),
    0x19: (IT.ADD, AM.R_R, RT.HL, RT.DE),
    0x1A: (IT.LD, AM.R_MR, RT.A, RT.DE),
    0x1B: (IT.DEC, AM.R, RT.DE),
    0x1C: (IT.INC, AM.R, RT.E),
    0x1D: (IT.DEC, AM.R, RT.E),
    0x1E: (IT.LD, AM.R_D8, RT.E),
    0x1F: (IT.RRA,),
    0x20: (IT.JR, AM.D8, RT.NONE, RT.NONE, CT.NZ),
    0x21: (IT.LD, AM.R_D16, RT.HL),
    0x22: (IT.LD, AM.HLI_R, RT.HL, RT.A),
    0x23: (IT.INC, AM.R, RT.HL),
    0x24: (IT.INC, AM.R, RT.H),
    0x25: (IT.DEC, AM.R, RT.H),
    0x26: (IT.LD, AM.R_D8, RT.H),
    0x27: (IT.DAA,),
    0x28: (IT.JR, AM.D8, RT.NONE, RT.NONE, CT.Z),
    0x29: (IT.ADD, AM.R_R, RT.HL, RT.HL),
    0x2A: (IT.LD, AM.R_HLI, RT.A, RT.HL),
    0x2B: (IT.DEC, AM.R, RT.HL),
    0x2C: (IT.INC, AM.R, RT.L),
    0x2D: (IT.DEC, AM.R, RT.L),
    0x2E: (IT.LD, AM.R_D8, RT.L),
    0x2F: (IT.CPL,),
    0x30: (IT.JR, AM.D8, RT.NONE, RT.NONE, CT.NC),
    0x31: (IT.LD, AM.R_D16, RT.SP),
    0x32: (IT.LD, AM.HLD_R, RT.HL, RT.A),
    0x33: (IT.INC, AM.R, RT.SP),
    0x34: (IT.INC, AM.MR, RT.HL),
    0x35: (IT.DEC, AM.MR, RT.HL),
    0x36: (IT.LD, AM.MR_D8, RT.HL),
    0x37: (IT.SCF,),
    0x38: (IT.JR, AM.D8, RT.NONE, RT.NONE, CT.C),
    0x39: (IT.ADD, AM.R_R, RT.HL, RT.SP),
    0x3A: (IT.LD, AM.R_HLD, RT.A, RT.HL),
    0x3B: (IT.DEC, AM.R, RT.SP),
    0x3C: (IT.INC, AM.R, RT.A),
    0x3D: (IT.DEC, AM.R, RT.A),
    0x3E: (IT.LD, AM.R_D8, RT.A),
    0x3F: (IT.CCF,),
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
    0x80: (IT.ADD, AM.R_R, RT.A, RT.B),
    0x81: (IT.ADD, AM.R_R, RT.A, RT.C),
    0x82: (IT.ADD, AM.R_R, RT.A, RT.D),
    0x83: (IT.ADD, AM.R_R, RT.A, RT.E),
    0x84: (IT.ADD, AM.R_R, RT.A, RT.H),
    0x85: (IT.ADD, AM.R_R, RT.A, RT.L),
    0x86: (IT.ADD, AM.R_MR, RT.A, RT.HL),
    0x87: (IT.ADD, AM.R_R, RT.A, RT.A),
    0x88: (IT.ADC, AM.R_R, RT.A, RT.B),
    0x89: (IT.ADC, AM.R_R, RT.A, RT.C),
    0x8A: (IT.ADC, AM.R_R, RT.A, RT.D),
    0x8B: (IT.ADC, AM.R_R, RT.A, RT.E),
    0x8C: (IT.ADC, AM.R_R, RT.A, RT.H),
    0x8D: (IT.ADC, AM.R_R, RT.A, RT.L),
    0x8E: (IT.ADC, AM.R_MR, RT.A, RT.HL),
    0x8F: (IT.ADC, AM.R_R, RT.A, RT.A),
    0x90: (IT.SUB, AM.R_R, RT.A, RT.B),
    0x91: (IT.SUB, AM.R_R, RT.A, RT.C),
    0x92: (IT.SUB, AM.R_R, RT.A, RT.D),
    0x93: (IT.SUB, AM.R_R, RT.A, RT.E),
    0x94: (IT.SUB, AM.R_R, RT.A, RT.H),
    0x95: (IT.SUB, AM.R_R, RT.A, RT.L),
    0x96: (IT.SUB, AM.R_MR, RT.A, RT.HL),
    0x97: (IT.SUB, AM.R_R, RT.A, RT.A),
    0x98: (IT.SBC, AM.R_R, RT.A, RT.B),
    0x99: (IT.SBC, AM.R_R, RT.A, RT.C),
    0x9A: (IT.SBC, AM.R_R, RT.A, RT.D),
    0x9B: (IT.SBC, AM.R_R, RT.A, RT.E),
    0x9C: (IT.SBC, AM.R_R, RT.A, RT.H),
    0x9D: (IT.SBC, AM.R_R, RT.A, RT.L),
    0x9E: (IT.SBC, AM.R_MR, RT.A, RT.HL),
    0x9F: (IT.SBC, AM.R_R, RT.A, RT.A),
    0xA0: (IT.AND, AM.R_R, RT.A, RT.B),
    0xA1: (IT.AND, AM.R_R, RT.A, RT.C),
    0xA2: (IT.AND, AM.R_R, RT.A, RT.D),
    0xA3: (IT.AND, AM.R_R, RT.A, RT.E),
    0xA4: (IT.AND, AM.R_R, RT.A, RT.H),
    0xA5: (IT.AND, AM.R_R, RT.A, RT.L),
    0xA6: (IT.AND, AM.R_MR, RT.A, RT.HL),
    0xA7: (IT.AND, AM.R_R, RT.A, RT.A),
    0xA8: (IT.XOR, AM.R_R, RT.A, RT.B),
    0xA9: (IT.XOR, AM.R_R, RT.A, RT.C),
    0xAA: (IT.XOR, AM.R_R, RT.A, RT.D),
    0xAB: (IT.XOR, AM.R_R, RT.A, RT.E),
    0xAC: (IT.XOR, AM.R_R, RT.A, RT.H),
    0xAD: (IT.XOR, AM.R_R, RT.A, RT.L),
    0xAE: (IT.XOR, AM.R_MR, RT.A, RT.HL),
    0xAF: (IT.XOR, AM.R, RT.A, RT.A),
    0xB0: (IT.OR, AM.R_R, RT.A, RT.B),
    0xB1: (IT.OR, AM.R_R, RT.A, RT.C),
    0xB2: (IT.OR, AM.R_R, RT.A, RT.D),
    0xB3: (IT.OR, AM.R_R, RT.A, RT.E),
    0xB4: (IT.OR, AM.R_R, RT.A, RT.H),
    0xB5: (IT.OR, AM.R_R, RT.A, RT.L),
    0xB6: (IT.OR, AM.R_MR, RT.A, RT.HL),
    0xB7: (IT.OR, AM.R_R, RT.A, RT.A),
    0xB8: (IT.CP, AM.R_R, RT.A, RT.B),
    0xB9: (IT.CP, AM.R_R, RT.A, RT.C),
    0xBA: (IT.CP, AM.R_R, RT.A, RT.D),
    0xBB: (IT.CP, AM.R_R, RT.A, RT.E),
    0xBC: (IT.CP, AM.R_R, RT.A, RT.H),
    0xBD: (IT.CP, AM.R_R, RT.A, RT.L),
    0xBE: (IT.CP, AM.R_MR, RT.A, RT.HL),
    0xBF: (IT.CP, AM.R_R, RT.A, RT.A),
    0xC0: (IT.RET, AM.IMP, RT.NONE, RT.NONE, CT.NZ),
    0xC1: (IT.POP, AM.R, RT.BC),
    0xC2: (IT.JP, AM.D16, RT.NONE, RT.NONE, CT.NZ),
    0xC3: (IT.JP, AM.D16),
    0xC4: (IT.CALL, AM.D16, RT.NONE, RT.NONE, CT.NZ),
    0xC5: (IT.PUSH, AM.R, RT.BC),
    0xC6: (IT.ADD, AM.R_A8, RT.A),
    0xC7: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x00),
    0xC8: (IT.RET, AM.IMP, RT.NONE, RT.NONE, CT.Z),
    0xC9: (IT.RET,),
    0xCA: (IT.JP, AM.D16, RT.NONE, RT.NONE, CT.Z),
    0xCB: (IT.CB, AM.D8),
    0xCC: (IT.CALL, AM.D16, RT.NONE, RT.NONE, CT.Z),
    0xCD: (IT.CALL, AM.D16),
    0xCE: (IT.ADC, AM.R_D8, RT.A),
    0xCF: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x08),
    0xD0: (IT.RET, AM.IMP, RT.NONE, RT.NONE, CT.NC),
    0xD1: (IT.POP, AM.R, RT.DE),
    0xD2: (IT.JP, AM.D16, RT.NONE, RT.NONE, CT.NC),
    0xD4: (IT.CALL, AM.D16, RT.NONE, RT.NONE, CT.NC),
    0xD5: (IT.PUSH, AM.R, RT.DE),
    0xD6: (IT.SUB, AM.R_D8, RT.A),
    0xD7: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x10),
    0xD8: (IT.RET, AM.IMP, RT.NONE, RT.NONE, CT.C),
    0xD9: (IT.RETI,),
    0xDA: (IT.JP, AM.D16, RT.NONE, RT.NONE, CT.C),
    0xDC: (IT.CALL, AM.D16, RT.NONE, RT.NONE, CT.C),
    0xDE: (IT.SBC, AM.R_D8, RT.A),
    0xDF: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x18),
    0xE0: (IT.LDH, AM.A8_R, RT.NONE, RT.A),
    0xE1: (IT.POP, AM.R, RT.HL),
    0xE2: (IT.LD, AM.MR_R, RT.C, RT.A),
    0xE5: (IT.PUSH, AM.R, RT.HL),
    0xE6: (IT.AND, AM.D8),
    0xE7: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x20),
    0xE8: (IT.ADD, AM.R_D8, RT.SP),
    0xE9: (IT.JP, AM.MR, RT.HL),
    0xEA: (IT.LD, AM.A16_R, RT.NONE, RT.A),
    0xEE: (IT.XOR, AM.D8),
    0xEF: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x28),
    0xF0: (IT.LDH, AM.R_A8, RT.A),
    0xF1: (IT.POP, AM.R, RT.AF),
    0xF2: (IT.LD, AM.R_MR, RT.A, RT.C),
    0xF3: (IT.DI,),
    0xF5: (IT.PUSH, AM.R, RT.AF),
    0xF6: (IT.OR, AM.D8),
    0xF7: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x30),
    0xF8: (IT.LD, AM.HL_SPR, RT.HL, RT.SP),
    0xF9: (IT.LD, AM.R_R, RT.SP, RT.HL),
    0xFA: (IT.LD, AM.R_A16, RT.A),
    0xFB: (IT.EI,),
    0xFE: (IT.CP, AM.D8),
    0xFF: (IT.RST, AM.IMP, RT.NONE, RT.NONE, CT.NONE, 0x38),
})


REG_8BIT = (RT.A, RT.B, RT.C, RT.D, RT.E, RT.F, RT.H, RT.L)
REG_16BIT = (RT.AF, RT.BC, RT.DE, RT.HL, RT.PC, RT.SP)
REG_LOOKUP = (RT.B, RT.C, RT.D, RT.E, RT.H, RT.L, RT.HL, RT.A)


def decode_instruction(opcode: int) -> Instruction:
    return instructions.get(opcode, Instruction(opcode, IT.NONE))
