import tkinter as tk
from tkinter import ttk
from .config import ConfigSingleton

class TerminalUI:
    def __init__(self, state_manager, root):
        self.state_manager = state_manager
        self.root = root
        self.config = ConfigSingleton()

        # Create frames for layout
        self.create_frames()

        # Populate tables
        self.populate_player_table()
        self.populate_radar_table()
        
        self.update_ui()

    def create_frames(self):
        """Create frames for layout."""
        self.player_frame = ttk.LabelFrame(self.root, text="Players")
        self.player_frame.grid(row=0, column=0, padx=10, pady=10)

        self.radar_frame = ttk.LabelFrame(self.root, text="Radars")
        self.radar_frame.grid(row=0, column=1, padx=10, pady=10)

        self.state_label = ttk.Label(self.root, text="", font=("Helvetica", 12, "bold"), foreground="yellow")
        self.state_label.grid(row=1, columnspan=2)

        self.buffer_label = ttk.Label(self.root, text="", font=("Helvetica", 12, "bold"))
        self.buffer_label.grid(row=2, columnspan=2)

        self.traps_frame = ttk.LabelFrame(self.root, text="Traps")
        self.traps_frame.grid(row=3, columnspan=2, padx=10, pady=10)

    def populate_player_table(self):
        """Populate player table."""
        player_tree = ttk.Treeview(self.player_frame, columns=("No.", "Name"), show='headings')
        player_tree.heading("No.", text="No.")
        player_tree.heading("Name", text="Name")

        for idx, player in enumerate(self.config.get("PLAYERS")):
            player_tree.insert("", "end", values=(idx + 1, player))

        player_tree.pack(fill=tk.BOTH, expand=True)

    def populate_radar_table(self):
        """Populate radar table."""
        radar_tree = ttk.Treeview(self.radar_frame, columns=("No.", "Radar"), show='headings')
        radar_tree.heading("No.", text="No.")
        radar_tree.heading("Radar", text="Radar")

        for idx, radar in enumerate(self.config.get("RADARS")):
            radar_tree.insert("", "end", values=(idx + 1, radar))

        radar_tree.pack(fill=tk.BOTH, expand=True)

    def display_state(self):
        """Display current state."""
        state_text = f"State: {self.state_manager.state}"
        self.state_label.config(text=state_text)

    def get_text_buffer(self):
        """Get formatted text buffer."""
        text_array = [w.replace("space", " ") for w in self.state_manager.to_be_written]
        return ''.join(text_array)

    def display_traps(self):
        """Display traps information."""
        # Determine the traps display text
        traps_display = "ALL TRAPS" if self.state_manager.want_all_traps else ' '.join(self.state_manager.traps)
        
        # Clear previous traps display
        for widget in self.traps_frame.winfo_children():
            widget.destroy()
        
        # Create and pack the new traps label
        traps_label = ttk.Label(self.traps_frame, text=traps_display)
        traps_label.pack(padx=10, pady=10)


    def run(self):
        """Run the tkinter main loop."""
        self.refresh_ui()
        self.root.mainloop()

    def refresh_ui(self):
        # Update state and traps display
        self.display_state()
        
        # Update buffer label
        buffer_text = f"TEXT BUFFER: {self.get_text_buffer()}"
        self.buffer_label.config(text=buffer_text)
        
        # Refresh traps display
        self.display_traps()

    def update_ui(self):
        """Update the UI with the latest data."""
        self.refresh_ui()
        # Schedule the next update after 1000 milliseconds (1 second)
        self.root.after(1000, self.update_ui)
