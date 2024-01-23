from typing import Optional

from gameboy.core import BaseDevice
from gameboy.hardware.bootrom import BootROM
from gameboy.hardware.bus import Bus
from gameboy.hardware.cartridge import Cartridge
from gameboy.hardware.cpu import CPU


class Motherboard(BaseDevice):

    def __init__(
        self,
        cartridge_rom: str,
        boot_rom: Optional[str],
    ):
        self._cartridge_rom_file = cartridge_rom
        self._boot_rom_file = boot_rom

        self._cartridge = Cartridge(cartridge_rom)
        self._boot_rom = BootROM(boot_rom)
        self._bus = Bus(
            cartridge=self._cartridge,
            boot_rom=self._boot_rom,
        )
        self._cpu = CPU(bus=self._bus)

    def startup(self):
        self._boot_rom.startup()
        self._cartridge.startup()

    def shutdown(self):
        self._cartridge.shutdown()
        self._boot_rom.shutdown()

    def step(self):
        self._cpu.step()
