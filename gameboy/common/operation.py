def get_hi(value: int) -> int:
    return (value >> 8) & 0xFF


def get_lo(value: int) -> int:
    return value & 0xFF


def set_hi(hi: int, value: int) -> int:
    return (value & 0xFF) | ((hi & 0xFF) << 8)


def set_lo(lo: int, value: int) -> int:
    return (value & 0xFF00) | (lo & 0xFF)


def concat(hi: int, lo: int) -> int:
    return ((hi & 0xFF) << 8) | (lo & 0xFF)


def get_bit(value: int, index: int) -> int:
    return (value >> index) & 0x1


def set_bit(bit: bool, value: int, index: int) -> int:
    if bit:
        value |= (1 << index)
    else:
        value &= ~(1 << index)
    return value
