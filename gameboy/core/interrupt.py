from enum import Flag


class InterruptType(Flag):
    VBLANK = 1
    LCD_STAT = 2
    TIMER = 4
    SERIAL = 8
    JOYPAD = 16
