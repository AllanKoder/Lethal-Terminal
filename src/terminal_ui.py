from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
import random

class TerminalUI:
    def __init__(self, state_manager):
        self.console = Console()
        self.state_manager = state_manager
        
        # Mock data for players and radars
        self.players = ["Player 1", "Player 2", "Player 3", "Player 4"]
        self.radars = [f"Radar {i + 1}" for i in range(random.randint(1, 10))]

    def get_text_buffer(self):
        text_array = [w.replace("space", " ") for w in self.state_manager.to_be_written]
        output = ""
        for text in text_array:
            if len(text) == 1:
                output += text
        return output

    def render(self):
        """Render the terminal UI."""
        self.console.clear()
        self.console.print("[bold red]Lethal[/bold red] [green]TERMINAL[/green]")

        # Create tables for players and radars
        player_table = self.create_player_table()
        radar_table = self.create_radar_table()

        # Use Columns to display tables side by side
        columns = Columns([player_table, radar_table], equal=True)
        self.console.print(columns)

        # State display
        state_text = Text(f"\nState: {self.state_manager.state.name}", style="bold yellow")
        self.console.print(state_text)

        # Buffer display
        buffer_label = Text(f"TEXT BUFFER: {self.get_text_buffer()}", style="bold")
        self.console.print(buffer_label)

        # Traps box display logic
        traps_display = "ALL TRAPS" if self.state_manager.want_all_traps else ' '.join(self.state_manager.traps)
        traps_panel = Panel(traps_display, title="Traps", border_style="magenta")
        self.console.print(traps_panel)

    def create_player_table(self):
        """Create a table for players."""
        player_table = Table(title="Players")
        player_table.add_column("No.", justify="center")
        player_table.add_column("Name", justify="left")

        for idx, player in enumerate(self.players):
            player_table.add_row(str(idx + 1), player)
        
        return player_table

    def create_radar_table(self):
        """Create a table for radars."""
        radar_table = Table(title="Radars")
        radar_table.add_column("No.", justify="center")
        radar_table.add_column("Radar", justify="left")

        for idx, radar in enumerate(self.radars):
            radar_table.add_row(str(idx + 1), radar)
        
        return radar_table

