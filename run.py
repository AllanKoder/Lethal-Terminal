from Lethal.terminal_state_manager import TerminalStateManager
from Lethal.keyboard_manager import KeyboardManager
import threading

if __name__ == "__main__":
    keyboard_manager = KeyboardManager()
    try:
        state_manager = TerminalStateManager(keyboard_manager)
        threading.Thread(target=state_manager.automatic_trap_writing_manager).start()
        keyboard_manager.wait()  # Keep the program running
    finally:
        state_manager.stop()
        keyboard_manager.stop()