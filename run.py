from Lethal.terminal_state_manager import TerminalStateManager
from Lethal.keyboard_manager import KeyboardManager

if __name__ == "__main__":
    try:
        keyboard_manager = KeyboardManager()
        state_manager = TerminalStateManager(keyboard_manager)
        keyboard_manager.wait()  # Keep the program running
    finally:
        keyboard_manager.stop()