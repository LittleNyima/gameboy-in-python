from typing import TYPE_CHECKING, cast

from gameboy.common.loggings import get_logger
from gameboy.common.typings import U16
from gameboy.hardware.carts import checks
from gameboy.hardware.carts.constants import (
    CARTRIDGE_TYPE_ADDR, CGB_FLAG_ADDR, DESTINATION_CODE_ADDR,
    HEADER_CHECKSUM_ADDR, MANUFACTURER_CODE_ADDR, NEW_LICENSE_CODE_ADDR,
    NINTENDO_LOGO, NINTENDO_LOGO_BASE_ADDR, OLD_LICENSE_CODE_ADDR,
    RAM_SIZE_ADDR, ROM_SIZE_ADDR, ROM_VERSION_ADDR, SGB_FLAG_ADDR,
    TITLE_BASE_ADDR,
)
from gameboy.hardware.memory import MemoryLike

if TYPE_CHECKING:
    from gameboy.hardware.cartridge import Cartridge

logger = get_logger(file=__file__)


def check_header(cartridge: 'Cartridge'):
    memory = cast(MemoryLike, super(type(cartridge), cartridge))
    checks.check_nintendo_logo(
        memory.read_many(
            NINTENDO_LOGO_BASE_ADDR, U16(NINTENDO_LOGO.size),
        ),
    )
    checks.check_title(memory.read_many(TITLE_BASE_ADDR, U16(0x10)))
    checks.check_manufacturer(memory.read_many(MANUFACTURER_CODE_ADDR, U16(4)))
    checks.check_cgb_flag(memory.read_many(CGB_FLAG_ADDR, U16(1)))
    checks.check_new_licensee_code(
        memory.read_many(NEW_LICENSE_CODE_ADDR, U16(2)),
    )
    checks.check_sgb_flag(memory.read_many(SGB_FLAG_ADDR, U16(1)))
    checks.check_cartridge_type(memory.read_many(CARTRIDGE_TYPE_ADDR, U16(1)))
    checks.check_rom_size(memory.read_many(ROM_SIZE_ADDR, U16(1)))
    checks.check_ram_size(memory.read_many(RAM_SIZE_ADDR, U16(1)))
    checks.check_destination_code(
        memory.read_many(DESTINATION_CODE_ADDR, U16(1)),
    )
    checks.check_old_licensee_code(
        memory.read_many(OLD_LICENSE_CODE_ADDR, U16(1)),
    )
    checks.check_version_number(memory.read_many(ROM_VERSION_ADDR, U16(1)))
    checks.check_header_checksum(
        memory.read(HEADER_CHECKSUM_ADDR),
        memory.read_range(TITLE_BASE_ADDR, HEADER_CHECKSUM_ADDR),
    )
