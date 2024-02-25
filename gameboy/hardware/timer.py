from typing import TYPE_CHECKING

from gameboy.common import UnexpectedFallThrough, get_hi
from gameboy.core import InterruptType

if TYPE_CHECKING:
    from gameboy.hardware import Motherboard

inc_period = {
    0: 1 << 9,
    1: 1 << 3,
    2: 1 << 5,
    3: 1 << 7,
}


class Timer:

    def __init__(self, motherboard: 'Motherboard'):
        self._div = 0xAC00
        self._tima = 0
        self._tma = 0
        self._tac = 0

        self.motherboard = motherboard

    def tick(self):
        prev_div = self.div
        self.div += 1
        # determine whether to update according to increment cycles
        clock_select = self.tac & 0b11
        period = inc_period[clock_select]
        should_update = bool(prev_div & period) and not bool(self.div & period)
        enabled = bool(self.tac & (1 << 2))
        # update
        if should_update and enabled:
            self.tima += 1
            if self.tima == 0xFF:
                self.tima = self.tma
                self.motherboard.cpu.request_interrupt(InterruptType.TIMER)

    def write(self, address: int, value: int):
        if address == 0xFF04:
            self.div = 0
            return
        elif address == 0xFF05:
            self.tima = value
            return
        elif address == 0xFF06:
            self.tma = value
            return
        elif address == 0xFF07:
            self.tac = value
            return
        raise UnexpectedFallThrough

    def read(self, address: int) -> int:
        if address == 0xFF04:
            return get_hi(self.div)
        elif address == 0xFF05:
            return self.tima
        elif address == 0xFF06:
            return self.tma
        elif address == 0xFF07:
            return self.tac
        raise UnexpectedFallThrough

    @property
    def div(self):
        return self._div

    @div.setter
    def div(self, new_value: int):
        self._div = new_value & 0xFFFF

    @property
    def tima(self):
        return self._tima

    @tima.setter
    def tima(self, new_value: int):
        self._tima = new_value & 0xFF

    @property
    def tma(self):
        return self._tma

    @tma.setter
    def tma(self, new_value: int):
        self._tma = new_value & 0xFF

    @property
    def tac(self):
        return self._tac

    @tac.setter
    def tac(self, new_value: int):
        self._tac = new_value & 0xFF
