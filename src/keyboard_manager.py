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
            type, arg2 = "none", None
            with self.lock:
                if len(self.queue) > 0:
                    type, arg2 = self.queue.popleft()
            match type:
                case "key":
                    if arg2 is not None:
                        keyboard.press(arg2)
                        sleep(self.config.get("USER_INPUT_DELAY"))
                        keyboard.release(arg2)
                    else:
                        sleep(0.01)
                case "callback":
                    arg2()
                case "none":
                    sleep(0.01)
                    

    def press_key(self, key):
        with self.lock:
            self.queue.append(("key", key))
    
    def stop(self):
        self.running = False 
        # Wait for the thread to finish
        self.thread.join()

    def wait(self):
        # Wait for a keyboard event
        keyboard.wait()
    
    def callback(self, callback):
        with self.lock:
            self.queue.append(("callback", callback))

# Decorator for keyboard setup
def keyboard_setup(func):
    def decorator(self):
        keyboard.unhook_all()
        func(self)
    return decorator
