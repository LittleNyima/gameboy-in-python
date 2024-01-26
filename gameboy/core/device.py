from gameboy.common.typings import U8, U16, U8Array


class BaseDevice:

    def __init__(self):
        self._started = False

    def startup(self):
        if not self._started:
            self._started = True
            for obj in self.__dict__.values():
                if isinstance(obj, BaseDevice) and not obj._started:
                    obj.startup()
                    obj._started = True

    def shutdown(self):
        if self._started:
            self._started = False
            for obj in self.__dict__.values():
                if isinstance(obj, BaseDevice) and obj._started:
                    obj.shutdown()
                    obj._started = False


class IODevice(BaseDevice):

    def read(self, address: U16) -> U8:
        raise NotImplementedError

    def read_many(self, address: U16, size: U16) -> U8Array:
        raise NotImplementedError

    def read_range(self, lowerbound: U16, upperbound: U16) -> U8Array:
        raise NotImplementedError

    def write(self, address: U16, value: U8):
        raise NotImplementedError
