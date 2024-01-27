from typing import Tuple

from gameboy.hardware.motherboard import Motherboard

from .base import BaseDisplay
from .pyglet_display import PygletDebugDisplay, PygletDisplay

impl_mapping = {
    'pyglet': PygletDisplay,
}

debug_impl_mapping = {
    'pyglet': PygletDebugDisplay,
}


def _create_display(
    mapping,
    motherboard: Motherboard,
    window_title: str,
    window_size: Tuple[int, int] = (160, 144),
    scale: int = 2,
    backend: str = 'pyglet',
) -> BaseDisplay:
    impl = mapping.get(backend, None)
    if impl is None:
        raise NotImplementedError(f'{backend=} is not support')
    return impl(
        motherboard=motherboard,
        window_title=window_title,
        window_size=window_size,
        scale=scale,
    )


def create_display(
    motherboard: Motherboard,
    window_title: str,
    window_size: Tuple[int, int] = (160, 144),
    scale: int = 2,
    backend: str = 'pyglet',
) -> BaseDisplay:
    return _create_display(
        mapping=impl_mapping,
        motherboard=motherboard,
        window_title=window_title,
        window_size=window_size,
        scale=scale,
        backend=backend,
    )


def create_debug_display(
    motherboard: Motherboard,
    window_title: str,
    window_size: Tuple[int, int] = (160, 144),
    scale: int = 2,
    backend: str = 'pyglet',
) -> BaseDisplay:
    return _create_display(
        mapping=debug_impl_mapping,
        motherboard=motherboard,
        window_title=window_title,
        window_size=window_size,
        scale=scale,
        backend=backend,
    )
