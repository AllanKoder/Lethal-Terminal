from Lethal.terminal_state_manager import TerminalStateManager
from Lethal.keyboard_manager import KeyboardManager

if __name__ == "__main__":
    keyboard_manager = KeyboardManager()
    manager = TerminalStateManager(keyboard_manager)
    keyboard_manager.wait()  # Keep the program running
