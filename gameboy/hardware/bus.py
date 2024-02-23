from typing import TYPE_CHECKING

from gameboy.common import UnexpectedFallThrough

if TYPE_CHECKING:
    from gameboy.hardware.motherboard import Motherboard

'''
0x0000 - 0x3FFF : ROM Bank 0
0x4000 - 0x7FFF : ROM Bank 1 - Switchable
0x8000 - 0x97FF : CHR RAM
0x9800 - 0x9BFF : BG Map 1
0x9C00 - 0x9FFF : BG Map 2
0xA000 - 0xBFFF : Cartridge RAM
0xC000 - 0xCFFF : RAM Bank 0
0xD000 - 0xDFFF : RAM Bank 1-7 - switchable - Color only
0xE000 - 0xFDFF : Reserved - Echo RAM
0xFE00 - 0xFE9F : Object Attribute Memory
0xFEA0 - 0xFEFF : Reserved - Unusable
0xFF00 - 0xFF7F : I/O Registers
0xFF80 - 0xFFFE : Zero Page
'''


class Bus:

    def __init__(
        self,
        motherboard: 'Motherboard',
    ):
        self.motherboard = motherboard
        self.cartridge = motherboard.cartridge
        self.ram = motherboard.ram
        self.io = motherboard.io

    def read(self, address: int) -> int:
        if 0x0 <= address <= 0x7FFF:  # Cartridge ROM
            return self.cartridge.read(address=address)
        elif 0x8000 <= address <= 0x9FFF:  # Tile Data
            pass
        elif 0xA000 <= address <= 0xBFFF:  # Cartridge RAM
            return self.cartridge.read(address=address)
        elif 0xC000 <= address <= 0xDFFF:  # Working RAM
            return self.ram.read(address=address)
        elif 0xE000 <= address <= 0xFDFF:  # Echo RAM
            return 0
        elif 0xFE00 <= address <= 0xFE9F:  # OAM
            pass
        elif 0xFEA0 <= address <= 0xFEFF:  # Reserved
            pass
        elif 0xFF00 <= address <= 0xFF7F:  # I/O Ports
            return self.io.read(address=address)
        elif 0xFF80 <= address <= 0xFFFE:  # Zero Page / High RAM
            return self.ram.read(address=address)
        elif address == 0xFFFF:  # CPU Interrupt Enable Register
            return self.motherboard.cpu.int_enable_register
        return 0
        raise UnexpectedFallThrough(f'{address:04X}')

    def write(self, address: int, value: int) -> None:
        if 0x0 <= address <= 0x7FFF:
            return self.cartridge.write(address=address, value=value)
        elif 0x8000 <= address <= 0x9FFF:  # Tile Data
            pass
        elif 0xA000 <= address <= 0xBFFF:  # Cartridge RAM
            return self.cartridge.write(address=address, value=value)
        elif 0xC000 <= address <= 0xDFFF:  # Working RAM
            return self.ram.write(address=address, value=value)
        elif 0xE000 <= address <= 0xFDFF:  # Echo RAM
            pass
        elif 0xFE00 <= address <= 0xFE9F:  # OAM
            pass
        elif 0xFEA0 <= address <= 0xFEFF:  # Reserved
            pass
        elif 0xFF00 <= address <= 0xFF7F:  # I/O Ports
            return self.io.write(address=address, value=value)
        elif 0xFF80 <= address <= 0xFFFE:  # Zero Page / High RAM
            return self.ram.write(address=address, value=value)
        elif address == 0xFFFF:  # CPU Interrupt Enable Register
            self.motherboard.cpu.int_enable_register = value
            return
        return
        raise UnexpectedFallThrough(f'{address:04X}: {value}')
