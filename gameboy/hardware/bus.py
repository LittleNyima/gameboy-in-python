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

from gameboy.common.errors import UnexpectedFallThroughError
from gameboy.common.loggings import get_logger
from gameboy.common.typings import U8, U16
from gameboy.core.device import IODevice
from gameboy.hardware.memory import MemoryLike
from gameboy.hardware.register import InterruptRegister

logger = get_logger(file=__file__)


class Bus(IODevice):

    def __init__(
        self,
        cartridge: MemoryLike,
        boot_rom: MemoryLike,
        vram: MemoryLike,
        wram: MemoryLike,
        hram: MemoryLike,
        oam: MemoryLike,
        int_reg: InterruptRegister,
    ):
        super().__init__()
        self._boot_rom = boot_rom
        self._cartridge = cartridge
        self._vram = vram
        self._wram = wram
        self._hram = hram
        self._oam = oam
        self._int_reg = int_reg
        self._bootrom_mapped = True

    def read(self, address: U16) -> U8:
        if self._bootrom_mapped and 0x0 <= address <= 0xFF:  # Boot Mode
            return self._boot_rom.read(address)
        if 0x0 <= address <= 0x7FFF:  # Cartridge ROM
            return self._cartridge.read(address)
        elif 0x8000 <= address <= 0x9FFF:  # Video RAM
            return self._vram.read(address)
        elif 0xA000 <= address <= 0xBFFF:  # Cartridge RAM
            return self._cartridge.read(address)
        elif 0xC000 <= address <= 0xDFFF:  # Working RAM
            return self._wram.read(address)
        elif 0xE000 <= address <= 0xFDFF:  # Echo RAM
            raise NotImplementedError(f'Echo RAM {address:04X} is prohibited.')
        elif 0xFE00 <= address <= 0xFE9F:  # Object Attribute Memory
            return self._oam.read(address)
        elif 0xFEA0 <= address <= 0xFEFF:
            raise NotImplementedError(f'Memory {address:04X} is unusable.')
        elif 0xFF00 <= address <= 0xFF7F:  # I/O Registers
            # TODO: implement I/O registers
            return U8()
        elif 0xFF80 <= address <= 0xFFFE:  # High RAM
            return self._hram.read(address)
        elif address == 0xFFFF:  # Interrupt Enable Register
            return self._int_reg.int_enable
        raise UnexpectedFallThroughError(f'Unable to read {address:04X}.')

    def write(self, address: U16, value: U8):
        logger.debug(f'Writting {value:02X} to {address:04X}.')
        if 0x0 <= address <= 0x7FFF:  # Cartridge ROM
            return self._cartridge.write(address, value)
        elif 0x8000 <= address <= 0x9FFF:  # Video RAM
            return self._vram.write(address, value)
        elif 0xA000 <= address <= 0xBFFF:  # Cartridge RAM
            return self._cartridge.write(address, value)
        elif 0xC000 <= address <= 0xDFFF:  # Working RAM
            return self._wram.write(address, value)
        elif 0xE000 <= address <= 0xFDFF:  # Echo RAM
            raise NotImplementedError(f'Echo RAM {address:04X} is prohibited.')
        elif 0xFE00 <= address <= 0xFE9F:  # Object Attribute Memory
            return self._oam.write(address, value)
        elif 0xFEA0 <= address <= 0xFEFF:
            raise NotImplementedError(f'Memory {address:04X} is unusable.')
        elif 0xFF00 <= address <= 0xFF7F:  # I/O Registers
            # TODO: implement I/O registers
            return
        elif 0xFF80 <= address <= 0xFFFE:  # High RAM
            return self._hram.write(address, value)
        elif address == 0xFFFF:  # Interrupt Enable Register
            self._int_reg.int_enable = value
            return
        raise UnexpectedFallThroughError(f'Unable to write {address:04X}.')
