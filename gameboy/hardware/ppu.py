from enum import Enum
from typing import List

import numpy as np

from gameboy.common.errors import UnexpectedFallThroughError
from gameboy.common.typings import U8, U16, U32
from gameboy.core.device import BaseDevice
from gameboy.hardware.bus import Bus
from gameboy.hardware.lcd import LCD

LINES_PER_FRAME = 154
TICKS_PER_LINE = 456
Y_RESOLUTION = 144
X_RESOLUTION = 160
COLOR_PALETTE = np.array(
    [0xFFFFFFFF, 0xAAAAAAFF, 0x555555FF, 0x000000FF], dtype=U32,
)


class PPUStatus(Enum):

    HORIZONTAL_BLANK = 0
    VERTICAL_BLANK = 1
    OAM_SCAN = 2
    DRAWING_PIXELS = 3


class FIFOStatus(Enum):

    FETCH_TILE = 0
    FETCH_TILE_HIGH = 1
    FETCH_TILE_LOW = 2
    IDLE = 3
    PUSH = 4


class PixelFIFO:

    def __init__(self):
        self._status = FIFOStatus.FETCH_TILE
        self._fifo: List[U32] = []
        self._line_x = U8()
        self._pushed_x = U8()
        self._fetch_x = U8()
        self._bg_fetch_data = np.zeros((3,), dtype=U8)
        self._sprite_fetch_data = np.zeros((6,), dtype=U8)
        self._map_y = U8()
        self._map_x = U8()
        self._tile_y = U8()
        self._fifo_x = U8()


class PPU(BaseDevice):

    def __init__(self, bus: Bus, lcd: LCD):
        super().__init__()
        self._bus = bus
        self._lcd = lcd
        self._current_frame = 0
        self._line_ticks = 0
        self._mode = PPUStatus.OAM_SCAN
        self._pixel_fifo = PixelFIFO()
        self._video_buffer = np.zeros(
            (Y_RESOLUTION * X_RESOLUTION,), dtype=U32,
        )
        self._video_buffer[:] = 0x00FF00FF

    def move_to_new_line(self):
        # increment LY value
        self._lcd._ly += U8(1)
        # deal with STAT.LYC_EQUALS_LY flag
        if self._lcd._ly == self._lcd._lyc:
            self._lcd._stat.set_lyc_equals_ly()
            # TODO: trigger STAT interrupt
        else:
            self._lcd._stat.reset_lyc_equals_ly()
        # return to the beginning of the line
        self._line_ticks = U8(0)

    def horizontal_blank_worker(self):
        if self._line_ticks >= TICKS_PER_LINE:
            self.move_to_new_line()

            if self._lcd._ly >= Y_RESOLUTION:
                self._mode = PPUStatus.VERTICAL_BLANK

                # TODO: request vblank interrupt and stat interrupt
                self._current_frame += 1
            else:
                self._mode = PPUStatus.OAM_SCAN

    def vertical_blank_worker(self):
        # finish drawing a line
        if self._line_ticks >= TICKS_PER_LINE:
            self.move_to_new_line()

            # finish drawing all lines
            if self._lcd._ly >= LINES_PER_FRAME:
                self._mode = PPUStatus.OAM_SCAN
                self._lcd._ly = U8(0)

    def oam_scan_worker(self):
        if self._line_ticks >= 80:
            self._mode = PPUStatus.DRAWING_PIXELS

            self._pixel_fifo._status = FIFOStatus.FETCH_TILE
            self._pixel_fifo._line_x = 0
            self._pixel_fifo._fetch_x = 0
            self._pixel_fifo._pushed_x = 0
            self._pixel_fifo._fifo_x = 0

    def drawing_pixels_worker(self):
        fifo = self._pixel_fifo
        lcd = self._lcd
        fifo._map_y = lcd._ly + lcd._scy
        fifo._map_x = fifo._fetch_x + lcd._scx
        fifo._tile_y = U8((lcd._ly + lcd._scy) % 8 * 2)

        # fetch every 2 ticks
        if self._line_ticks % 2 == 0:
            self.fifo_fetch()

        if len(fifo._fifo) > 8:
            pixel = fifo._fifo.pop(0)
            if fifo._line_x >= lcd._scx % 8:
                push_index = fifo._pushed_x + lcd._ly * X_RESOLUTION
                self._video_buffer[push_index] = pixel
                fifo._pushed_x += U8(1)
            fifo._line_x += 1

        if fifo._pushed_x >= X_RESOLUTION:
            self._mode = PPUStatus.HORIZONTAL_BLANK

            # TODO: invoke interrupt

    def fifo_add(self) -> bool:
        fifo = self._pixel_fifo
        lcd = self._lcd
        if len(fifo._fifo) > 8:  # FIFO is full
            return False
        x = fifo._fetch_x - (8 - lcd._scx % 8)
        for bit in range(7, -1, -1):
            hi = fifo._bg_fetch_data[1] & (1 << bit)
            lo = fifo._bg_fetch_data[2] & (1 << bit)
            color_index = hi + lo + lo  # hi + (lo << 1)
            color = COLOR_PALETTE[lcd._bgp_index[color_index]]
            if x >= 0:
                fifo._fifo.append(color)
                fifo._fifo_x += U8(1)
        return True

    def fifo_fetch(self):
        fifo = self._pixel_fifo
        lcd = self._lcd
        if fifo._status == FIFOStatus.FETCH_TILE:
            if lcd._lcdc.bg_window_enable:
                base_addr = 0x8000 if lcd._lcdc.window_tile_map else 0x8800
                addr = base_addr + fifo._map_x // 8 + fifo._map_y // 8 * 32
                fifo._bg_fetch_data[0] = self._bus.read(U16(addr))
                if not lcd._lcdc.bg_window_tiles:
                    fifo._bg_fetch_data[0] += U8(128)
            fifo._status = FIFOStatus.FETCH_TILE_HIGH
            fifo._fetch_x += U8(8)
        elif fifo._status == FIFOStatus.FETCH_TILE_HIGH:
            base_addr = 0x8000 if lcd._lcdc.bg_window_tiles else 0x8800
            addr = base_addr + fifo._bg_fetch_data[0] * 16 + fifo._tile_y
            fifo._bg_fetch_data[1] = self._bus.read(U16(addr))
            fifo._status = FIFOStatus.FETCH_TILE_LOW
        elif fifo._status == FIFOStatus.FETCH_TILE_LOW:
            base_addr = 0x8000 if lcd._lcdc.bg_window_tiles else 0x8800
            addr = base_addr + fifo._bg_fetch_data[0] * 16 + fifo._tile_y + 1
            fifo._bg_fetch_data[1] = self._bus.read(U16(addr))
            fifo._status = FIFOStatus.IDLE
        elif fifo._status == FIFOStatus.IDLE:
            fifo._status = FIFOStatus.PUSH
        elif fifo._status == FIFOStatus.PUSH:
            if self.fifo_add():
                fifo._status = FIFOStatus.FETCH_TILE
        else:
            raise UnexpectedFallThroughError

    def dispatch_modes(self):
        if self._mode == PPUStatus.HORIZONTAL_BLANK:
            return self.horizontal_blank_worker()
        elif self._mode == PPUStatus.VERTICAL_BLANK:
            return self.vertical_blank_worker()
        elif self._mode == PPUStatus.OAM_SCAN:
            return self.oam_scan_worker()
        elif self._mode == PPUStatus.DRAWING_PIXELS:
            return self.drawing_pixels_worker()
        raise UnexpectedFallThroughError

    def step(self):
        self._line_ticks += 1
        self.dispatch_modes()
