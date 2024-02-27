from dataclasses import dataclass
from enum import IntEnum, auto


class EventType(IntEnum):

    IGNORED = auto()
    QUIT = auto()
    PRESS_ARROW_UP = auto()
    PRESS_ARROW_DOWN = auto()
    PRESS_ARROW_LEFT = auto()
    PRESS_ARROW_RIGHT = auto()
    PRESS_BUTTON_A = auto()
    PRESS_BUTTON_B = auto()
    PRESS_BUTTON_START = auto()
    PRESS_BUTTON_SELECT = auto()
    RELEASE_ARROW_UP = auto()
    RELEASE_ARROW_DOWN = auto()
    RELEASE_ARROW_LEFT = auto()
    RELEASE_ARROW_RIGHT = auto()
    RELEASE_BUTTON_A = auto()
    RELEASE_BUTTON_B = auto()
    RELEASE_BUTTON_START = auto()
    RELEASE_BUTTON_SELECT = auto()
    MEMORY_VIEW_SCROLL_DOWN = auto()
    MEMORY_VIEW_SCROLL_UP = auto()


@dataclass
class Event:

    type: EventType = EventType.IGNORED
    window_id: int = 0
