#!/usr/bin/env python3
"""
TUI - Textual User Interface for monitoring Blaude workers
Using textual for TUI - must include boxes for each running agent (max 8) 
that display their reasoning/thinking and output live.
A small indicator on each box saying name/prompt time alive total token and cost (color coded).
"""

# TODO: Implement full TUI with Textual
# For now, this is a placeholder. The full implementation will include:
# 
# Features to implement:
# - 8 worker boxes showing live status
# - Real-time log tailing for each worker  
# - Token counters and cost tracking with color coding
# - Kill/restart buttons for each worker
# - Spawn new worker dialog
# - Auto-refresh every 2-5 seconds
# 
# Based on our proven subagent-dashboard code:

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll  
from textual.widgets import Button, DataTable, Footer, Header, Label, Static
from textual.reactive import reactive
from textual.timer import Timer

class BlaudeApp(App):
    """Main Blaude TUI Application"""
    
    CSS_PATH = "blaude.css"  # TODO: Create stylesheet
    TITLE = "Blaude - Background Claude Worker Monitor"
    
    def compose(self) -> ComposeResult:
        """Compose the main UI"""
        yield Header()
        
        with Horizontal():
            # Main worker table
            with Vertical(classes="main-panel"):
                yield Label("Active Workers", classes="panel-title")
                yield DataTable(id="workers-table")
                
                # Control buttons
                with Horizontal(classes="control-buttons"):
                    yield Button("Spawn Worker", id="spawn", variant="primary")
                    yield Button("Kill Selected", id="kill", variant="error")
                    yield Button("Refresh", id="refresh")
                    yield Button("Cleanup", id="cleanup")
            
            # Side panel for worker details
            with Vertical(classes="detail-panel"):
                yield Label("Worker Details", classes="panel-title")
                yield Static("Select a worker to view details", id="worker-details")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the app"""
        # Set up worker table
        table = self.query_one("#workers-table", DataTable)
        table.add_columns("Name", "Status", "Model", "Age", "Target", "PID")
        
        # Start auto-refresh
        self.set_interval(3, self.refresh_workers)
        
        # Initial load
        self.refresh_workers()
    
    def refresh_workers(self) -> None:
        """Refresh the workers table"""
        # TODO: Integrate with Runner class
        table = self.query_one("#workers-table", DataTable)
        table.clear()
        
        # Placeholder data
        table.add_row("test-worker", "running", "haiku", "2m", "dev-general", "12345")
        table.add_row("deploy", "completed", "sonnet", "5m", "ops-lob", "12346")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "spawn":
            # TODO: Show spawn dialog
            pass
        elif event.button.id == "kill":
            # TODO: Kill selected worker
            pass
        elif event.button.id == "refresh":
            self.refresh_workers()
        elif event.button.id == "cleanup":
            # TODO: Cleanup completed workers
            pass


def launch_tui():
    """Launch the Blaude TUI"""
    app = BlaudeApp()
    app.run()


if __name__ == "__main__":
    launch_tui()