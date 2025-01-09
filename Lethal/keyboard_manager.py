from time import sleep
import keyboard
import threading
from collections import deque

INPUT_DELAY = 0.02
class KeyboardManager:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.process_keys)
        self.thread.start()

    def process_keys(self):
        while True:
            with self.lock:
                if len(self.queue) > 0:
                    key = self.queue.popleft()
                else:
                    key = None

            if key is not None:
                keyboard.press(key)
                sleep(INPUT_DELAY)
                keyboard.release(key)
            else:
                sleep(0.01)  # Sleep briefly to stop overloading the system

    def press_key(self, key):
        with self.lock:
            self.queue.append(key)
    
    def wait(self):
        keyboard.wait()


# Decorator for keyboard setup
def keyboard_setup(func):
    def decorator(self):
        keyboard.unhook_all()
        func(self)
    return decorator
