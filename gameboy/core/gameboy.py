from typing import Optional

from gameboy.core.device import BaseDevice
from gameboy.display import create_debug_display, create_display
from gameboy.hardware import Motherboard


class GameBoy(BaseDevice):

    def __init__(
        self,
        cartridge_rom: str,
        *,
        boot_rom: Optional[str] = None,
        display_backend: str = 'pyglet',
    ):
        self._cartridge_rom = cartridge_rom
        self._boot_rom = boot_rom

        self._montherboard = Motherboard(
            cartridge_rom=cartridge_rom,
            boot_rom=boot_rom,
        )

        self._display = create_display(
            motherboard=self._montherboard,
            window_title='GameBoy',
            backend=display_backend,
        )
        self._debug_display = create_debug_display(
            motherboard=self._montherboard,
            window_title='Debug',
            window_size=(16*8, 24*8),
            backend=display_backend,
        )

    def startup(self):
        self._montherboard.startup()

    def shutdown(self):
        self._montherboard.shutdown()

    def step(self):
        if self._montherboard._stopped:
            return False
        self._montherboard.step()
        self._display.render()
        self._debug_display.render()
        return True
