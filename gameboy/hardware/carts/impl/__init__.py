from types import ModuleType
from typing import Dict

from gameboy.hardware.carts.constants import CartImplType

from . import rom_only as ROM_ONLY

impl_mapping: Dict[CartImplType, ModuleType] = {
    CartImplType.ROM_ONLY: ROM_ONLY,
}
