from enum import Enum
from typing import List
from collections import deque
from time import sleep
import keyboard
import threading


class State(Enum):
    GAMEPLAY = 0
    TERMINAL = 1
    ADD_TRAP = 2
    DELETE_TRAP = 3
    INSERT_TEXT = 4
    SWITCH_PLAYER = 5
    ALL_TRAPS = 6
    AUTOMATIC_TRAPS = 7

class StateManager:
    def __init__(self):
        self.buffer = deque([]) # will be flushed with 'enter'
        self.to_be_written = deque([]) # What the user is about to write
        self.unfinished_writing_in_terminal = deque([]) # What the user didn't finish while the automation was happening
        self.writing_queue = deque([])
        self.traps = set([ a + str(n) for a in 'abcdefghi' for n in range(0,10)]) # List of traps

        self.suppress = False # Suppress the keyboard
        self.is_auto_typing_traps = [False] # Is the computer typing the traps right now?
        self.state = None
        self.gameplay_state()

    # Check if the last few characters in the buffer have been typed to the array
    def is_typed(self, array: List[str]):
        if len(self.buffer) < len(array): 
            return False
        
        # Check last n elements directly from deque
        for i in range(len(array)):
            if self.buffer[-(i + 1)] != array[-(i + 1)]:
                return False
        
        return True

    def handle_keyboard_logic(self):
        match self.state:            
            case State.GAMEPLAY:
                self.handle_gameplay_keyboard()
            case State.TERMINAL:
                self.handle_terminal_keyboard()
            case State.ADD_TRAP:
                self.handle_adding_trap_keyboard()
            case State.DELETE_TRAP:
                self.handle_delete_trap_keyboard()
            case State.INSERT_TEXT:
                self.handle_insert_text_keyboard()
            
        if self.is_typed(['q', 'q']):
            t1 = threading.Thread(target=self.automatic_trap_writing, args=(self.is_auto_typing_traps, self.writing_queue))
            t1.start()

    def handle_key_buffer(self, key: str):
        print(key.name)
        # Add the key to the buffer
        self.buffer.append(key.name)
        print(self.buffer)

        self.handle_keyboard_logic()

        # Flush on enter
        if key.name == 'enter':
            self.buffer.clear()

        # No need for more than 50 characters in reality
        if len(self.buffer) > 50:
            self.buffer.popleft()

    def listen_to_keyboard(self):
        # If is auto typing, suppress the user input
        suppress = self.suppress or self.is_auto_typing_traps[0]

        keyboard.on_press(self.handle_key_buffer, suppress=suppress)
    
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
        print("gaming state")
        self.state = State.GAMEPLAY
        self.suppress = False
        self.listen_to_keyboard()

    def handle_gameplay_keyboard(self):
        # Enter Terminal State
        if self.is_typed(['t', 'enter']):
            self.terminal_state()


    @keyboard_setup
    def terminal_state(self):
        print("terminal state")
        self.state = State.TERMINAL
        self.suppress = True
        self.listen_to_keyboard()

    def handle_terminal_keyboard(self):
        # Enter Gameplay State
        if self.is_typed(['tab', 'tab']):
            self.gameplay_state()
        # Enter Adding Trap State
        elif self.is_typed(['a']):
            self.add_trap_state()
        # Enter Removing Trap State
        elif self.is_typed(['x']):
            self.remove_trap_state()
        # Enter Text Insertion state
        elif self.is_typed(['i']):
            self.insert_text_state()
        
        # Control + C wipes buffer
        self.handle_control_c()


    def is_valid_trap(self, trap: str):
        if len(trap) != 2:
            print(" bad len")
            return False
        if not trap[0].isalpha():
            print("not letter", trap[0])
            return False
        if not trap[1].isdigit():
            print ("not numb")
            return False
        return True


    @keyboard_setup
    def add_trap_state(self):
        print("add trap state")
        self.state = State.ADD_TRAP
        self.suppress = True
        self.listen_to_keyboard()

    def handle_adding_trap_keyboard(self):
        if (len(self.buffer) >= 3 and self.buffer[-1] == 'enter'):
            trap = (self.buffer[-3] + self.buffer[-2])
            print("adding", trap)
            if self.is_valid_trap(trap):
                self.traps.add(trap)

        self.handle_control_c()



    @keyboard_setup
    def remove_trap_state(self):
        print("remove trap state")
        self.state = State.DELETE_TRAP
        self.suppress = True
        self.listen_to_keyboard()

    def handle_delete_trap_keyboard(self):
        if (len(self.buffer) >= 3 and self.buffer[-1] == 'enter'):
            trap = (self.buffer[-3] + self.buffer[-2])
            print("removing", trap)
            if self.is_valid_trap(trap) and trap in self.traps:
                self.traps.remove(trap)

        self.handle_control_c()


    @keyboard_setup
    def insert_text_state(self):
        print("insert text state")
        self.state = State.INSERT_TEXT
        self.suppress = True
        self.listen_to_keyboard()

    def handle_insert_text_keyboard(self):
        # TODO: Make handling control c a decorator
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()
            return

        event = self.buffer[-1]

        # Add the latest event to the to_be_written list
        self.to_be_written.append(event)

        # If the system is not typing traps, handle user input directly
        if not self.is_auto_typing_traps[0]:
            keyboard.press_and_release(event)

            # Clear the buffer since it is a newline
            if event == 'enter':
                self.to_be_written.clear()
        
        # System is typing traps
        else:
            self.unfinished_writing_in_terminal.append(event)
            if event == 'enter':
                # Send the line that was desired to be typed to the writing queue
                self.writing_queue.appendleft(("user", deque(self.to_be_written)))
                self.to_be_written.clear()
                self.unfinished_writing_in_terminal.clear()


    def automatic_trap_writing(self, is_auto_typing_traps, writing_queue):
        print("STARTED WRITING")
        is_auto_typing_traps[0] = True
        for trap in self.traps:
            writing_queue.extend(deque([("bot",f"{trap}\n\n")]))  # Pre-fill with lines
        
        while len(writing_queue) > 0:
            DELAY = 0.016
            type, write = writing_queue.popleft()

            match type:
                case "bot":
                    keyboard.write(write, delay=DELAY)
                case "user":
                    for key in write:
                        keyboard.press(key)
                        sleep(DELAY)
                        keyboard.release(key)
                    keyboard.write("\n")
       
            waiting = (len(write)+1) * DELAY
            sleep(waiting)
        
        is_auto_typing_traps[0] = False

        # Finish off buffer that is not done from the terminal
        while len(self.unfinished_writing_in_terminal) > 0:
            keyboard.press_and_release(self.unfinished_writing_in_terminal.popleft())

        print("ENDING WRITING")
