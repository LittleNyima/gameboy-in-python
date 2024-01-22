from enum import Enum
from typing import Dict

import numpy as np

from gameboy.common.typings import U8, U16


class CartImplType(Enum):
    UNKNOWN = '<UNKNOWN>'
    ROM_ONLY = 'ROM_ONLY'
    MBC1 = 'MBC1'
    MBC1_RAM = 'MBC1_RAM'
    MBC1_RAM_BATTERY = 'MBC1_RAM_BATTERY'
    MBC2 = 'MBC2'
    MBC2_BATTERY = 'MBC2_BATTERY'
    ROM_RAM = 'ROM_RAM'
    ROM_RAM_BATTERY = 'ROM_RAM_BATTERY'
    MMM01 = 'MMM01'
    MMM01_RAM = 'MMM01_RAM'
    MMM01_RAM_BATTERY = 'MMM01_RAM_BATTERY'
    MBC3_TIMER_BATTERY = 'MBC3_TIMER_BATTERY'
    MBC3_TIMER_RAM_BATTERY = 'MBC3_TIMER_RAM_BATTERY'
    MBC3 = 'MBC3'
    MBC3_RAM = 'MBC3_RAM'
    MBC3_RAM_BATTERY = 'MBC3_RAM_BATTERY'
    MBC5 = 'MBC5'
    MBC5_RAM = 'MBC5_RAM'
    MBC5_RAM_BATTERY = 'MBC5_RAM_BATTERY'
    MBC5_RUMBLE = 'MBC5_RUMBLE'
    MBC5_RUMBLE_RAM = 'MBC5_RUMBLE_RAM'
    MBC5_RUMBLE_RAM_BATTERY = 'MBC5_RUMBLE_RAM_BATTERY'
    MBC6 = 'MBC6'
    MBC7_SENSOR_RUMBLE_RAM_BATTERY = 'MBC7_SENSOR_RUMBLE_RAM_BATTERY'
    POCKET_CAMERA = 'POCKET_CAMERA'
    BANDAI_TAMA5 = 'BANDAI_TAMA5'
    HUC3 = 'HuC3'
    HUC1_RAM_BATTERY = 'HuC1_RAM_BATTERY'


class ROMSizeType(Enum):
    UNKNOWN = '<UNKNOWN>'
    ROM_32KiB = 32 * 1024
    ROM_64KiB = 64 * 1024
    ROM_128KiB = 128 * 1024
    ROM_256KiB = 256 * 1024
    ROM_512KiB = 512 * 1024
    ROM_1MiB = 1 * 1024 * 1024
    ROM_2MiB = 2 * 1024 * 1024
    ROM_4MiB = 4 * 1024 * 1024
    ROM_8MiB = 8 * 1024 * 1024


class RAMSizeType(Enum):
    UNKNOWN = '<UNKNOWN>'
    NO_RAM = 0
    RAM_2KiB = 2 * 1024
    RAM_8KiB = 8 * 1024
    RAM_32KiB = 32 * 1024
    RAM_64KiB = 64 * 1024
    RAM_128KiB = 128 * 1024


rom_size_codes: Dict[int, ROMSizeType] = {
    0x00: ROMSizeType.ROM_32KiB,
    0x01: ROMSizeType.ROM_64KiB,
    0x02: ROMSizeType.ROM_128KiB,
    0x03: ROMSizeType.ROM_256KiB,
    0x04: ROMSizeType.ROM_512KiB,
    0x05: ROMSizeType.ROM_1MiB,
    0x06: ROMSizeType.ROM_2MiB,
    0x07: ROMSizeType.ROM_4MiB,
    0x08: ROMSizeType.ROM_8MiB,
}


ram_size_codes: Dict[int, RAMSizeType] = {
    0x00: RAMSizeType.NO_RAM,
    0x01: RAMSizeType.RAM_2KiB,
    0x02: RAMSizeType.RAM_8KiB,
    0x03: RAMSizeType.RAM_32KiB,
    0x04: RAMSizeType.RAM_128KiB,
    0x05: RAMSizeType.RAM_64KiB,
}


impl_codes: Dict[int, CartImplType] = {
    0x00: CartImplType.ROM_ONLY,
    0x01: CartImplType.MBC1,
    0x02: CartImplType.MBC1_RAM,
    0x03: CartImplType.MBC1_RAM_BATTERY,
    0x05: CartImplType.MBC2,
    0x06: CartImplType.MBC2_BATTERY,
    0x08: CartImplType.ROM_RAM,
    0x09: CartImplType.ROM_RAM_BATTERY,
    0x0B: CartImplType.MMM01,
    0x0C: CartImplType.MMM01_RAM,
    0x0D: CartImplType.MMM01_RAM_BATTERY,
    0x0F: CartImplType.MBC3_TIMER_BATTERY,
    0x10: CartImplType.MBC3_TIMER_RAM_BATTERY,
    0x11: CartImplType.MBC3,
    0x12: CartImplType.MBC3_RAM,
    0x13: CartImplType.MBC3_RAM_BATTERY,
    0x19: CartImplType.MBC5,
    0x1A: CartImplType.MBC5_RAM,
    0x1B: CartImplType.MBC5_RAM_BATTERY,
    0x1C: CartImplType.MBC5_RUMBLE,
    0x1D: CartImplType.MBC5_RUMBLE_RAM,
    0x1E: CartImplType.MBC5_RUMBLE_RAM_BATTERY,
    0x20: CartImplType.MBC6,
    0x22: CartImplType.MBC7_SENSOR_RUMBLE_RAM_BATTERY,
    0xFC: CartImplType.POCKET_CAMERA,
    0xFD: CartImplType.BANDAI_TAMA5,
    0xFE: CartImplType.HUC3,
    0xFF: CartImplType.HUC1_RAM_BATTERY,
}


NINTENDO_LOGO = np.array(
    [
        0xCE, 0xED, 0x66, 0x66, 0xCC, 0x0D, 0x00, 0x0B,
        0x03, 0x73, 0x00, 0x83, 0x00, 0x0C, 0x00, 0x0D,
        0x00, 0x08, 0x11, 0x1F, 0x88, 0x89, 0x00, 0x0E,
        0xDC, 0xCC, 0x6E, 0xE6, 0xDD, 0xDD, 0xD9, 0x99,
        0xBB, 0xBB, 0x67, 0x63, 0x6E, 0x0E, 0xEC, 0xCC,
        0xDD, 0xDC, 0x99, 0x9F, 0xBB, 0xB9, 0x33, 0x3E,
    ], dtype=U8,
)

NINTENDO_LOGO_BASE_ADDR = U16(0x104)
TITLE_BASE_ADDR = U16(0x134)
MANUFACTURER_CODE_ADDR = U16(0x13F)
CGB_FLAG_ADDR = U16(0x143)
NEW_LICENSE_CODE_ADDR = U16(0x144)
SGB_FLAG_ADDR = U16(0x146)
CARTRIDGE_TYPE_ADDR = U16(0x147)
ROM_SIZE_ADDR = U16(0x148)
RAM_SIZE_ADDR = U16(0x149)
DESTINATION_CODE_ADDR = U16(0x14A)
OLD_LICENSE_CODE_ADDR = U16(0x14B)
ROM_VERSION_ADDR = U16(0x14C)
HEADER_CHECKSUM_ADDR = U16(0x14D)
GLOBAL_CHECKSUM_ADDR = U16(0x14E)
