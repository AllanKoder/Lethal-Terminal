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
        self.traps = set() # List of traps

        self.gameplay_state()
    
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

            # No need for more than 50 characters in reality
            if len(self.buffer) > 50:
                self.buffer.popleft()

        keyboard.on_press(add_to_buffer, suppress=suppress)
    
    def keyboard_setup(func):
        def decorator(self):
            keyboard.unhook_all()
        
            func(self)
        return decorator

    def handle_control_c(self):
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()

    @keyboard_setup
    def gameplay_state(self):
        print("gaming")

        def handle_transitions():
            # Enter Terminal State
            if self.is_typed(['t', 'enter']):
                self.terminal_state()

        self.listen_to_keyboard(handle_transitions, False)

    @keyboard_setup
    def terminal_state(self):

        print("terminal")

        def handle_transitions():
            # Enter Gameplay State
            if self.is_typed(['tab', 'tab']):
                self.gameplay_state()
            if self.is_typed(['a']):
                self.add_trap_state()
            self.handle_control_c()

        self.listen_to_keyboard(handle_transitions, True)

    @keyboard_setup
    def add_trap_state(self):
        print("add trap state")

        def handle_transitions():
            if (len(self.buffer) >= 3 and self.buffer[-1] == 'enter'):
                trap = self.buffer[-2] + self.buffer[-3]
                self.traps.add(trap)
                print(trap)

            self.handle_control_c()

        self.listen_to_keyboard(handle_transitions, True)
