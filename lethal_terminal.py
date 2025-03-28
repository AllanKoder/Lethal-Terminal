from src.terminal_state_manager import TerminalStateManager
from src.keyboard_manager import KeyboardManager
from src.terminal_ui import TerminalUI
from src.config import ConfigSingleton
import logging

def main():
    config = ConfigSingleton()

    # Configure logging
    file_handler = logging.FileHandler("lethal_terminal.log")
    logging.basicConfig(
        level=config.get("LOG_LEVEL"),
        format="%(message)s",
        handlers=[file_handler]
    )
    logger = logging.getLogger("Lethal Terminal")

    # Keyboard operations
    keyboard_manager = KeyboardManager(logger)

    try:
        # Initialize TerminalStateManager
        state_manager = TerminalStateManager(keyboard_manager, logger)
        
        # Initialize TerminalUI
        terminal_ui = TerminalUI(state_manager)

        # Register the refresh callback after both are created
        def refresh_ui_callback():
            terminal_ui.rerender()

        # Pass the callback to the state manager
        state_manager.set_refresh_callback(refresh_ui_callback)

        # Initial render of the UI
        terminal_ui.render()

        # Keep the program alive
        keyboard_manager.wait()
    finally:
        # Stop the threads
        keyboard_manager.stop()

if __name__ == "__main__":
    main()
