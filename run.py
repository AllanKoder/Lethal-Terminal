from src.terminal_state_manager import TerminalStateManager
from src.keyboard_manager import KeyboardManager
import threading

if __name__ == "__main__":
    keyboard_manager = KeyboardManager()
    try:
        state_manager = TerminalStateManager(keyboard_manager)
        keyboard_manager.wait()  # Keep the program running
    finally:
        keyboard_manager.stop()