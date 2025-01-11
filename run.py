from src.terminal_state_manager import TerminalStateManager
from src.keyboard_manager import KeyboardManager
from src.terminal_ui import TerminalUI
import tkinter as tk
from tkinter import ttk
import sv_ttk

from src.terminal_ui import TerminalUI

def main():
    keyboard_manager = KeyboardManager()
    root = tk.Tk()
    root.title("Lethal TERMINAL")

    # Initialize TerminalUI and TerminalStateManager separately
    state_manager = TerminalStateManager(keyboard_manager)
    terminal_ui = TerminalUI(state_manager, root)

    # Register the refresh callback after both are created
    def refresh_ui_callback():
        terminal_ui.update_ui()

    # Pass the callback to the state manager
    state_manager.set_refresh_callback(refresh_ui_callback)

    def toggle_theme():
        if sv_ttk.get_theme() == "dark":
            print("Setting theme to light")
            sv_ttk.use_light_theme()
        elif sv_ttk.get_theme() == "light":
            print("Setting theme to dark")
            sv_ttk.use_dark_theme()

    button = ttk.Button(root, text="Toggle theme", command=toggle_theme)
    button.grid(row=3, column=0)  # Adjust position as needed

    try:
        sv_ttk.set_theme("dark")
        terminal_ui.run()
    finally:
        keyboard_manager.stop()

if __name__ == "__main__":
    main()
