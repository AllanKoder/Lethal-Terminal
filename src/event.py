
from enum import Enum

class EventType(Enum):
    SUCCESS = 0
    FAIL = 1
    NONE = 2
class Event():
    def __init__(self, text, type):
        self.text = text
        self.type = type