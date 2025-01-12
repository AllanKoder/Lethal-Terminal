
from enum import Enum

# Enum to define different types of Log events for the UI
class EventType(Enum):
    SUCCESS = 0
    FAIL = 1
    NONE = 2

# Represents an event in the UI
class Event():
    def __init__(self, text: str, type: EventType):
        self.text = text
        self.type = type