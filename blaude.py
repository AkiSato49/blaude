#!/usr/bin/env python3
"""
Blaude - Background Claude runner + monitoring with TUI
Integration of all modules, processes flags and prompts. TUI also accessible.
"""
import sys
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from runner import Runner
from notifier import Notifier

class Blaude:
    """Main Blaude application coordinator"""
    
    def __init__(self):
        self.runner = Runner()
        self.notifier = Notifier()
    
    def spawn(self, name: str, prompt: str, model="haiku", budget=2.0, 
              notify="main", background=True) -> bool:
        """Spawn a new Claude worker"""
        return self.runner.run(name, prompt, model, budget, notify, background)
    
    def kill(self, name: str) -> bool:
        """Kill a running worker"""
        return self.runner.kill_worker(name)
    
    def list(self) -> None:
        """List all workers with status"""
        workers = self.runner.list_workers()
        
        if not workers:
            print("No workers found")
            return
        
        # Print header
        print(f"{'Name':<15} {'Status':<10} {'Model':<10} {'Age':<8} {'Target':<12} {'PID':<8}")
        print("─" * 75)
        
        # Print workers
        for worker in workers:
            age = worker["age_seconds"]
            age_str = f"{age}s" if age < 60 else f"{age//60}m"
            pid_str = str(worker["pid"]) if worker["pid"] else "-"
            
            print(f"{worker['name']:<15} {worker['status']:<10} {worker['model']:<10} "
                  f"{age_str:<8} {worker['notify_target']:<12} {pid_str:<8}")
    
    def cleanup(self) -> None:
        """Clean up completed workers"""
        count = self.runner.cleanup_completed()
        if count == 0:
            print("No workers to clean up")
    
    def test_notify(self, target="dev-general") -> bool:
        """Send a test notification"""
        return self.notifier.test_notification(target)
    
    def status(self) -> None:
        """Show system status"""
        workers = self.runner.list_workers()
        
        running = len([w for w in workers if w["status"] == "running"])
        completed = len([w for w in workers if w["status"] == "completed"])
        total = len(workers)
        
        print(f"📊 Blaude Status:")
        print(f"   Running: {running}")
        print(f"   Completed: {completed}")
        print(f"   Total: {total}")
        print(f"   Workers file: {self.runner.workers_file}")
        print(f"   Logs dir: {self.runner.logs_dir}")


def main():
    """Main CLI entry point"""
    
    parser = argparse.ArgumentParser(
        description="Blaude - Background Claude runner with monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  blaude spawn test-task "Fix the failing tests" --model haiku --budget 2.0
  blaude spawn deploy "Deploy to staging" --notify ops-lob --budget 5.0
  blaude list
  blaude kill test-task  
  blaude cleanup
  blaude test-notify dev-general
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Spawn command
    spawn_parser = subparsers.add_parser("spawn", help="Spawn a new worker")
    spawn_parser.add_argument("name", help="Worker name")
    spawn_parser.add_argument("prompt", help="Prompt for Claude")
    spawn_parser.add_argument("--model", default="haiku", help="Claude model (default: haiku)")
    spawn_parser.add_argument("--budget", type=float, default=2.0, help="Budget in USD (default: 2.0)")
    spawn_parser.add_argument("--notify", default="main", help="Agent to notify (default: main)")
    spawn_parser.add_argument("--foreground", action="store_true", help="Run in foreground (for testing)")
    
    # Kill command
    kill_parser = subparsers.add_parser("kill", help="Kill a running worker")
    kill_parser.add_argument("name", help="Worker name to kill")
    
    # List command
    subparsers.add_parser("list", help="List all workers")
    
    # Cleanup command
    subparsers.add_parser("cleanup", help="Remove completed workers")
    
    # Status command
    subparsers.add_parser("status", help="Show system status")
    
    # Test notification command
    test_parser = subparsers.add_parser("test-notify", help="Send test notification")
    test_parser.add_argument("target", nargs="?", default="main", help="Target agent")
    
    # TUI command (placeholder)
    subparsers.add_parser("tui", help="Launch TUI dashboard (coming soon)")
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize Blaude
    app = Blaude()
    
    # Execute command
    if args.command == "spawn":
        background = not args.foreground
        success = app.spawn(args.name, args.prompt, args.model, args.budget, args.notify, background)
        sys.exit(0 if success else 1)
    
    elif args.command == "kill":
        success = app.kill(args.name)
        sys.exit(0 if success else 1)
    
    elif args.command == "list":
        app.list()
    
    elif args.command == "cleanup":
        app.cleanup()
    
    elif args.command == "status":
        app.status()
    
    elif args.command == "test-notify":
        success = app.test_notify(args.target)
        sys.exit(0 if success else 1)
    
    elif args.command == "tui":
        print("🚧 TUI dashboard coming soon! Use 'blaude list' for now.")
        sys.exit(1)
    
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()