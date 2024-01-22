from typing import Optional

from gameboy.core import BaseDevice
from gameboy.hardware.bootrom import BootROM
from gameboy.hardware.cartridge import Cartridge


class Motherboard(BaseDevice):

    def __init__(
        self,
        cartridge_rom: str,
        boot_rom: Optional[str],
    ):
        self._cartridge_rom_file = cartridge_rom
        self._boot_rom_file = boot_rom

        self._cartridge = Cartridge(cartridge_rom)
        self._bootrom = BootROM(boot_rom)

    def startup(self):
        self._bootrom.startup()
        self._cartridge.startup()

    def shutdown(self):
        self._cartridge.shutdown()
        self._bootrom.shutdown()
