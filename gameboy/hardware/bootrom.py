from typing import Optional

from gameboy.hardware.memory import MemoryLike


class BootROM(MemoryLike):
    def __init__(self, file: Optional[str] = None):
        super().__init__(file=file)
