from enum import Enum
from typing import List
from collections import deque
import keyboard

#class State(Enum):
    #GAMEPLAY = 0
    #TERMINAL = 1
    #ADD_TRAP = 2
    #DELETE_TRAP = 3
    #INSERT_TEXT = 4
    #SWITCH_PLAYER = 5
    #ALL_TRAPS = 6

class StateManager:
    def __init__(self):
        self.buffer = deque([]) # will be flushed with 'enter'

        self.set_state_to_gameplay()
    
    def is_typed(self, array: List[str]):
        if len(self.buffer) < len(array): 
            return False
        
        # Check last n elements directly from deque
        for i in range(len(array)):
            if self.buffer[-(i + 1)] != array[-(i + 1)]:
                return False
        
        return True

    def listen_to_keyboard(self, callback, suppress=True):
        def add_to_buffer(key):
            print(key.name)
            self.buffer.append(key.name)
            print(self.buffer)

            callback()

            # Flush on enter
            if key.name == 'enter':
                self.buffer.clear()

            if len(self.buffer) > 50:
                self.buffer.popleft()
            # No need for more than 50 characters in reality

        keyboard.on_press(add_to_buffer, suppress=suppress)

    def set_state_to_gameplay(self):
        keyboard.unhook_all()
        print("gaming")

        def handle_transitions():
            # Enter Terminal State
            if self.is_typed(['t', 'enter']):
                self.set_state_to_terminal()

        self.listen_to_keyboard(handle_transitions, False)

    def set_state_to_terminal(self):
        keyboard.unhook_all()

        print("terminal")

        def handle_transitions():
            # Enter Gameplay State
            if self.is_typed(['tab', 'tab']):
                self.set_state_to_gameplay()

        self.listen_to_keyboard(handle_transitions, True)
