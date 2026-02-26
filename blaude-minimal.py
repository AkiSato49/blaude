#!/usr/bin/env python3
"""
Blaude Minimal - Background Claude worker manager
Usage: python blaude-minimal.py <command> [args...]
"""
import subprocess
import json
import uuid
import time
import os
import signal
import sys
from pathlib import Path
from typing import Dict, Optional

WORKERS_FILE = "/tmp/blaude-workers.json"
LOGS_DIR = "/tmp/blaude-logs"

class WorkerManager:
    def __init__(self):
        self.workers = self.load_workers()
        Path(LOGS_DIR).mkdir(exist_ok=True)
    
    def load_workers(self) -> Dict:
        """Load workers from persistent storage"""
        try:
            if Path(WORKERS_FILE).exists():
                with open(WORKERS_FILE, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_workers(self):
        """Save workers to persistent storage"""
        with open(WORKERS_FILE, 'w') as f:
            json.dump(self.workers, f, indent=2)
    
    def spawn_worker(self, name: str, prompt: str, model="haiku", 
                    budget=2.0, notify_target="dev-general"):
        """Spawn a new Claude worker in background"""
        if name in self.workers:
            print(f"❌ Worker '{name}' already exists")
            return False
        
        session_id = str(uuid.uuid4())
        log_file = f"{LOGS_DIR}/{name}.log"
        
        # Build claude command
        cmd = [
            "nohup", "claude", "--print",
            "--session-id", session_id,
            "--model", model,
            "--max-budget-usd", str(budget),
            "--debug-file", log_file,
            "--output-format", "json",
            prompt
        ]
        
        try:
            # Start process in background
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # Create new process group
            )
            
            self.workers[name] = {
                "pid": proc.pid,
                "session_id": session_id,
                "model": model,
                "budget": budget,
                "notify_target": notify_target,
                "start_time": time.time(),
                "status": "running",
                "log_file": log_file
            }
            
            self.save_workers()
            print(f"✅ Spawned worker '{name}' (PID: {proc.pid})")
            
            # Start monitoring thread for this worker
            import threading
            threading.Thread(
                target=self._monitor_worker, 
                args=(name,), 
                daemon=True
            ).start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to spawn worker '{name}': {e}")
            return False
    
    def _monitor_worker(self, name: str):
        """Monitor a worker and notify when complete"""
        worker = self.workers.get(name)
        if not worker:
            return
        
        pid = worker["pid"]
        try:
            # Wait for process to complete
            os.waitpid(pid, 0)
            
            # Process completed - check results
            self._handle_completion(name)
            
        except (OSError, ProcessLookupError):
            # Process doesn't exist or already reaped
            self._handle_completion(name)
    
    def _handle_completion(self, name: str):
        """Handle worker completion and notification"""
        worker = self.workers.get(name)
        if not worker:
            return
        
        worker["status"] = "completed"
        worker["end_time"] = time.time()
        
        # Try to read output/results
        try:
            if Path(worker["log_file"]).exists():
                with open(worker["log_file"], 'r') as f:
                    log_content = f.read()
                    # Extract summary from last few lines
                    summary = log_content.split('\n')[-10:]  # Last 10 lines
                    summary = '\n'.join([line for line in summary if line.strip()])[:200]
            else:
                summary = "No output captured"
        except:
            summary = "Error reading output"
        
        # Notify completion
        self._notify_completion(name, summary)
        self.save_workers()
    
    def _notify_completion(self, name: str, summary: str):
        """Send completion notification via openclaw"""
        worker = self.workers[name]
        target = worker["notify_target"]
        
        duration = int(worker.get("end_time", time.time()) - worker["start_time"])
        message = f"🎯 Worker **{name}** completed ({duration}s)\n```\n{summary}\n```"
        
        try:
            subprocess.run([
                "openclaw", "agent", "message", target, message
            ], check=True)
            print(f"📤 Notified {target} about '{name}' completion")
        except Exception as e:
            print(f"❌ Failed to notify {target}: {e}")
    
    def kill_worker(self, name: str):
        """Kill a running worker"""
        if name not in self.workers:
            print(f"❌ Worker '{name}' not found")
            return False
        
        worker = self.workers[name]
        if worker["status"] != "running":
            print(f"❌ Worker '{name}' is not running (status: {worker['status']})")
            return False
        
        try:
            # Kill entire process group to ensure cleanup
            os.killpg(worker["pid"], signal.SIGTERM)
            worker["status"] = "killed"
            self.save_workers()
            print(f"✅ Killed worker '{name}'")
            return True
        except (OSError, ProcessLookupError):
            print(f"⚠️ Worker '{name}' was already dead")
            worker["status"] = "dead"
            self.save_workers()
            return True
    
    def list_workers(self):
        """List all workers and their status"""
        if not self.workers:
            print("No workers found")
            return
        
        print(f"{'Name':<15} {'Status':<10} {'Model':<10} {'Age':<8} {'PID':<8}")
        print("─" * 60)
        
        for name, worker in self.workers.items():
            age = int(time.time() - worker["start_time"])
            age_str = f"{age}s" if age < 60 else f"{age//60}m"
            
            print(f"{name:<15} {worker['status']:<10} {worker['model']:<10} {age_str:<8} {worker['pid']:<8}")
    
    def cleanup_dead(self):
        """Remove completed/dead workers from tracking"""
        to_remove = []
        for name, worker in self.workers.items():
            if worker["status"] in ["completed", "killed", "dead"]:
                to_remove.append(name)
        
        for name in to_remove:
            del self.workers[name]
            print(f"🗑️ Cleaned up worker '{name}'")
        
        self.save_workers()

def main():
    if len(sys.argv) < 2:
        print("Usage: python blaude-minimal.py <spawn|kill|list|cleanup> [args...]")
        print("\nCommands:")
        print("  spawn <name> <prompt> [--model haiku] [--budget 2.0] [--notify dev-general]")
        print("  kill <name>")  
        print("  list")
        print("  cleanup")
        return
    
    manager = WorkerManager()
    command = sys.argv[1]
    
    if command == "spawn":
        if len(sys.argv) < 4:
            print("Usage: spawn <name> <prompt> [--model MODEL] [--budget BUDGET] [--notify TARGET]")
            return
        
        name = sys.argv[2]
        prompt = sys.argv[3]
        model = "haiku"
        budget = 2.0
        notify_target = "dev-general"
        
        # Parse optional flags
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--model" and i+1 < len(sys.argv):
                model = sys.argv[i+1]
                i += 2
            elif sys.argv[i] == "--budget" and i+1 < len(sys.argv):
                budget = float(sys.argv[i+1])
                i += 2
            elif sys.argv[i] == "--notify" and i+1 < len(sys.argv):
                notify_target = sys.argv[i+1]
                i += 2
            else:
                i += 1
        
        manager.spawn_worker(name, prompt, model, budget, notify_target)
    
    elif command == "kill":
        if len(sys.argv) < 3:
            print("Usage: kill <name>")
            return
        manager.kill_worker(sys.argv[2])
    
    elif command == "list":
        manager.list_workers()
    
    elif command == "cleanup":
        manager.cleanup_dead()
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()