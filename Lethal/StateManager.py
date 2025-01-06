from enum import Enum
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
        self.buffer = [] # will be flushed with 'enter'

        self.set_state_to_gameplay()
    
    def listen_to_keyboard(self, callback, suppress=True):
        def add_to_buffer(key):
            print(key.name)
            self.buffer.append(key.name)
            print(self.buffer)

            callback()

            # No need for more than 50 characters in reality
            if key.name == 'enter' or len(self.buffer) > 50:
                self.buffer.clear()


        keyboard.on_press(add_to_buffer, suppress=suppress)

    def set_state_to_gameplay(self):
        keyboard.unhook_all()
        print("gaming")

        def handle_transitions():
            # Enter Terminal State
            if len(self.buffer) >= 2 and self.buffer[-2:] == ['t', 'enter']:
                self.set_state_to_terminal()

        self.listen_to_keyboard(handle_transitions, False)

    def set_state_to_terminal(self):
        keyboard.unhook_all()

        print("terminal")

        def handle_transitions():
            # Enter Gameplay State
            if len(self.buffer) >= 2 and self.buffer[-2:] == ['tab', 'tab']:
                self.set_state_to_gameplay()

        self.listen_to_keyboard(handle_transitions, True)
