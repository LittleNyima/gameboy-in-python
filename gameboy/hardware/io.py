# from gameboy.common import UnexpectedFallThrough
from typing import TYPE_CHECKING

from gameboy.hardware.cpu import CPU

if TYPE_CHECKING:
    from gameboy.hardware import Motherboard


class Serial:

    def __init__(self):
        self.data = 0
        self.control = 0


class IO:

    def __init__(self, motherboard: 'Motherboard'):
        self.serial = Serial()
        self.cpu: CPU
        self.timer = motherboard.timer

    def read(self, address: int) -> int:
        if address == 0xFF01:
            return self.serial.data
        elif address == 0xFF02:
            return self.serial.control
        elif 0xFF04 <= address <= 0xFF07:
            return self.timer.read(address=address)
        elif address == 0xFF0F:
            return self.cpu.int_flags_register
        return 0
        # raise UnexpectedFallThrough

    def write(self, address: int, value: int) -> None:
        if address == 0xFF01:
            self.serial.data = value
            return
        elif address == 0xFF02:
            self.serial.control = value
            return
        elif 0xFF04 <= address <= 0xFF07:
            self.timer.write(address=address, value=value)
            return
        elif address == 0xFF0F:
            self.cpu.int_flags_register = value
            return
        return
        # raise UnexpectedFallThrough(f'{address:04X}: {value:02X}')
