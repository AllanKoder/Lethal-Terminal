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
        
        # Update UI initially
        self.update_ui()

    def create_frames(self):
        """Create frames for layout."""
        # Frame for state, buffer, and traps at the top
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5)  # Reduced padding

        # State label with increased font size
        self.state_label = ttk.Label(self.info_frame, text="", font=("Helvetica", 14, "bold"))  # Increased font size
        self.state_label.grid(row=0, column=0, sticky="w")

        # Buffer label
        self.buffer_label = ttk.Label(self.info_frame, text="", font=("Helvetica", 10, "bold"))  # Smaller font size
        self.buffer_label.grid(row=1, column=0, sticky="w")

        # Traps frame with increased label size
        self.traps_frame = ttk.LabelFrame(self.info_frame, text="Traps")
        self.traps_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)  # Reduced padding

        # Create a label for traps display initially
        self.traps_label = ttk.Label(self.traps_frame, text="", font=("Helvetica", 12))  # Increased font size
        self.traps_label.pack(padx=10, pady=10)  # Adjusted padding for better spacing

        # Frame for player and radar tables at the bottom
        self.player_frame = ttk.LabelFrame(self.root, text="Players")
        self.player_frame.grid(row=1, column=0, padx=5, pady=5)  # Reduced padding

        self.radar_frame = ttk.LabelFrame(self.root, text="Radars")
        self.radar_frame.grid(row=1, column=1, padx=5, pady=5)  # Reduced padding

    def populate_player_table(self):
        """Populate player table."""
        player_tree = ttk.Treeview(self.player_frame, columns=("No.", "Name"), show='headings', height=4)  # Limit height to 4 rows
        player_tree.heading("No.", text="No.")
        player_tree.heading("Name", text="Name")

        # Set specific column widths
        player_tree.column("No.", width=30)
        player_tree.column("Name", width=100)

        for idx, player in enumerate(self.config.get("PLAYERS")):
            player_tree.insert("", "end", values=(idx + 1, player))

        player_tree.pack(fill=tk.BOTH)  # Removed expand=True to keep it compact

    def populate_radar_table(self):
        """Populate radar table."""
        radar_tree = ttk.Treeview(self.radar_frame, columns=("No.", "Radar"), show='headings', height=4)  # Limit height to 4 rows
        radar_tree.heading("No.", text="No.")
        radar_tree.heading("Radar", text="Radar")

        # Set specific column widths
        radar_tree.column("No.", width=30)
        radar_tree.column("Radar", width=100)

        for idx, radar in enumerate(self.config.get("RADARS")):
            radar_tree.insert("", "end", values=(idx + 1, radar))

        radar_tree.pack(fill=tk.BOTH)  # Removed expand=True to keep it compact

    def display_state(self):
        """Display current state."""
        actual_state = str(self.state_manager.state).split(".")[1]
        state_text = f"State: {actual_state}"
        self.state_label.config(text=state_text)

    def get_text_buffer(self):
        """Get formatted text buffer."""
        text_array = [w.replace("space", " ") for w in self.state_manager.to_be_written]
        return ''.join(text_array)

    def display_traps(self):
        """Display traps information."""
        
        # Determine the traps display text
        traps_display = "ALL TRAPS" if self.state_manager.want_all_traps else ' '.join(self.state_manager.traps)
        
        # Update the traps label instead of destroying it
        self.traps_label.config(text=traps_display)

    def run(self):
        """Run the tkinter main loop."""
        self.refresh_ui()
        self.root.mainloop()

    def refresh_ui(self):
        """Refresh the UI with the latest data."""
        
        # Update state and traps display
        self.display_state()
        
        # Update buffer label
        buffer_text = f"TEXT BUFFER: {self.get_text_buffer()}"
        self.buffer_label.config(text=buffer_text)
        
        # Refresh traps display
        self.display_traps()

    def update_ui(self):
        """Update the UI with the latest data at regular intervals."""
        
        # Refresh UI components
        self.refresh_ui()
        
        # Schedule the next update after 1000 milliseconds (1 second)
        self.root.after(1000, self.update_ui)
