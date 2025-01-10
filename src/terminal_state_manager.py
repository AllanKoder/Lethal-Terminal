from enum import Enum
from typing import List
from collections import deque
from time import sleep, time
import keyboard
import threading

from .traps import is_valid_trap
from .keyboard_manager import keyboard_setup
from .config import ConfigSingleton
from .terminal_ui import TerminalUI

class State(Enum):
    GAMEPLAY = 0
    TERMINAL = 1
    ADD_TRAP = 2
    DELETE_TRAP = 3
    INSERT_TEXT = 4
    TRANSMIT_TEXT = 5
    PING_RADAR = 6

class TerminalStateManager:
    def __init__(self, keyboard_manager):
        self.buffer = deque([]) # What the keyboard has typed
        self.to_be_written = deque([]) # What the user is about to write before the interuption by the automated trap system
        self.writing_queue = deque([]) # The things that are to be typed

        # The traps (e.g. mines, turrets)
        self.traps = set() # List of traps
        # All the traps in the game
        self.all_traps = {f"{chr(i)}{j}" for i in range(ord('a'), ord('z')+1) for j in range(10)}

        # Flags
        self.first_terminal_enter = True # Makes you type view monitor on the first go
        self.run_auto_trap_thread = True
        self.want_all_traps = False # Will type all combinations
        self.is_auto_typing_traps = False # Is the computer typing the traps right now?
        self.is_running_manager = False

        # Timer for the trap thread
        self.start_time = time()

        # Config
        self.config = ConfigSingleton()
        # Keyboard
        self.keyboard_manager = keyboard_manager

        # The current state
        self.state = State.GAMEPLAY

        # The UI
        self.terminal_ui = TerminalUI(self)
        self.terminal_ui.render()
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
            case State.TRANSMIT_TEXT:
                self.handle_suffix_text_enter_keyboard()
            case State.PING_RADAR:
                self.handle_suffix_text_enter_keyboard()
            
    def handle_key_buffer(self, key: str):
        # Add the key to the buffer
        self.buffer.append(key.name)

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
        self.state = State.GAMEPLAY
        self.first_terminal_enter = True
        self.clear_all_buffers() # Stop writing
        self.run_auto_trap_thread = False

        self.listen_to_keyboard(False)
    def handle_gameplay_keyboard(self):
        # Enter Terminal State
        if self.is_typed(['t', 'enter']):
            self.terminal_state()

    @keyboard_setup
    def terminal_state(self):
        self.state = State.TERMINAL
        self.listen_to_keyboard(True)
        self.clear_to_be_written_buffer() # Clear buffer
        self.run_auto_trap_thread = True
        if not self.is_running_manager:
            threading.Thread(target=self.automatic_trap_writing_manager).start()

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
        # Transmit message state
        elif self.is_typed(['t']):
            self.transmit_text_state()
        # Ping
        elif self.is_typed(['p']):
            self.ping_state()
        # Go to player (switch)
        elif self.is_typed(['g']):
            self.ping_state()
        # Set all the traps
        elif self.is_typed(['q', 'q']):
            if self.want_all_traps: # Don't write if we disabled all traps
                self.writing_queue.clear()
            self.want_all_traps = not self.want_all_traps
        
        # Control + C wipes buffer
        self.handle_control_c()


    @keyboard_setup
    def add_trap_state(self):
        self.state = State.ADD_TRAP
        self.listen_to_keyboard(True)

    def handle_adding_trap_keyboard(self):
        if (len(self.buffer) >= 3 and self.buffer[-1] == 'enter'):
            trap = (self.buffer[-3] + self.buffer[-2])
            if is_valid_trap(trap):
                self.traps.add(trap)

                # Return to Terminal State
                self.terminal_state()

        self.handle_control_c()


    @keyboard_setup
    def remove_trap_state(self):
        self.state = State.DELETE_TRAP
        self.listen_to_keyboard(True)

    def handle_delete_trap_keyboard(self):
        if (len(self.buffer) >= 3 and self.buffer[-1] == 'enter'):
            trap = (self.buffer[-3] + self.buffer[-2])
            if is_valid_trap(trap) and trap in self.traps:
                self.traps.remove(trap)

                # Return to Terminal State
                self.terminal_state()

        self.handle_control_c()

    def insert_event_to_be_written(self, key_event: str):
        # Add the latest event to the to_be_written list
        self.to_be_written.append(key_event)
        # If the system is not typing traps, handle user input directly
        if not self.is_auto_typing_traps:
            # handle the inputs given
            self.keyboard_manager.press_key(key_event)

            # Clear the buffer since it is a newline
            if key_event == 'enter':
                self.clear_to_be_written_buffer()
            
        
        # System is typing traps
        else:
            if key_event == 'enter':
                # Send the line that was desired to be typed to the writing queue
                self.writing_queue.appendleft(("user", deque(self.to_be_written)))
                self.clear_to_be_written_buffer()
        
        # Clean the to_be_written buffer, we don't want to save deletes, since it is just removing elements from the buffer
        if key_event == 'backspace':
            self.to_be_written.pop()
            if len(self.to_be_written) > 0:
                self.to_be_written.pop()
        
        self.terminal_ui.render()
            
        
    @keyboard_setup
    def insert_text_state(self):
        self.state = State.INSERT_TEXT
        self.listen_to_keyboard(True)
    def handle_insert_text_keyboard(self):
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
            self.insert_event_to_be_written(k)

    @keyboard_setup
    def transmit_text_state(self):
        self.to_be_written.clear()
        for k in ['enter','t','r','a','n','s','m','i','t','space']:
            self.insert_event_to_be_written(k)
        
        self.state = State.TRANSMIT_TEXT
        self.listen_to_keyboard(True)
    @keyboard_setup
    def ping_state(self):
        self.to_be_written.clear()
        for k in ['enter','p','i','n','g','space']:
            self.insert_event_to_be_written(k)
        
        self.state = State.PING_RADAR
        self.listen_to_keyboard(True)
    def handle_suffix_text_enter_keyboard(self):
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()
            return

        event = self.buffer[-1]
        self.insert_event_to_be_written(event)

        # Finished writing
        if event == 'enter':
            self.terminal_state()

    def clear_to_be_written_buffer(self):
        self.to_be_written.clear()
        self.terminal_ui.render()

    # Thread to handle writing the trap
    def start_automatic_trap_writing(self):
        bot_input_delay = self.config.get("BOT_INPUT_DELAY")
        user_input_delay = self.config.get("USER_INPUT_DELAY")

        self.is_auto_typing_traps = True

        trap_set = self.traps
        if self.want_all_traps:
            trap_set = self.all_traps

        for trap in trap_set:
            self.writing_queue.extend(deque([("bot",f"{trap}\n")]))

        # In case the user hasn't finished typing something
        keyboard.write("\n", delay=bot_input_delay) 
        while len(self.writing_queue) > 0:
            # Write could be of type list of strings or a single key
            type, write = self.writing_queue.popleft()

            waiting = 0 # Time to wait for timing this function correctly, so it ends when the typing ends as well
            match type:
                case "bot":
                    keyboard.write(write, delay=bot_input_delay)
                    waiting = (len(write)) * bot_input_delay
                case "user":
                    keyboard.write("\n", delay=bot_input_delay)
                    for key in write:
                        self.keyboard_manager.press_key(key)
                    keyboard.write("\n", delay=bot_input_delay)
                    waiting = len(write) * user_input_delay + 2 * bot_input_delay
                    
            # The delay is doubled (not sure why x2 is better, but it works better this way)
            # Need some help figuring out the timing for this thread
            sleep(waiting*2) 
        
        time_since_start_of_trap_thread = time() - self.start_time
        time_left = self.config.get("TRAP_TIMER_DURATION") - time_since_start_of_trap_thread
        # If there is time to return the terminal back to normal
        if time_left > 0:
            # Try catch since the user could clear the self.to_be_written buffer at any time
            try:
                # Finish off user typed buffer that is not done from the terminal
                for i in range(len(self.to_be_written)):
                    self.keyboard_manager.press_key(self.to_be_written[i])
                sleep(len(self.to_be_written)*2*user_input_delay)
            except:
                sleep(user_input_delay)

        self.is_auto_typing_traps = False
    
    def clear_all_buffers(self):
        self.clear_to_be_written_buffer()
        self.writing_queue.clear()

    def automatic_trap_writing_manager(self):
        ideal_timer = self.config.get("TRAP_TIMER_DURATION")

        initial_call = True
        self.is_running_manager = True
        while self.run_auto_trap_thread:
            if self.state is not State.GAMEPLAY:
                self.start_time = time()

                if initial_call:
                    sleep(1)
                    initial_call = False

                if (len(self.traps) > 0 or self.want_all_traps):
                    thread = threading.Thread(target=self.start_automatic_trap_writing)
                    thread.start()
                    thread.join()

                elapsed_time = time() - self.start_time
                remaining_time = max(0, ideal_timer - elapsed_time)

                while remaining_time > 0 and self.state is not State.GAMEPLAY:
                    sleep_time = min(0.1, remaining_time)
                    sleep(sleep_time)
                    remaining_time -= sleep_time

            else:
                sleep(0.1)
        self.is_running_manager = False