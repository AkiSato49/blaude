#!/usr/bin/env python3
"""
Blaude Worker TUI - Lazygit-style dashboard for monitoring Claude workers
"""
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from textual.app import App, ComposeResult
from textual.containers import Container, Grid, Horizontal, Vertical
from textual.widgets import Static, Label, Button, TextArea
from textual.reactive import reactive, var
from textual.timer import Timer
from rich.text import Text
from rich.panel import Panel
from rich.console import Console
from rich.markup import escape

# Import our blaude modules
import sys
sys.path.insert(0, str(Path(__file__).parent))
from runner import Runner
from notifier import Notifier

class WorkerBox(Static):
    """Individual worker monitoring box"""
    
    def __init__(self, worker_id: int, **kwargs):
        self.worker_id = worker_id
        self.worker_data = None
        self.is_selected = False
        super().__init__(**kwargs)
        self.can_focus = True
    
    def compose(self) -> ComposeResult:
        """Create the worker box layout"""
        yield Label("", id=f"worker-{self.worker_id}-header")
        yield Static("", id=f"worker-{self.worker_id}-content", classes="worker-content")
        yield Label("", id=f"worker-{self.worker_id}-controls")
    
    def update_worker(self, worker_data: Optional[Dict] = None):
        """Update worker box with current data"""
        self.worker_data = worker_data
        
        # Update header
        header_widget = self.query_one(f"#worker-{self.worker_id}-header")
        content_widget = self.query_one(f"#worker-{self.worker_id}-content")
        controls_widget = self.query_one(f"#worker-{self.worker_id}-controls")
        
        if worker_data:
            # Header: name, status, model, duration, cost
            name = worker_data["name"]
            status = worker_data["status"]
            model = worker_data.get("model", "unknown")
            age = int(time.time() - worker_data.get("start_time", time.time()))
            budget = worker_data.get("budget", 0)
            
            # Status icon
            status_icons = {
                "running": "🟢",
                "completed": "✅", 
                "killed": "🔴",
                "dead": "💀",
                "failed": "❌"
            }
            icon = status_icons.get(status, "⚪")
            
            # Duration formatting
            if age < 60:
                duration = f"{age}s"
            elif age < 3600:
                duration = f"{age//60}m {age%60}s"
            else:
                duration = f"{age//3600}h {(age%3600)//60}m"
            
            # Header text
            header_text = f"{icon} {name} | {model} | ${budget:.2f} | {duration}"
            header_widget.update(header_text)
            
            # Content: reasoning/output from logs
            log_content = self.get_worker_reasoning(worker_data)
            content_widget.update(log_content)
            
            # Controls
            if status == "running":
                controls_widget.update("[k]Kill [s]Steer [l]Logs [p]Pause")
            elif status == "completed":
                controls_widget.update("[v]View Result [r]Restart [x]Remove")
            else:
                controls_widget.update("[r]Restart [x]Remove [l]Logs")
                
        else:
            # Empty slot
            header_widget.update("[ Empty Slot ]")
            content_widget.update(self.get_empty_slot_content())
            controls_widget.update("[n]New Worker [t]Templates")
    
    def get_worker_reasoning(self, worker_data: Dict) -> str:
        """Extract reasoning/output from worker log file"""
        try:
            log_file = worker_data.get("log_file", "")
            if not log_file or not Path(log_file).exists():
                return "No log file available"
            
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Extract meaningful lines (skip debug timestamps)
            lines = content.split('\n')
            meaningful_lines = []
            
            for line in lines[-30:]:  # Last 30 lines
                if line.strip() and not line.startswith("2026-"):
                    # Try to extract reasoning from JSON results
                    if '"result":' in line:
                        try:
                            import json as json_module
                            data = json_module.loads(line)
                            if 'result' in data:
                                meaningful_lines.extend(data['result'].split('\n')[:5])
                        except:
                            continue
                    else:
                        meaningful_lines.append(line.strip())
            
            # Take last 8 lines for the box
            display_lines = meaningful_lines[-8:]
            if not display_lines:
                return "Worker starting..."
            
            return '\n'.join(display_lines)
            
        except Exception as e:
            return f"Error reading log: {e}"
    
    def get_empty_slot_content(self) -> str:
        """Content for empty worker slots"""
        return """[n] New Worker

[t] Quick Templates:
  • Fix Tests  
  • Update Docs
  • Deploy Staging
  • Code Review
  • Debug Issue"""
    
    def update_selection(self, selected: bool):
        """Update visual selection state"""
        self.is_selected = selected
        if selected:
            self.add_class("worker-selected")
        else:
            self.remove_class("worker-selected")

