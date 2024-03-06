from enum import IntEnum, IntFlag
from typing import List

from gameboy.common import UnexpectedFallThrough, get_bit, set_bit


class LCDMode(IntEnum):
    HBLANK = 0
    VBLANK = 1
    OAM_SCAN = 2
    TRANSFERRING = 3


"""
Instantiating enum object from value is time consuming, so we prepare a lookup
table here for optimization.
"""
LCD_MODE_LOOKUP = [
    LCDMode.HBLANK,
    LCDMode.VBLANK,
    LCDMode.OAM_SCAN,
    LCDMode.TRANSFERRING,
]


class InterruptSource(IntFlag):
    HBLANK = 1 << 3
    VBLANK = 1 << 4
    OAM = 1 << 5
    LYC = 1 << 6


class LCD:

    def __init__(self):
        self.lcd_control = 0x91  # 0xFF40, R/W
        self.lcd_status = 0  # 0xFF41, Mixed
        self.scroll_y = 0  # 0xFF42, R/W
        self.scroll_x = 0  # 0xFF43, R/W
        self.ly = 0  # 0xFF44, R
        self.ly_compare = 0  # 0xFF45, R/W
        self.bg_palette = 0xFC  # 0xFF47, R/W
        self.obj0_palette = 0xFF  # 0xFF48, R/W
        self.obj1_palette = 0xFF  # 0xFF49, R/W
        self.window_y = 0  # 0xFF4A, R/W
        self.window_x = 0  # 0xFF4B, R/W

        self.default_colors = [0xFFFFFFFF, 0xFFAAAAAA, 0xFF555555, 0xFF000000]
        self.bg_colors = self.default_colors[:]
        self.obj0_colors = self.default_colors[:]
        self.obj1_colors = self.default_colors[:]

    def read(self, address: int) -> int:
        if address == 0xFF40:
            return self.lcd_control
        elif address == 0xFF41:
            return self.lcd_status
        elif address == 0xFF42:
            return self.scroll_y
        elif address == 0xFF43:
            return self.scroll_x
        elif address == 0xFF44:
            return self.ly
        elif address == 0xFF45:
            return self.ly_compare
        elif address == 0xFF47:
            return self.bg_palette
        elif address == 0xFF48:
            return self.obj0_palette
        elif address == 0xFF49:
            return self.obj1_palette
        elif address == 0xFF4A:
            return self.window_y
        elif address == 0xFF4B:
            return self.window_x
        raise UnexpectedFallThrough

    def write(self, address: int, value: int) -> None:
        if address == 0xFF40:
            self.lcd_control = value
            return
        elif address == 0xFF41:
            self.lcd_status = value
            return
        elif address == 0xFF42:
            self.scroll_y = value
            return
        elif address == 0xFF43:
            self.scroll_x = value
            return
        elif address == 0xFF44:
            self.ly = value
            return
        elif address == 0xFF45:
            self.ly_compare = value
            return
        elif address == 0xFF47:
            self.bg_palette = value
            self.update_palette(self.bg_colors, value)
            return
        elif address == 0xFF48:
            self.obj0_palette = value
            self.update_palette(self.obj0_colors, value & 0xFC)
            return
        elif address == 0xFF49:
            self.obj1_palette = value
            self.update_palette(self.obj1_colors, value & 0xFC)
            return
        elif address == 0xFF4A:
            self.window_y = value
            return
        elif address == 0xFF4B:
            self.window_x = value
            return
        raise UnexpectedFallThrough

    def update_palette(self, palette: List[int], value: int):
        palette[0] = self.default_colors[value & 0x3]
        palette[1] = self.default_colors[(value >> 2) & 0x3]
        palette[2] = self.default_colors[(value >> 4) & 0x3]
        palette[3] = self.default_colors[(value >> 6) & 0x3]

    @property
    def lcdc_bgw_enable(self):
        return get_bit(self.lcd_control, 0)

    @property
    def lcdc_obj_enable(self):
        return get_bit(self.lcd_control, 1)

    @property
    def lcdc_obj_height(self):
        return 16 if get_bit(self.lcd_control, 2) else 8

    @property
    def lcdc_bg_map_area(self):
        return 0x9C00 if get_bit(self.lcd_control, 3) else 0x9800

    @property
    def lcdc_bgw_data_area(self):
        return 0x8000 if get_bit(self.lcd_control, 4) else 0x8800

    @property
    def lcdc_win_enable(self):
        return get_bit(self.lcd_control, 5)

    @property
    def lcdc_win_map_area(self):
        return 0x9C00 if get_bit(self.lcd_control, 6) else 0x9800

    @property
    def lcdc_lcd_enable(self):
        return get_bit(self.lcd_control, 7)

    @property
    def lcds_mode(self):
        return LCD_MODE_LOOKUP[self.lcd_status & 0x3]

    @lcds_mode.setter
    def lcds_mode(self, mode: LCDMode):
        self.lcd_status &= 0xFC
        self.lcd_status |= mode.value

    @property
    def lcds_lyc(self):
        return get_bit(self.lcd_status, 2)

    @lcds_lyc.setter
    def lcds_lyc(self, new_value: bool):
        self.lcd_status = set_bit(bool(new_value), self.lcd_status, 2)

    def lcds_stat_int(self, int_source: InterruptSource):
        return self.lcd_status & int_source.value
