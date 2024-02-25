import sdl2

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
                        rect = sdl2.SDL_Rect(
                            x=(col * self.stride + 7 - bit) * self.scale,
                            y=(row * self.stride + y // 2) * self.scale,
                            w=self.scale,
                            h=self.scale,
                        )
                        sdl2.SDL_FillRect(self.surface, rect, color)

    def clear(self):
        color = 0xFF333333
        sdl2.SDL_FillRect(self.surface, None, color)
