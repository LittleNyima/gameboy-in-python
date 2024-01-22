import math
import os
from typing import Callable, Optional, Union

import numpy as np

from gameboy.common.loggings import get_logger
from gameboy.common.typings import U8, U16, U8Array

logger = get_logger(file=__file__)


def load_u8_binary_file(file: Union[str, bytes, os.PathLike]) -> U8Array:
    data = np.fromfile(file=file, dtype=U8)
    logger.info(f'Loaded 0x{data.size:X} bytes from {file!r}')
    return data


def format_hex_data(hex_data: U8Array) -> str:
    format_string = ' '.join([r'{:02X}'] * hex_data.size)
    return format_string.format(*hex_data)


def dump_memory(
    data: U8Array,
    base_address: Optional[U16] = None,
    print_func: Callable = print,
):
    def print_hex_row(prefix: str, hex_data: U8Array, pad_left: int = 0):
        prefix_string = prefix + ' ..' * pad_left
        margin = ' ' if prefix_string else ''
        print_func(prefix_string + margin + format_hex_data(hex_data))

    if data.size == 0:  # ignore empty data
        return
    lowest = base_address & 0xFFF0 if base_address is not None else None
    padding = base_address % 0x10 if base_address is not None else 0
    columns = min(data.size, 0x10)
    rows = math.ceil((data.size + padding) / columns)
    if base_address is not None:  # print column headers
        print_hex_row('    ', np.arange(columns, dtype=U16))
    for row_index in range(rows):
        row_addr = lowest + row_index * 0x10 if lowest is not None else None
        row_prefix = f'{row_addr:04X}' if base_address is not None else ''
        row_padding = padding if row_index == 0 else 0
        row_length = columns - row_padding
        lower_index = max(0, row_index * columns - padding)
        row_data = data[lower_index:lower_index + row_length]
        print_hex_row(row_prefix, row_data, row_padding)
