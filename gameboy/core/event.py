from dataclasses import dataclass
from enum import IntEnum, auto


class EventType(IntEnum):

    IGNORED = auto()
    QUIT = auto()
    MEMORY_VIEW_SCROLL_DOWN = auto()
    MEMORY_VIEW_SCROLL_UP = auto()


@dataclass
class Event:

    type: EventType = EventType.IGNORED
    window_id: int = 0
