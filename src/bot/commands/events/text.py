from enum import StrEnum


class EventName(StrEnum):
    PAST = "past"
    FUTURE = "future"


class EventText:
    BUTTON_LABELS = {
        EventName.PAST: "Past Events",
        EventName.FUTURE: "Future Games",
    }
