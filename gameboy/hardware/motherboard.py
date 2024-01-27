from typing import Optional

from gameboy.common.typings import U16
from gameboy.core import BaseDevice
from gameboy.hardware.bootrom import BootROM
from gameboy.hardware.bus import Bus
from gameboy.hardware.cartridge import Cartridge
from gameboy.hardware.cpu import CPU
from gameboy.hardware.dma import DMA
from gameboy.hardware.lcd import LCD
from gameboy.hardware.ppu import PPU
from gameboy.hardware.ram import RAM
from gameboy.hardware.register import InterruptRegister


class Motherboard(BaseDevice):

    def __init__(
        self,
        cartridge_rom: str,
        boot_rom: Optional[str] = None,
    ):
        super().__init__()

        self._boot_rom_file = boot_rom
        self._cartridge_rom_file = cartridge_rom

        self._boot_rom = BootROM(boot_rom)
        self._cartridge = Cartridge(cartridge_rom)
        self._vram = RAM(base_addr=U16(0x8000), size=U16(0xA000 - 0x8000))
        self._wram = RAM(base_addr=U16(0xC000), size=U16(0xE000 - 0xC000))
        self._hram = RAM(base_addr=U16(0xFF80), size=U16(0xFFFF - 0xFF80))
        self._oam = RAM(base_addr=U16(0xFE00), size=U16(0xFE9F - 0xFE00))
        self._int_reg = InterruptRegister()
        self._dma = DMA()
        self._lcd = LCD()
        self._bus = Bus(
            cartridge=self._cartridge,
            boot_rom=self._boot_rom,
            vram=self._vram,
            wram=self._wram,
            hram=self._hram,
            oam=self._oam,
            int_reg=self._int_reg,
            dma=self._dma,
            lcd=self._lcd,
        )
        self._cpu = CPU(bus=self._bus)
        self._ppu = PPU(
            bus=self._bus,
            lcd=self._lcd,
        )

        self._dma._bus = self._bus  # connect DMA to BUS

        self._stopped = False

    def step(self):
        self._cpu.step()
        self._ppu.step()
        return True
