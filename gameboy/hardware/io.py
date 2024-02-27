# from gameboy.common import UnexpectedFallThrough
from typing import TYPE_CHECKING

from gameboy.common import set_bit
from gameboy.core import Event, EventType

if TYPE_CHECKING:
    from gameboy.hardware import Motherboard


class Joypad:

    def __init__(self):
        self.select_button = True
        self.select_direction = True
        self.standard = 0xF
        self.directional = 0xF

    def read(self) -> int:
        r = 0xFF
        if self.select_button ^ self.select_direction:
            if not self.select_button:
                r &= self.standard
            if not self.select_direction:
                r &= self.directional
        return r

    def write(self, value: int) -> None:
        self.select_button = bool(value & 0x20)
        self.select_direction = bool(value & 0x10)

    def handle_event(self, event: Event):
        '''
            PRESS_ARROW_UP = auto()
            PRESS_ARROW_DOWN = auto()
            PRESS_ARROW_LEFT = auto()
            PRESS_ARROW_RIGHT = auto()
            PRESS_BUTTON_A = auto()
            PRESS_BUTTON_B = auto()
            PRESS_BUTTON_START = auto()
            PRESS_BUTTON_SELECT = auto()
            RELEASE_ARROW_UP = auto()
            RELEASE_ARROW_DOWN = auto()
            RELEASE_ARROW_LEFT = auto()
            RELEASE_ARROW_RIGHT = auto()
            RELEASE_BUTTON_A = auto()
            RELEASE_BUTTON_B = auto()
            RELEASE_BUTTON_START = auto()
            RELEASE_BUTTON_SELECT = auto()
        '''
        if event.type == EventType.PRESS_ARROW_RIGHT:
            self.directional = set_bit(False, self.directional, 0)
        elif event.type == EventType.PRESS_ARROW_LEFT:
            self.directional = set_bit(False, self.directional, 1)
        elif event.type == EventType.PRESS_ARROW_UP:
            self.directional = set_bit(False, self.directional, 2)
        elif event.type == EventType.PRESS_ARROW_DOWN:
            self.directional = set_bit(False, self.directional, 3)
        elif event.type == EventType.PRESS_BUTTON_A:
            self.standard = set_bit(False, self.standard, 0)
        elif event.type == EventType.PRESS_BUTTON_B:
            self.standard = set_bit(False, self.standard, 1)
        elif event.type == EventType.PRESS_BUTTON_SELECT:
            self.standard = set_bit(False, self.standard, 2)
        elif event.type == EventType.PRESS_BUTTON_START:
            self.standard = set_bit(False, self.standard, 3)
        elif event.type == EventType.RELEASE_ARROW_RIGHT:
            self.directional = set_bit(True, self.directional, 0)
        elif event.type == EventType.RELEASE_ARROW_LEFT:
            self.directional = set_bit(True, self.directional, 1)
        elif event.type == EventType.RELEASE_ARROW_UP:
            self.directional = set_bit(True, self.directional, 2)
        elif event.type == EventType.RELEASE_ARROW_DOWN:
            self.directional = set_bit(True, self.directional, 3)
        elif event.type == EventType.RELEASE_BUTTON_A:
            self.standard = set_bit(True, self.standard, 0)
        elif event.type == EventType.RELEASE_BUTTON_B:
            self.standard = set_bit(True, self.standard, 1)
        elif event.type == EventType.RELEASE_BUTTON_SELECT:
            self.standard = set_bit(True, self.standard, 2)
        elif event.type == EventType.RELEASE_BUTTON_START:
            self.standard = set_bit(True, self.standard, 3)


class DMA:

    def __init__(self, motherboard: 'Motherboard'):
        self.active = False
        self.offset = 0
        self.base = 0
        self.start_delay = 0

        self.motherboard = motherboard

    def write(self, value: int):
        self.active = True
        self.offset = 0
        self.base = value
        self.start_delay = 2

    def tick(self):
        if self.active:
            if self.start_delay:
                self.start_delay -= 1
                return
            addr = self.base * 0x100 + self.offset
            value = self.motherboard.bus.read(address=addr)
            self.motherboard.ppu.oam[self.offset] = value
            self.offset += 1
            self.active = self.offset < 0xA0


class Serial:

    def __init__(self):
        self.data = 0
        self.control = 0


class IO:

    def __init__(self, motherboard: 'Motherboard'):
        self.joypad = Joypad()
        self.serial = Serial()
        self.dma = DMA(motherboard=motherboard)
        self.motherboard = motherboard
        self.lcd = motherboard.lcd
        self.timer = motherboard.timer

    def read(self, address: int) -> int:
        if address == 0xFF00:
            return self.joypad.read()
        elif address == 0xFF01:
            return self.serial.data
        elif address == 0xFF02:
            return self.serial.control
        elif 0xFF04 <= address <= 0xFF07:
            return self.timer.read(address=address)
        elif address == 0xFF0F:
            return self.motherboard.cpu.int_flags_register
        elif 0xFF40 <= address <= 0xFF45:
            return self.lcd.read(address=address)
        elif address == 0xFF46:  # DMA
            return 0
        elif 0xFF47 <= address <= 0xFF4B:
            return self.lcd.read(address=address)
        return 0
        # raise UnexpectedFallThrough

    def write(self, address: int, value: int) -> None:
        if address == 0xFF00:
            return self.joypad.write(value=value)
        elif address == 0xFF01:
            self.serial.data = value
            return
        elif address == 0xFF02:
            self.serial.control = value
            return
        elif 0xFF04 <= address <= 0xFF07:
            return self.timer.write(address=address, value=value)
        elif address == 0xFF0F:
            self.motherboard.cpu.int_flags_register = value
            return
        elif 0xFF40 <= address <= 0xFF45:
            return self.lcd.write(address=address, value=value)
        elif address == 0xFF46:
            return self.dma.write(value=value)
        elif 0xFF47 <= address <= 0xFF4B:
            return self.lcd.write(address=address, value=value)
        return
        # raise UnexpectedFallThrough(f'{address:04X}: {value:02X}')
