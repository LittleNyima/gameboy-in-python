from array import array
from enum import IntEnum, auto
from queue import Queue
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


class PixelFIFOState(IntEnum):
    TILE = auto()
    DATA0 = auto()
    DATA1 = auto()
    IDLE = auto()
    PUSH = auto()


class PixelFIFO:
    def __init__(self, ppu: 'PPU'):
        self.fifo: Queue[int] = Queue()
        self.size = 0
        self.line_x = 0
        self.pushed_x = 0
        self.fetch_x = 0
        self.bgw_fetch_data = [0] * 3
        self.fetch_entry_data = [0] * 6
        self.map_y = 0
        self.map_x = 0
        self.tile_y = 0
        self.fifo_x = 0
        self.state = PixelFIFOState.TILE

        self.ppu = ppu

    def fetch(self):
        if self.state == PixelFIFOState.TILE:
            if self.ppu.lcd.lcdc_bgw_enable:
                self.bgw_fetch_data[0] = self.ppu.motherboard.bus.read(
                    self.ppu.lcd.lcdc_bg_map_area
                    + self.map_x // 8
                    + self.map_y // 8 * 32,
                )
                if self.ppu.lcd.lcdc_bgw_data_area == 0x8800:
                    self.bgw_fetch_data[0] += 128
            self.state = PixelFIFOState.DATA0
            self.fetch_x = (self.fetch_x + 8) & 0xFF
        elif self.state == PixelFIFOState.DATA0:
            self.bgw_fetch_data[1] = self.ppu.motherboard.bus.read(
                self.ppu.lcd.lcdc_bgw_data_area
                + self.bgw_fetch_data[0] * 16
                + self.tile_y,
            )
            self.state = PixelFIFOState.DATA1
        elif self.state == PixelFIFOState.DATA1:
            self.bgw_fetch_data[2] = self.ppu.motherboard.bus.read(
                self.ppu.lcd.lcdc_bgw_data_area
                + self.bgw_fetch_data[0] * 16
                + self.tile_y + 1,
            )
            self.state = PixelFIFOState.IDLE
        elif self.state == PixelFIFOState.IDLE:
            self.state = PixelFIFOState.PUSH
        elif self.state == PixelFIFOState.PUSH:
            if self.size <= 8:
                if self.fetch_x + self.ppu.lcd.scroll_x % 8 >= 8:
                    for bit in range(7, -1, -1):
                        lo = (self.bgw_fetch_data[1] >> bit) & 1
                        hi = (self.bgw_fetch_data[2] >> bit) & 1
                        index = (hi << 1) | lo
                        color = self.ppu.lcd.bg_colors[index]
                        self.push(color)
                        self.fifo_x = (self.fifo_x + 1) & 0xFF
                self.state = PixelFIFOState.TILE

    def push_pixel(self):
        if self.size > 8:
            data = self.pull()
            if self.line_x >= self.ppu.lcd.scroll_x % 8:
                index = self.pushed_x + self.ppu.lcd.ly * X_RESOLUTION
                self.ppu.video_buffer[index] = data
                self.pushed_x = (self.pushed_x + 1) & 0xFF
            self.line_x = (self.line_x + 1) & 0xFF

    def process(self):
        self.map_y = (self.ppu.lcd.ly + self.ppu.lcd.scroll_y) & 0xFF
        self.map_x = (self.fetch_x + self.ppu.lcd.scroll_x) & 0xFF
        self.tile_y = (self.map_y % 8 * 2) & 0xFF
        if self.ppu.line_ticks % 2 == 0:
            self.fetch()
        self.push_pixel()

    def clear(self):
        while self.size:
            _ = self.pull()

    def push(self, value: int):
        self.fifo.put(value, block=False)
        self.size += 1

    def pull(self) -> int:
        self.size -= 1
        return self.fifo.get(block=False)


class PPU:

    def __init__(self, motherboard: 'Motherboard'):
        self.vram = array('B', [0] * 0x2000)
        self.oam = array('B', [0] * 0xA0)
        self.current_frame = 0
        self.line_ticks = 0
        self.video_buffer = array('I', [0] * Y_RESOLUTION * X_RESOLUTION)

        self.motherboard = motherboard
        self.lcd = motherboard.lcd
        self.lcd.lcds_mode = LCDMode.OAM_SCAN
        self.pixel_fifo = PixelFIFO(ppu=self)

    def tick(self):
        self.line_ticks += 1
        if self.lcd.lcds_mode == LCDMode.HBLANK:
            return self.tick_hblank()
        elif self.lcd.lcds_mode == LCDMode.VBLANK:
            return self.tick_vblank()
        elif self.lcd.lcds_mode == LCDMode.OAM_SCAN:
            return self.tick_oam_scan()
        elif self.lcd.lcds_mode == LCDMode.TRANSFERRING:
            return self.tick_transferring()
        raise UnexpectedFallThrough

    def request_interrupt(self, int_type: InterruptType):
        self.motherboard.cpu.request_interrupt(int_type)

    def newline(self):
        self.lcd.ly = (self.lcd.ly + 1) & 0xFF
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
            self.pixel_fifo.state = PixelFIFOState.TILE
            self.pixel_fifo.line_x = 0
            self.pixel_fifo.fetch_x = 0
            self.pixel_fifo.pushed_x = 0
            self.pixel_fifo.fifo_x = 0

    def tick_transferring(self):
        self.pixel_fifo.process()
        if self.pixel_fifo.pushed_x >= X_RESOLUTION:
            self.pixel_fifo.clear()
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
