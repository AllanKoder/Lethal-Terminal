from time import sleep
import keyboard
import threading
from collections import deque

from .config import ConfigSingleton

class KeyboardManager:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()
        self.running = True  # keep running or end?

        self.thread = threading.Thread(target=self.process_keys)
        self.thread.start()

        self.config = ConfigSingleton()
    def process_keys(self):
        while self.running:
            with self.lock:
                if len(self.queue) > 0:
                    key = self.queue.popleft()
                else:
                    key = None

            if key is not None:
                keyboard.press(key)
                sleep(self.config.get("USER_INPUT_DELAY"))
                keyboard.release(key)
            else:
                sleep(0.01)  # Sleep briefly to avoid overloading

    def press_key(self, key):
        with self.lock:
            self.queue.append(key)

    def stop(self):
        self.running = False 
        # Wait for the thread to finish
        self.thread.join()

    def wait(self):
        # Wait for a keyboard event
        keyboard.wait()

    # TODO: def write(self):
        

# Decorator for keyboard setup
def keyboard_setup(func):
    def decorator(self):
        keyboard.unhook_all()
        func(self)
        self.terminal_ui.render()
    return decorator
