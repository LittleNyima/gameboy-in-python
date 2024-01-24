from typing import Optional

from gameboy.core.device import BaseDevice
from gameboy.hardware import Motherboard


class GameBoy(BaseDevice):

    def __init__(
        self,
        cartridge_rom: str,
        *,
        boot_rom: Optional[str] = None,
    ):
        self._cartridge_rom = cartridge_rom
        self._boot_rom = boot_rom

        self._montherboard = Motherboard(
            cartridge_rom=cartridge_rom,
            boot_rom=boot_rom,
        )

    def startup(self):
        self._montherboard.startup()

    def shutdown(self):
        self._montherboard.shutdown()

    def step(self):
        return self._montherboard.step()