class BlaudeTUI(App):
    """Main Blaude TUI Application"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 4 2;
        grid-columns: 1fr 1fr 1fr 1fr;
        grid-rows: 1fr 1fr;
    }
    
    WorkerBox {
        border: round;
        margin: 1;
        padding: 1;
        height: 100%;
    }
    
    .worker-selected {
        border: thick blue;
    }
    
    .worker-content {
        height: 10;
        overflow-y: auto;
    }
    
    Label {
        text-style: bold;
    }
    """
    
    TITLE = "Blaude Worker Monitor"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"), 
        ("c", "cleanup", "Cleanup"),
        ("n", "new_worker", "New Worker"),
        ("k", "kill_worker", "Kill Worker"),
        ("t", "templates", "Templates"),
    ]
    
    selected_worker = var(0)  # Currently selected worker (0-7)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.runner = Runner()
        self.worker_boxes = []
    
    def compose(self) -> ComposeResult:
        """Create the main TUI layout"""
        # Create 8 worker boxes in a 4x2 grid
        for i in range(8):
            yield WorkerBox(i, id=f"worker-box-{i}")
    
    def on_mount(self) -> None:
        """Initialize the app"""
        # Store references to worker boxes
        self.worker_boxes = [
            self.query_one(f"#worker-box-{i}") for i in range(8)
        ]
        
        # Set initial selection
        self.update_selection()
        
        # Start auto-refresh timer
        self.set_interval(2, self.refresh_workers)
        
        # Initial load
        self.refresh_workers()
    
    def refresh_workers(self) -> None:
        """Refresh worker data and update display"""
        try:
            # Get current workers
            workers_list = self.runner.list_workers()
            
            # Update each box
            for i in range(8):
                if i < len(workers_list):
                    worker_data = workers_list[i]
                    self.worker_boxes[i].update_worker(worker_data)
                else:
                    self.worker_boxes[i].update_worker(None)
                    
        except Exception as e:
            self.notify(f"Error refreshing: {e}", severity="error")
    
    def update_selection(self) -> None:
        """Update visual selection highlight"""
        for i, box in enumerate(self.worker_boxes):
            box.update_selection(i == self.selected_worker)
    
    def watch_selected_worker(self, old_value: int, new_value: int) -> None:
        """Handle selection changes"""
        self.update_selection()
    
    def action_refresh(self) -> None:
        """Manual refresh"""
        self.refresh_workers()
        self.notify("Refreshed worker status")
    
    def action_cleanup(self) -> None:
        """Cleanup completed workers"""
        try:
            count = self.runner.cleanup_completed()
            self.notify(f"Cleaned up {count} workers")
            self.refresh_workers()
        except Exception as e:
            self.notify(f"Cleanup error: {e}", severity="error")
    
    def action_new_worker(self) -> None:
        """Spawn new worker (placeholder)"""
        self.notify("New worker dialog - TODO")
    
    def action_kill_worker(self) -> None:
        """Kill selected worker"""
        workers_list = self.runner.list_workers()
        if self.selected_worker < len(workers_list):
            worker = workers_list[self.selected_worker]
            try:
                success = self.runner.kill_worker(worker["name"])
                if success:
                    self.notify(f"Killed worker: {worker['name']}")
                    self.refresh_workers()
            except Exception as e:
                self.notify(f"Kill error: {e}", severity="error")
    
    def action_templates(self) -> None:
        """Show worker templates"""
        self.notify("Worker templates - TODO")
    
    def on_key(self, event) -> None:
        """Handle navigation keys"""
        if event.key == "h" and self.selected_worker > 0:
            self.selected_worker = (self.selected_worker - 1) % 8
        elif event.key == "l" and self.selected_worker < 7:
            self.selected_worker = (self.selected_worker + 1) % 8
        elif event.key == "j" and self.selected_worker < 4:
            self.selected_worker = self.selected_worker + 4
        elif event.key == "k" and self.selected_worker >= 4:
            self.selected_worker = self.selected_worker - 4

def main():
    """Launch the Blaude TUI"""
    app = BlaudeTUI()
    app.run()

if __name__ == "__main__":
    main()