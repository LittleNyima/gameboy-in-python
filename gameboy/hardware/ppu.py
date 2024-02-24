from array import array
from typing import TYPE_CHECKING

from gameboy.common import UnexpectedFallThrough
from gameboy.core import InterruptType
from gameboy.hardware.lcd import InterruptSource, LCDMode

if TYPE_CHECKING:
    from gameboy.hardware import Motherboard


LINES_PER_FRAME = 154
TICKS_PER_LINE = 456
Y_RESOLUTION = 144
X_RESOLUTION = 160


class PPU:

    def __init__(self, motherboard: 'Motherboard'):
        self.vram = array('B', [0] * 0x2000)
        self.oam = array('B', [0] * 0xA0)
        self.current_frame = 0
        self.line_ticks = 0
        self.video_buffer = [0] * Y_RESOLUTION * X_RESOLUTION

        self.motherboard = motherboard
        self.lcd = motherboard.lcd
        self.lcd.lcds_mode = LCDMode.OAM_SCAN

    def tick(self):
        self.line_ticks += 1
        if self.lcd.lcds_mode == LCDMode.HBLANK:
            return self.tick_hblank()
        elif self.lcd.lcds_mode == LCDMode.VBLANK:
            return self.tick_vblank()
        elif self.lcd.lcds_mode == LCDMode.OAM_SCAN:
            return self.tick_oam_scan()
        elif self.lcd.lcds_mode == LCDMode.TRANSFERRING:
            return self.tick_tansferring()
        raise UnexpectedFallThrough

    def request_interrupt(self, int_type: InterruptType):
        self.motherboard.cpu.request_interrupt(int_type)

    def newline(self):
        self.lcd.ly += 1
        if self.lcd.ly == self.lcd.ly_compare:
            self.lcd.lcds_lyc = True
            if self.lcd.lcds_stat_int(InterruptSource.LYC):
                self.request_interrupt(InterruptType.LCD_STAT)
        else:
            self.lcd.lcds_lyc = False

    def tick_hblank(self):
        if self.line_ticks >= TICKS_PER_LINE:
            self.newline()
            if self.lcd.ly >= Y_RESOLUTION:
                self.lcd.lcds_mode = LCDMode.VBLANK
                self.request_interrupt(InterruptType.VBLANK)
                if self.lcd.lcds_stat_int(InterruptSource.VBLANK):
                    self.request_interrupt(InterruptType.LCD_STAT)
                self.current_frame += 1
            else:
                self.lcd.lcds_mode = LCDMode.OAM_SCAN
            self.line_ticks = 0

    def tick_vblank(self):
        if self.line_ticks >= TICKS_PER_LINE:
            self.newline()
            if self.lcd.ly >= LINES_PER_FRAME:
                self.lcd.lcds_mode = LCDMode.OAM_SCAN
                self.lcd.ly = 0
            self.line_ticks = 0

    def tick_oam_scan(self):
        if self.line_ticks >= 80:
            self.lcd.lcds_mode = LCDMode.TRANSFERRING

    def tick_tansferring(self):
        if self.line_ticks >= X_RESOLUTION:
            self.lcd.lcds_mode = LCDMode.HBLANK
            if self.lcd.lcds_stat_int(InterruptSource.HBLANK):
                self.request_interrupt(InterruptType.LCD_STAT)

    def read(self, address: int) -> int:
        if 0x8000 <= address <= 0x9FFF:
            return self.vram[address - 0x8000]
        elif 0xFE00 <= address <= 0xFE9F:
            return self.oam[address - 0xFE00]
        raise UnexpectedFallThrough

    def write(self, address: int, value: int) -> None:
        if 0x8000 <= address <= 0x9FFF:
            self.vram[address - 0x8000] = value
            return
        elif 0xFE00 <= address <= 0xFE9F:
            self.oam[address - 0xFE00] = value
            return
        raise UnexpectedFallThrough
