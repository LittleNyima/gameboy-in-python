from gameboy.common.typings import U8, U16, U8Array


class BaseDevice:

    def startup(self):
        pass

    def shutdown(self):
        pass


class IODevice(BaseDevice):

    def read(self, address: U16) -> U8:
        raise NotImplementedError

    def read_many(self, address: U16, size: U16) -> U8Array:
        raise NotImplementedError

    def read_range(self, lowerbound: U16, upperbound: U16) -> U8Array:
        raise NotImplementedError

    def write(self, address: U16, value: U8):
        raise NotImplementedError
