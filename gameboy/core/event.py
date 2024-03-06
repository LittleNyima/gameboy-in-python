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


JOYPAD_EVENTS = {
    EventType.PRESS_ARROW_UP,
    EventType.PRESS_ARROW_DOWN,
    EventType.PRESS_ARROW_RIGHT,
    EventType.PRESS_ARROW_LEFT,
    EventType.PRESS_BUTTON_A,
    EventType.PRESS_BUTTON_B,
    EventType.PRESS_BUTTON_START,
    EventType.PRESS_BUTTON_SELECT,
    EventType.RELEASE_ARROW_UP,
    EventType.RELEASE_ARROW_DOWN,
    EventType.RELEASE_ARROW_RIGHT,
    EventType.RELEASE_ARROW_LEFT,
    EventType.RELEASE_BUTTON_A,
    EventType.RELEASE_BUTTON_B,
    EventType.RELEASE_BUTTON_START,
    EventType.RELEASE_BUTTON_SELECT,
}


@dataclass
class Event:

    type: EventType = EventType.IGNORED
    window_id: int = 0
