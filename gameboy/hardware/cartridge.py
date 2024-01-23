from functools import wraps
from typing import Any, Callable, Optional

from gameboy.common.loggings import get_logger
from gameboy.common.typings import U8, U16, U8Array
from gameboy.hardware.carts.constants import CartImplType
from gameboy.hardware.carts.impl import impl_mapping
from gameboy.hardware.memory import MemoryLike

logger = get_logger(file=__file__)


def dispatch_impl(allow_fallback=False):
    def dispatcher(method: Callable):
        @wraps(method)
        def wrapper(self: 'Cartridge', *args: Any, **kwargs: Any):
            name = method.__name__
            impl = impl_mapping.get(self.impl)
            if impl is not None and hasattr(impl, name):
                dispatch_func = getattr(impl, name)
                if callable(dispatch_func):
                    return dispatch_func(self, *args, **kwargs)
            if allow_fallback:
                return method(self, *args, **kwargs)
            raise NotImplementedError(
                f'{name} is not implemented for {self.impl}',
            )
        return wrapper
    return dispatcher


class Cartridge(MemoryLike):
    def __init__(self, file: Optional[str] = None):
        super().__init__(file=file)
        self.impl = CartImplType.UNKNOWN

    def startup(self):
        super().startup()
        self.impl = self.infer_impl()
        self.check_header()

    def shutdown(self):
        super().shutdown()
        self.impl = CartImplType.UNKNOWN

    def infer_impl(self):
        return CartImplType.ROM_ONLY

    @dispatch_impl()
    def check_header(self):
        raise NotImplementedError

    @dispatch_impl(allow_fallback=True)
    def read(self, address: U16) -> U8:
        return super().read(address)

    @dispatch_impl(allow_fallback=True)
    def read_many(self, address: U16, size: U16) -> U8Array:
        return super().read_many(address, size)

    @dispatch_impl(allow_fallback=True)
    def read_range(self, lowerbound: U16, upperbound: U16) -> U8Array:
        return super().read_range(lowerbound, upperbound)

    @dispatch_impl(allow_fallback=True)
    def write(self, address: U16, value: U8):
        return super().write(address, value)
