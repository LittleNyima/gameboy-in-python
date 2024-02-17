from array import array

from gameboy.common import get_logger

logger = get_logger(file=__file__)


RAM_BANKS = {
    0x0: 0,
    0x1: 1,
    0x2: 1,
    0x3: 4,
    0x4: 16,
    0x5: 8,
}


class Cartridge:

    def __init__(self, filename: str):
        self.data = self.load(filename)
        logger.info(f'Load cartridge from {filename}.')
        logger.info(f'title    : {self.title}')
        logger.info(f'SGB flag : {self.sgb_flag}')
        logger.info(f'type     : {self.cart_type}')
        logger.info(f'ROM size : {self.rom_size}')
        logger.info(f'RAM size : {self.ram_size}')
        logger.info(f'version  : {self.version}')
        logger.info(f'checksum : 0x{self.data[0x14D]:X} ({self.checksum})')

    def read(self, address: int) -> int:
        return self.data[address]

    def write(self, address: int, value: int) -> None:
        raise NotImplementedError

    def load(self, filename: str) -> array[int]:
        with open(filename, 'rb') as fp:
            data = array('B', fp.read())
        return data

    @property
    def title(self):
        return bytes(self.data[0x134:0x144]).decode()

    @property
    def sgb_flag(self):
        return self.data[0x146]

    @property
    def cart_type(self):
        return self.data[0x147]

    @property
    def rom_size(self):
        return self.data[0x148]

    @property
    def ram_size(self):
        return self.data[0x149]

    @property
    def version(self):
        return self.data[0x14C]

    @property
    def checksum(self):
        value = 0
        for addr in range(0x134, 0x14D):
            value -= self.data[addr] + 1
        value %= 256
        return 'PASS' if value == self.data[0x14D] else 'FAIL'
