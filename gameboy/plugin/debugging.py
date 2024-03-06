from typing import List

import sdl2

from gameboy.common import create_font_buffer
from gameboy.core import Event, EventType
from gameboy.plugin.base import BasePlugin
from gameboy.plugin.window import BaseSDL2Window


class DebuggingSerial(BasePlugin):

    def __init__(self, gameboy):
        super().__init__(gameboy=gameboy)

    def after_tick(self):
        if self.motherboard.bus.read(0xFF02) == 0x81:
            with open('debug.log', 'a') as fp:
                c = self.motherboard.bus.read(address=0xFF01)
                fp.write(chr(c))
                self.motherboard.bus.write(address=0xFF02, value=0)


class DebuggingTileView(BaseSDL2Window):

    def __init__(self, gameboy, title: str, scale: int):
        super().__init__(
            gameboy=gameboy, title=title, x_pos=sdl2.SDL_WINDOWPOS_UNDEFINED,
            y_pos=sdl2.SDL_WINDOWPOS_UNDEFINED, width=16 * 9, height=24 * 9,
            scale=scale,
        )
        self.columns = 16
        self.rows = 24
        self.tile_size = 8
        self.stride = self.tile_size + 1
        self.palette = [0xFFFFFFFF, 0xFFAAAAAA, 0xFF555555, 0xFF000000]
        self.last_frame = 0

    # def handle_events(self, event_queue: List[Event]):
    #     """
    #     This empty method is to override the default event handling function,
    #     which is time-cosuming.
    #     """
    #     pass

    def after_tick(self):
        current_frame = self.motherboard.ppu.current_frame
        if not self.enabled or self.last_frame == current_frame:
            return
        self.last_frame = current_frame
        self.clear()
        self.display_tiles()
        return super().after_tick()

    def display_tiles(self):
        base_addr = 0x8000
        rect = sdl2.SDL_Rect()
        for row in range(self.rows):
            for col in range(self.columns):
                tile_idx = row * self.columns + col
                for y in range(0, 16, 2):
                    addr = base_addr + tile_idx * 16 + y
                    b0 = self.motherboard.bus.read(addr)
                    b1 = self.motherboard.bus.read(addr + 1)
                    for bit in range(7, -1, -1):
                        hi = int(bool(b0 & (1 << bit)))
                        lo = int(bool(b1 & (1 << bit)))
                        color = self.palette[(hi << 1) | lo]
                        rect.x = (col * self.stride + 7 - bit) * self.scale
                        rect.y = (row * self.stride + y // 2) * self.scale
                        rect.w = self.scale
                        rect.h = self.scale
                        sdl2.SDL_FillRect(self.surface, rect, color)

    def clear(self):
        color = 0xFF333333
        sdl2.SDL_FillRect(self.surface, None, color)


class DebuggingMemoryView(BaseSDL2Window):

    def __init__(self, gameboy, title: str, scale: int):
        super().__init__(
            gameboy=gameboy, title=title, x_pos=sdl2.SDL_WINDOWPOS_UNDEFINED,
            y_pos=sdl2.SDL_WINDOWPOS_UNDEFINED, width=456, height=432,
            scale=scale,
        )
        # The height 432 is to the same with the tile view window (24 * 9 * 2).
        # The width 456 is width of 57 characters.
        self.font_buffer = create_font_buffer()
        self.base_addr = 0x0
        # There will be 17 lines, which consist of 1 line for offsets and 16
        # lines for addresses and values.
        header = ' ' * 8 + ' '.join([f'{offset:02X}' for offset in range(16)])
        self.text_buffer = [header] + [''] * 24
        self.prev_buffer = [''] * 25
        self.first_frame = True

    def handle_events(self, event_queue: List[Event]):
        for event in event_queue:
            if event.type == EventType.MEMORY_VIEW_SCROLL_DOWN:
                if self.base_addr < 0xFF00:
                    self.base_addr += 0x100
            elif event.type == EventType.MEMORY_VIEW_SCROLL_UP:
                if self.base_addr > 0:
                    self.base_addr -= 0x100

    def after_tick(self):
        if not self.enabled or not self.should_refresh(10):
            return
        flush = False
        if self.first_frame:
            self.clear()
            flush = True
            self.first_frame = False
        self.update_text_buffer()
        self.render_text_buffer(flush=flush)
        return super().after_tick()

    def update_text_buffer(self):
        self.prev_buffer = self.text_buffer[:]
        for row in range(24):
            row_base = self.base_addr + row * 16
            if row_base >= 0x10000:
                self.text_buffer[row + 1] = ' ' * 55
                continue
            self.text_buffer[row + 1] = (
                f'0x{self.base_addr + row * 16:04X}  '
                + ' '.join([
                    f'{self.motherboard.bus.read(row_base + offset):02X}'
                    for offset in range(16)
                ])
            )

    def render_character(self, ch: str, x: int, y: int):
        code = ord(ch)
        base = code * 8 * 16
        rect = sdl2.SDL_Rect()
        for row in range(16):
            for col in range(8):
                color = self.font_buffer[base + row * 8 + col]
                rect.x = (x * 8 + col) * self.scale
                rect.y = (y * 16 + row) * self.scale
                rect.w = self.scale
                rect.h = self.scale
                sdl2.SDL_FillRect(self.surface, rect, color)

    def render_text_buffer(self, flush: bool):
        for row, line in enumerate(self.text_buffer):
            for col, ch in enumerate(line):
                if (
                    flush
                    or col >= len(self.prev_buffer[row])
                    or self.prev_buffer[row][col] != ch
                ):
                    self.render_character(ch, col + 1, row + 1)

    def clear(self):
        color = 0xFFFFFFFF
        sdl2.SDL_FillRect(self.surface, None, color)
