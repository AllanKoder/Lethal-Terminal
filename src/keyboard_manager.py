from time import sleep
from typing import Callable, List
import keyboard
import threading
from collections import deque
from logging import Logger
from .config import ConfigSingleton

class KeyboardManager:
    def __init__(self, logger: Logger):
        self.queue = deque()
        self.lock = threading.Lock()
        self.running = True  # keep running or end?

        self.logger = logger

        self.thread = threading.Thread(target=self.process_keys)
        self.thread.start()
        self.config = ConfigSingleton()
    def process_keys(self):
        while self.running:
            key = None
            with self.lock:
                if len(self.queue) > 0:
                    key = self.queue.popleft()
                    self.logger.debug(f"Typing {key}")
            if key is not None:
                keyboard.press(key)
                sleep(self.config.get("KEYBOARD_INPUT_DELAY"))
                keyboard.release(key)
            else:
                sleep(0.01)
                    

    def press_key(self, key: str):
        with self.lock:
            self.queue.append(key)
    
    def stop(self):
        self.running = False 
        # Wait for the thread to finish
        self.thread.join()

    def wait(self):
        # Wait for a keyboard event
        keyboard.wait()

    def keys_to_string(self, key_array: List[str]):
        output = ""
        for k in key_array:
            if len(k) == 1:
                output += k
            else:
                if k == 'space':
                    output += " "
        return output

# Decorator for keyboard setup
# Reduce repeated code for keyboard setup
def keyboard_setup(suppress: bool = True) -> Callable:
    def decorator(func):
        def wrapper(self):
            self.listen_to_keyboard(suppress)
            self.buffer.clear()
            func(self)
            if self.refresh_callback:
                self.refresh_callback()
        return wrapper
    return decorator
