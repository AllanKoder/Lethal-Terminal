from enum import Enum
from typing import Callable, List, Optional
from collections import deque
from time import sleep, time
import keyboard
import threading
from logging import Logger

from .traps import is_valid_trap
from .keyboard_manager import keyboard_setup, KeyboardManager
from .config import ConfigSingleton
from .event import Event, EventType

# Representing the states which the vim motions is in
class State(Enum):
    GAMEPLAY = 0
    TERMINAL = 1
    ADD_TRAP = 2
    DELETE_TRAP = 3
    INSERT_TEXT = 4
    TRANSMIT_TEXT = 5
    SWITCH_USER = 6
    FLASH_RADAR = 7
    PING_RADAR = 8

# The brain behind the whole operation
class TerminalStateManager:
    def __init__(self, keyboard_manager: KeyboardManager, logger: Logger):
        # Keyboard buffers
        self.buffer = deque([]) # What the keyboard has typed
        self.to_be_written = deque([]) # What the user is about to write before the interuption by the automated trap system
        self.writing_queue = deque([]) # The things that are to be typed

        # The traps (e.g. mines, turrets)
        self.traps = [] # List of traps
        # All the traps in the game
        self.all_traps = [f"{chr(i)}{j}" for i in range(ord('a'), ord('z')+1) for j in range(10)]
        self.current_trap = [] # What the user is typing

        # Flags
        self.first_terminal_enter = True # Makes you type view monitor on the first go
        self.run_auto_trap_thread = True
        self.want_all_traps = False # Will type all combinations
        self.is_auto_typing_traps = False # Is the computer typing the traps right now?
        self.is_running_manager = False

        # UI
        self.event = Event("", EventType.NONE)
        self.refresh_callback = None # Refreshing UI callback

        # Timer for the trap thread
        self.start_time = time()

        # Dependencies
        self.keyboard_manager = keyboard_manager
        self.logger = logger
        self.config = ConfigSingleton() # Config

        # The Current State
        self.state = State.GAMEPLAY

        self.logger.debug("TerminalStateManager initialized.")
        self.gameplay_state()
    
    # Set the function for refreshing the UI
    def set_refresh_callback(self, callback: Callable) -> None:
        self.refresh_callback = callback

    # Set the event to display
    def set_event(self, text: str, type: Optional[EventType] = EventType.SUCCESS) -> None:
        self.event.text = text
        self.event.type = type

    # Clear all the things that was about to be written
    def clear_to_be_written_buffer(self) -> None:
        self.to_be_written.clear()

    # Check if the last few characters in the buffer have been typed to the array
    def is_typed(self, array: List[str]) -> bool:
        '''Check if the array of keys has been typed in the user keyboard'''
        if len(self.buffer) < len(array): 
            return False
        
        # Check last n elements directly from deque
        for i in range(len(array)):
            if self.buffer[-(i + 1)].lower() != array[-(i + 1)].lower():
                return False
        
        return True

    def handle_keyboard_logic(self) -> None:
        '''Keyboard logic for all states'''
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
                self.handle_radar_command("ping")
            case State.FLASH_RADAR:
                self.handle_radar_command("flash")
            case State.SWITCH_USER:
                self.handle_switch_user_keyboard()
            
    def handle_key_buffer(self, key: str) -> None:
        '''Handling the addition of a new keyboard input'''

        # Add the key to the buffer
        self.buffer.append(key.name)
        self.handle_keyboard_logic()

        # Flush on enter
        if key.name == 'enter':
            self.buffer.clear()

        # No need for more than 50 characters in reality
        if len(self.buffer) > 50:
            self.buffer.popleft()
    
    def listen_to_keyboard(self, suppress: bool) -> None:
        # If is auto typing, suppress the user input
        keyboard.unhook_all()
        keyboard.on_press(self.handle_key_buffer, suppress=suppress)

    def handle_control_c(self) -> None:
        '''Logic for pressing control+c'''
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()

    @keyboard_setup(False)
    def gameplay_state(self) -> None:
        self.state = State.GAMEPLAY
        self.clear_all_buffers() # Stop writing
        self.run_auto_trap_thread = False

    def handle_gameplay_keyboard(self) -> None:
        # Enter Terminal State
        if self.is_typed(['t', 'enter']):
            self.terminal_state()
            self.insert_event_to_be_written('enter')

    @keyboard_setup()
    def terminal_state(self) -> None:
        self.state = State.TERMINAL
        self.clear_to_be_written_buffer() # Clear buffer
        self.run_auto_trap_thread = True
        if not self.is_running_manager:
            threading.Thread(target=self.automatic_trap_writing_manager).start()

        if self.first_terminal_enter:
            self.first_terminal_enter = False
            self.insert_view_monitor_text()
    def handle_terminal_keyboard(self) -> None:
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
            self.switch_user_state()
        # Enter view monitor text
        elif self.is_typed(['v']):
            self.insert_view_monitor_text()
        # Transmit message state
        elif self.is_typed(['t']):
            self.transmit_text_state()
        # Ping
        elif self.is_typed(['p']):
            self.switch_ping_state()
        # Flash a Radar
        elif self.is_typed(['f']):
            self.switch_flash_state()
        # Set all the traps
        elif self.is_typed(['q', 'q']):
           self.toggling_all_traps()
       
        # Control + C wipes buffer
        self.handle_control_c()

    def toggling_all_traps(self):
        if self.want_all_traps: 
            self.writing_queue.clear() # Don't write if we disabled all traps
            self.want_all_traps = False
            self.set_event("Disabled typing all traps")
        elif not self.want_all_traps:
            self.want_all_traps = True
            self.set_event("Enabled typing all traps")

        if self.refresh_callback:
            self.refresh_callback()
        self.terminal_state()

    @keyboard_setup()
    def add_trap_state(self) -> None:
        self.state = State.ADD_TRAP
        self.current_trap.clear()

    def handle_adding_trap_keyboard(self) -> None:
        '''Logic for adding a trap (a1, b2) to the trap list'''
        if len(self.buffer) >= 1 and len(self.buffer[-1]) == 1:
            self.current_trap.append(self.buffer[-1])

            # Handle delete
            if self.buffer[-1] == 'backspace':
                self.current_trap.pop()
                if len(self.current_trap) > 0:
                    self.current_trap.pop()


        if (len(self.current_trap) == 2):
            trap = (self.current_trap[0] + self.current_trap[1])
            if is_valid_trap(trap) and trap not in self.traps:
                self.traps.append(trap)
                self.set_event(f"Added trap: {trap}")

                # Type the trap inputted
                self.insert_event_to_be_written('enter')
                for k in trap:
                    self.insert_event_to_be_written(k) 
                self.insert_event_to_be_written('enter')

            else:
                self.set_event(f"Cannot add trap: {trap}", EventType.FAIL)

            # Return to Terminal State
            self.terminal_state()

        self.handle_control_c()


    @keyboard_setup()
    def remove_trap_state(self) -> None:
        self.state = State.DELETE_TRAP
        self.current_trap.clear()

    def handle_delete_trap_keyboard(self) -> None:
        '''Logic for removing a trap (a1, b2) from the trap list'''
        if len(self.buffer) >= 1 and len(self.buffer[-1]) == 1:
            self.current_trap.append(self.buffer[-1])

            # Handle delete
            if self.buffer[-1] == 'backspace':
                self.current_trap.pop()
                if len(self.current_trap) > 0:
                    self.current_trap.pop()

            if (len(self.current_trap) == 2):
                trap = (self.current_trap[0] + self.current_trap[1])
                if is_valid_trap(trap) and trap in self.traps:
                    self.traps.remove(trap)
                    self.set_event(f"Removed trap: {trap}")
                else:
                    self.set_event(f"Cannot remove trap: {trap}", EventType.FAIL)
                # Return to Terminal State
                self.terminal_state()

        self.handle_control_c()

    def press_key_and_wait(self, key_event: str) -> None:
        '''A function to pause the caller by the estimated amount of time the keypress would take.
        
        Timing is important overwise the writing_queue buffer would be overloaded with keys from start_automatic_trap_writing thread
        Since we timed the key presses, we can update the writing_queue buffer and get live changes while the traps are being written
        '''
        self.keyboard_manager.press_key(key_event)
        keyboard_delay = self.config.get("KEYBOARD_INPUT_DELAY")*1.3 # Added processing speed estimate
        sleep(keyboard_delay)

    def insert_event_to_be_written(self, key_event: str) -> None:
        '''Handling typing a key.
        
        If the system is not typing anything, just type the key and save it to the buffer
        When the system is typing, there is nothing typed. Afterwards, state is recovered by typing the to_be_written buffer'''
        # Add the latest event to the to_be_written list
        if len(key_event) == 1 or key_event in ['space', 'backspace']:
            self.to_be_written.append(key_event)
            self.logger.debug(f"to_be_written buffer is {self.to_be_written}")
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
                # Update UI Event
                self.set_event(f"Will type: {self.keyboard_manager.keys_to_string(self.to_be_written)}")
                if self.refresh_callback():
                    self.refresh_callback()

                # Send the line that was desired to be typed to the writing queue
                self.to_be_written.append('enter')
                self.writing_queue.appendleft(deque(self.to_be_written))

                self.clear_to_be_written_buffer()
        
        # Clean the to_be_written buffer, we don't want to save deletes, since it is just removing elements from the buffer
        if key_event == 'backspace':
            self.to_be_written.pop()
            if len(self.to_be_written) > 0:
                self.to_be_written.pop()
        
    @keyboard_setup()
    def insert_text_state(self) -> None:
        self.state = State.INSERT_TEXT
    def handle_insert_text_keyboard(self):
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()
            return
        
        if len(self.buffer) >= 1:
            event = self.buffer[-1]
            self.insert_event_to_be_written(event)

    @keyboard_setup()
    def switch_user_state(self) -> None:        
        self.state = State.SWITCH_USER
    def handle_switch_user_keyboard(self) -> None:
        # Switch
        if self.is_typed(['s']):
            for k in ['enter', 's','w','i','t','c','h','enter']:
                self.insert_event_to_be_written(k)
            self.terminal_state()

        if len(self.buffer) >= 1:
            number = self.buffer[-1]
            # Get the number chosen
            if number.isdigit():
                value = int(number)-1
                players = self.config.get("PLAYERS")
                player = None
                
                if 0 <= value < len(players):
                    player = players[value]

                if player:
                    self.to_be_written.clear()

                    to_type = ['enter', 's','w','i','t','c','h','space']
                    to_type.extend(list(player))
                    to_type.append('enter')
                    for k in to_type:
                        self.insert_event_to_be_written(k)
                else:
                    self.set_event(f"No player number: {value}", EventType.FAIL)
                self.terminal_state()

        self.handle_control_c()

    @keyboard_setup()
    def switch_flash_state(self) -> None:        
        self.state = State.FLASH_RADAR
    @keyboard_setup()
    def switch_ping_state(self) -> None:        
        self.state = State.PING_RADAR
    def handle_radar_command(self, command: str) -> None:
        if len(self.buffer) >= 1:
            number = self.buffer[-1]
            if number.isdigit():
                value = int(number)-1
                radars = self.config.get("RADARS")
                radar = None
                
                if 0 <= value < len(radars):
                    radar = radars[value]

                if radar:
                    self.to_be_written.clear()

                    to_type = ['enter']
                    to_type.extend(list(command))
                    to_type.append('space')
                    to_type.extend(list(radar))
                    to_type.append('enter')
                    for k in to_type:
                        self.insert_event_to_be_written(k)
                else:
                    self.set_event(f"No radar number: {value}", EventType.FAIL)
                self.terminal_state()

        self.handle_control_c()
    
    def insert_view_monitor_text(self) -> None:
        self.to_be_written.clear()
        for k in ['enter','v','i','e','w','space','m','o','n','i','t','o','r','enter']:
            self.insert_event_to_be_written(k)

    @keyboard_setup()
    def transmit_text_state(self) -> None:
        self.to_be_written.clear()
        for k in ['enter','t','r','a','n','s','m','i','t','space']:
            self.insert_event_to_be_written(k)
        
        self.state = State.TRANSMIT_TEXT

    def handle_suffix_text_enter_keyboard(self) -> None:
        if self.is_typed(['ctrl', 'c']):
            self.terminal_state()
            return

        if len(self.buffer) >= 1:
            event = self.buffer[-1]
            self.insert_event_to_be_written(event)

            # Finished writing
            if event == 'enter':
                self.terminal_state()

    # Thread to handle writing the trap
    def start_automatic_trap_writing(self) -> None:
        '''Writes the traps automatically from the writing_queue'''
        self.is_auto_typing_traps = True
        self.logger.debug("Started automatic trap writing")

        trap_list = self.traps
        if self.want_all_traps:
            trap_list = self.all_traps

        for trap in trap_list:
            self.writing_queue.append(deque([trap[0], trap[1]]))

        # Get rid of what the user was typing
        self.press_key_and_wait('enter')
        while len(self.writing_queue) > 0:
            # Write is a list of keys to write
            write = self.writing_queue.popleft()

            for key in write:
                self.press_key_and_wait(key)

            self.press_key_and_wait('enter')
        time_since_start_of_trap_thread = time() - self.start_time
        time_left = self.config.get("TRAP_TIMER_DURATION") - time_since_start_of_trap_thread
        # If there is time to return the terminal back to normal
        if time_left > 0:
            # Try catch since the user could clear the self.to_be_written buffer at any time
            try:
                # Finish off user typed buffer that is not done from the terminal
                for i in range(len(self.to_be_written)):
                    self.press_key_and_wait(self.to_be_written[i])
            except:
                sleep(0.01)

        self.logger.debug("Ended automatic trap writing")
        self.is_auto_typing_traps = False
    

    def clear_all_buffers(self) -> None:
        self.clear_to_be_written_buffer()
        self.buffer.clear()
        self.writing_queue.clear()

    def automatic_trap_writing_manager(self) -> None:
        '''The thread that manages the automatic trap writer
        
        Will call the trap writer every TRAP_TIMER_DURATION.
        If automatic trap writing takes a long time, it is compensated in the timer'''

        self.is_running_manager = True
        ideal_timer = self.config.get("TRAP_TIMER_DURATION")

        initial_call = True
        while self.run_auto_trap_thread:
            if self.state is not State.GAMEPLAY:
                self.start_time = time()

                # Need to wait at the first for the user to type 'view monitor'
                if initial_call:
                    sleep(1)
                    initial_call = False

                if (len(self.traps) > 0 or self.want_all_traps):
                    thread = threading.Thread(target=self.start_automatic_trap_writing)
                    thread.start()
                    # wait for the thread to finish
                    thread.join()

                elapsed_time = time() - self.start_time
                remaining_time = max(0, ideal_timer - elapsed_time)

                # If there is still time left, wait
                while remaining_time > 0 and self.state is not State.GAMEPLAY:
                    sleep_time = min(0.1, remaining_time)
                    sleep(sleep_time)
                    remaining_time -= sleep_time

            else:
                sleep(0.1)
        self.is_running_manager = False