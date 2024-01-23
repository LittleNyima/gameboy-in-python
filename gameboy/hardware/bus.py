'''
Memory Map
----------
Start End   Description             Notes
0000  3FFF  16 KiB ROM bank 00      From cartridge, usually a fixed bank
4000  7FFF  16 KiB ROM Bank 01~NN   From cartridge, switchable bank via mapper
8000  9FFF  8 KiB Video RAM (VRAM)  In CGB mode, switchable bank 0/1
A000  BFFF  8 KiB External RAM      From cartridge, switchable bank if any
C000  CFFF  4 KiB Work RAM (WRAM)
D000  DFFF  4 KiB Work RAM (WRAM)   In CGB mode, switchable bank 1~7
E000  FDFF  Mirror of C000~DDFF     Nintendo says use of this area is
            (ECHO RAM)              prohibited
FE00  FE9F  Object attribute
            memory (OAM)
FEA0  FEFF  Not Usable              Nintendo says use of this area is
                                    prohibited
FF00  FF7F  I/O Registers
FF80  FFFE  High RAM (HRAM)
FFFF  FFFF  Interrupt Enable
            register (IE)
'''

from gameboy.common.typings import U8, U16
from gameboy.core.device import IODevice
from gameboy.hardware.memory import MemoryLike


class Bus(IODevice):

    def __init__(self, cartridge: MemoryLike, boot_rom: MemoryLike):
        self._cartridge = cartridge
        self._boot_rom = boot_rom
        self._bootrom_enabled = True

    def read(self, address: U16) -> U8:
        if 0x0 <= address <= 0x7FFF:
            return self._cartridge.read(address)
        raise NotImplementedError(f'Unable to read {address}')
