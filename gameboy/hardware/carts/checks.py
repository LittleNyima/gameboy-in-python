import numpy as np

from gameboy.common.errors import CheckFailedError
from gameboy.common.ioutils import dump_memory, format_hex_data
from gameboy.common.loggings import get_logger
from gameboy.common.typings import U8, U8Array
from gameboy.hardware.carts.constants import (
    NINTENDO_LOGO, NINTENDO_LOGO_BASE_ADDR, CartImplType, RAMSizeType,
    ROMSizeType, impl_codes, ram_size_codes, rom_size_codes,
)

logger = get_logger(file=__file__)


def info(message: str):
    logger.info(f'CHECK: {message}')


def check_nintendo_logo(data: U8Array):
    if data.size != NINTENDO_LOGO.size:
        raise CheckFailedError(f'Bad Nintendo logo memory length {data.size}.')
    if not np.all(data == NINTENDO_LOGO):
        logger.critical('Nintendo logo mismatch. Loaded logo segment:')
        dump_memory(
            data=data, base_address=NINTENDO_LOGO_BASE_ADDR,
            print_func=logger.critical,
        )
        raise CheckFailedError('Nintendo logo mismatch.')
    info('Nintendo logo matches.')


def check_title(data: U8Array):
    databytes = data.tobytes()
    info(f'title - {databytes!r}')


def check_manufacturer(data: U8Array):
    info(f'manufacturer code: {format_hex_data(data)}')


def check_cgb_flag(data: U8Array):
    info(f'CGB flag: {format_hex_data(data)}')


def check_new_licensee_code(data: U8Array):
    info(f'new licensee code - {format_hex_data(data)}')


def check_sgb_flag(data: U8Array):
    info(f'SGB flag - {format_hex_data(data)}')


def check_cartridge_type(data: U8Array):
    impl_type = impl_codes.get(data[0], CartImplType.UNKNOWN)
    info(f'cartridge type - {format_hex_data(data)} ({impl_type})')


def check_rom_size(data: U8Array):
    rom_size = rom_size_codes.get(data[0], ROMSizeType.UNKNOWN)
    info(f'ROM size - {format_hex_data(data)} ({rom_size})')


def check_ram_size(data: U8Array):
    ram_size = ram_size_codes.get(data[0], RAMSizeType.UNKNOWN)
    info(f'RAM size - {format_hex_data(data)} ({ram_size})')


def check_destination_code(data: U8Array):
    info(f'destination code - {format_hex_data(data)}')


def check_old_licensee_code(data: U8Array):
    info(f'old licensee code - {format_hex_data(data)}')


def check_version_number(data: U8Array):
    info(f'ROM version number - {format_hex_data(data)}')


def check_header_checksum(expected: U8, header: U8Array):
    checksum = U8(0)
    for byte in header:
        checksum = U8(checksum - byte - 1)
    if checksum != expected:
        raise CheckFailedError(
            f'Bad checksum {checksum}, expected {expected}',
        )
