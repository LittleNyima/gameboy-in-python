import ctypes
from typing import List

import sdl2
import sdl2.ext

from gameboy.core import EventType
from gameboy.hardware.ppu import X_RESOLUTION, Y_RESOLUTION
from gameboy.plugin.base import BasePlugin

sdl2.ext.init()


KEY_UP = {
    sdl2.SDLK_ESCAPE: EventType.QUIT,
}


class BaseSDL2Window(BasePlugin):

    def __init__(
        self, gameboy, title: str, x_pos: int, y_pos: int,
        width: int, height: int, scale: int,
    ):
        super().__init__(gameboy=gameboy)
        self.title = title
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.width = width
        self.height = height
        self.scale = scale

        self.window: sdl2.SDL_Window
        self.surface: sdl2.SDL_Surface

    def handle_events(self, event_queue: List[EventType]):
        if not self.enabled:
            return
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)):
            if event.type == sdl2.SDL_QUIT:
                event_queue.append(EventType.QUIT)
            elif event.type == sdl2.SDL_KEYUP:
                key = event.key.keysym.sym
                event_queue.append(KEY_UP.get(key, EventType.IGNORED))

    def after_tick(self):
        if not self.enabled:
            return
        sdl2.SDL_UpdateWindowSurface(self.window)

    def enable(self):
        if self.enabled:
            return
        self.window = sdl2.SDL_CreateWindow(
            self.title.encode(), self.x_pos, self.y_pos,
            self.width * self.scale, self.height * self.scale,
            sdl2.SDL_WINDOW_SHOWN,
        )
        self.surface = sdl2.SDL_GetWindowSurface(self.window)
        sdl2.SDL_ShowWindow(self.window)
        return super().enable()

    def disable(self):
        if not self.enabled:
            return
        sdl2.SDL_HideWindow(self.window)
        sdl2.SDL_DestroyWindow(self.window)
        del self.window
        del self.surface
        return super().disable()


class GameSDL2Window(BaseSDL2Window):

    def __init__(self, gameboy, title: str, scale: int):
        super().__init__(
            gameboy=gameboy, title=title,
            x_pos=sdl2.SDL_WINDOWPOS_UNDEFINED,
            y_pos=sdl2.SDL_WINDOWPOS_UNDEFINED,
            width=X_RESOLUTION, height=Y_RESOLUTION,
            scale=scale,
        )
        self.last_frame = 0

    def after_tick(self):
        current_frame = self.motherboard.ppu.current_frame
        if not self.enabled or self.last_frame == current_frame:
            return
        self.last_frame = current_frame
        self.clear()
        self.render()
        return super().after_tick()

    def render(self):
        video_buffer = self.motherboard.ppu.video_buffer
        for row in range(self.height):
            for col in range(self.width):
                rect = sdl2.SDL_Rect(
                    x=col * self.scale,
                    y=row * self.scale,
                    w=self.scale,
                    h=self.scale,
                )
                sdl2.SDL_FillRect(
                    self.surface,
                    rect,
                    video_buffer[col + row * X_RESOLUTION],
                )

    def clear(self):
        color = 0xFF333333
        sdl2.SDL_FillRect(self.surface, None, color)
