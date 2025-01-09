from enum import Enum
from typing import List
from collections import deque
from time import sleep, time
import keyboard
import threading

from .traps import is_valid_trap
from .keyboard_manager import keyboard_setup
from .config import ConfigSingleton

class State(Enum):
    GAMEPLAY = 0
    TERMINAL = 1
    ADD_TRAP = 2
    DELETE_TRAP = 3
    INSERT_TEXT = 4

class TerminalStateManager:
    def __init__(self, keyboard_manager):
        self.buffer = deque([]) # What the keyboard has typed
        self.to_be_written = deque([]) # What the user is about to write before the interuption by the automated trap system
        self.writing_queue = deque([]) # The things that are to be typed

        # The traps (e.g. mines, turrets)
        self.traps = set() # List of traps
        # All the traps in the game
        self.all_traps = {f"{chr(i)}{j}" for i in range(ord('a'), ord('i')+1) for j in range(10)}

        # Flags
        self.first_terminal_enter = True # Makes you type view monitor on the first go
        self.running_auto_trap_thread = True
        self.is_auto_typing_traps = False # Is the computer typing the traps right now?

        # Config
        self.config = ConfigSingleton()
        # Keyboard
        self.keyboard_manager = keyboard_manager
        
        # The current state
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
            if not self.is_auto_typing_traps:
                threading.Thread(target=self.start_automatic_trap_writing).start()

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

    def listen_to_keyboard(self, suppress):
        # If is auto typing, suppress the user input
        keyboard.on_press(self.handle_key_buffer, suppress=suppress)
    
    # Reduce repeated code for keyboard setup

    def handle_control_c(self):
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()

    @keyboard_setup
    def gameplay_state(self):
        print("gaming state")
        self.state = State.GAMEPLAY
        self.first_terminal_enter = True
        self.writing_queue.clear() # Stop writing
        self.listen_to_keyboard(False)
    def handle_gameplay_keyboard(self):
        # Enter Terminal State
        if self.is_typed(['t', 'enter']):
            self.terminal_state()

    @keyboard_setup
    def terminal_state(self):
        print("terminal state")
        self.state = State.TERMINAL
        self.listen_to_keyboard(True)

        if self.first_terminal_enter:
            self.first_terminal_enter = False
            self.insert_view_monitor_text()
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
        # Enter switch player
        elif self.is_typed(['s']):
            self.insert_switch_player_text()
        # Enter view monitor text
        elif self.is_typed(['m']):
            self.insert_view_monitor_text()
        
        # Control + C wipes buffer
        self.handle_control_c()


    @keyboard_setup
    def add_trap_state(self):
        print("add trap state")
        self.state = State.ADD_TRAP
        self.listen_to_keyboard(True)

    def handle_adding_trap_keyboard(self):
        if (len(self.buffer) >= 3 and self.buffer[-1] == 'enter'):
            trap = (self.buffer[-3] + self.buffer[-2])
            print("adding", trap)
            if is_valid_trap(trap):
                self.traps.add(trap)

                # Return to Terminal State
                self.terminal_state()

        self.handle_control_c()


    @keyboard_setup
    def remove_trap_state(self):
        print("remove trap state")
        self.state = State.DELETE_TRAP
        self.listen_to_keyboard(True)

    def handle_delete_trap_keyboard(self):
        if (len(self.buffer) >= 3 and self.buffer[-1] == 'enter'):
            trap = (self.buffer[-3] + self.buffer[-2])
            print("removing", trap)
            if is_valid_trap(trap) and trap in self.traps:
                self.traps.remove(trap)

                # Return to Terminal State
                self.terminal_state()

        self.handle_control_c()

    def insert_event_to_be_written(self, key_event: str):
        # Add the latest event to the to_be_written list
        self.to_be_written.append(key_event)
        print("TO BE WRITTEN", self.to_be_written)
        # If the system is not typing traps, handle user input directly
        if not self.is_auto_typing_traps:
            # handle the inputs given
            self.keyboard_manager.press_key(key_event)

            # Clear the buffer since it is a newline
            if key_event == 'enter':
                self.to_be_written.clear()
            
        
        # System is typing traps
        else:
            if key_event == 'enter':
                # Send the line that was desired to be typed to the writing queue
                self.writing_queue.appendleft(("user", deque(self.to_be_written)))
                self.to_be_written.clear()

    @keyboard_setup
    def insert_text_state(self):
        print("insert text state")
        self.state = State.INSERT_TEXT
        self.listen_to_keyboard(True)
    def handle_insert_text_keyboard(self):
        # TODO: Make handling control c a decorator
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()
            return

        event = self.buffer[-1]
        self.insert_event_to_be_written(event)

    def insert_switch_player_text(self):
        for k in ['enter', 's','w','i','t','c','h','enter']:
            self.insert_event_to_be_written(k)
    
    def insert_view_monitor_text(self):
        for k in ['enter','v','i','e','w','space','m','o','n','i','t','o','r','enter']:
            # This command takes more time, needs more waiting
            self.insert_event_to_be_written(k)

    # Thread to handle writing the trap
    def start_automatic_trap_writing(self):
        print("STARTED WRITING")
        self.is_auto_typing_traps = True
        for trap in self.traps:
            self.writing_queue.extend(deque([("bot",f"\n{trap}\n")]))  # two \n\n in case one is missed
        
        while len(self.writing_queue) > 0:
            # Write could be of type list of strings or a single key
            type, write = self.writing_queue.popleft()

            waiting = 0 # Time to wait for timing this function correctly, so it ends when the typing ends as well
            input_delay = self.config.get("INPUT_DELAY")
            match type:
                case "bot":
                    keyboard.write(write, delay=input_delay)
                    # +2 for good measure on waiting
                    waiting = (len(write)+2) * input_delay
                case "user":
                    keyboard.write("\n", delay=input_delay)
                    for key in write:
                        self.keyboard_manager.press_key(key)
                    keyboard.write("\n", delay=input_delay)
                    # +4 on good measure on waiting
                    waiting = (len(write)+4) * input_delay
       
            sleep(waiting)
        
        self.is_auto_typing_traps = False

        # Finish off buffer that is not done from the terminal
        for i in range(len(self.to_be_written)):
            self.keyboard_manager.press_key(self.to_be_written[i])

        print("ENDING WRITING")

    def stop(self):
        self.running_auto_trap_thread = False

    def automatic_trap_writing_manager(self):
        ideal_timer = 5
        while self.running_auto_trap_thread:
            if self.state is not State.GAMEPLAY:
                sleep(1)
                starting_time = time()
                thread = threading.Thread(target=self.start_automatic_trap_writing)
                thread.start()
                thread.join()
                ending_time = time()

                time_already_used = ending_time - starting_time
                time_to_wait = ideal_timer - time_already_used - 1
                if time_to_wait > 0:
                    sleep(time_to_wait)
            else:
                sleep(0.1)
