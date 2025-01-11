from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.columns import Columns
from .config import ConfigSingleton

class TerminalUI:
    def __init__(self, state_manager):
        self.console = Console()
        self.state_manager = state_manager
        self.config = ConfigSingleton()

        # Mock data for players and radars
        self.players = self.config.get("PLAYERS")
        self.radars = self.config.get("RADARS")

    def render(self):
        """Initial render of the terminal UI."""
        self.console.clear()
        title = Panel("[bold red]LETHAL[/bold red] [green]TERMINAL[/green]", border_style="red")
        self.console.print(title)
        self.display_content()

    def rerender(self):
        """Update the terminal UI without clearing everything."""
        self.console.clear()
        self.display_content()

    def display_content(self):
        """Display all content including tables and state."""
        # State display
        state_text = Text(f"\nState: {self.state_manager.state.name}", style="bold yellow")
        self.console.print(state_text)

        # Traps box display logic
        traps_display = "ALL TRAPS" if self.state_manager.want_all_traps else ' '.join(self.state_manager.traps)
        traps_panel = Panel(traps_display, title="Traps", border_style="red")
        self.console.print(traps_panel)

        # Create tables for players and radars
        player_table = self.create_player_table()
        radar_table = self.create_radar_table()

        # Use Columns to display tables side by side
        columns = Columns([player_table, radar_table], equal=True)
        self.console.print(columns)

        # Print the event
        event = "test event, oh no!"
        event_text = Text(event, style="bold red")
        self.console.print(event_text)

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
