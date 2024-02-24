import ctypes
from typing import List

import sdl2

from gameboy.core import EventType
from gameboy.plugin.base import BasePlugin

sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)


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
