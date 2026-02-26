#!/usr/bin/env python3
"""
Runner - Claude Code worker management and session tracking
"""
import subprocess
import json
import uuid
import time
import os
import signal
import threading
from pathlib import Path
from typing import Dict, Optional, List

class Runner:
    """Manages Claude Code worker processes with session tracking"""
    
    def __init__(self, workers_file="/tmp/blaude-workers.json", logs_dir="/tmp/blaude-logs"):
        self.workers_file = Path(workers_file)
        self.logs_dir = Path(logs_dir)
        self.workers = self.load_workers()
        self.logs_dir.mkdir(exist_ok=True)
        
        # Start periodic status checker
        self._start_status_monitor()
    
    def load_workers(self) -> Dict:
        """Load workers from persistent storage"""
        try:
            if self.workers_file.exists():
                with open(self.workers_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load workers file: {e}")
        return {}
    
    def save_workers(self):
        """Save workers to persistent storage"""
        try:
            with open(self.workers_file, 'w') as f:
                json.dump(self.workers, f, indent=2)
        except Exception as e:
            print(f"Error saving workers: {e}")
    
    def set_env_wizard(self):
        """Prompts user to set claude code api key and sets env if not found"""
        # Check if Claude Code is authenticated
        try:
            result = subprocess.run(["claude", "auth", "status"], 
                                  capture_output=True, text=True, timeout=10)
            if "authenticated" in result.stdout.lower():
                print("✅ Claude Code is authenticated")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        print("❌ Claude Code not authenticated. Please run:")
        print("   claude auth")
        print("   or set ANTHROPIC_API_KEY environment variable")
        return False
    
    def get_config(self, name: str, command: str, env: dict = None) -> Dict:
        """Generate configuration for a worker"""
        session_id = str(uuid.uuid4())
        log_file = self.logs_dir / f"{name}.log"
        
        if env is None:
            env = {}
        
        return {
            "name": name,
            "session_id": session_id,
            "command": command,
            "log_file": str(log_file),
            "env": env,
            "created_at": time.time()
        }
    
    def run(self, name: str, prompt: str, model="haiku", budget=2.0, 
           notify_target="main", background=True) -> bool:
        """Run claude code in background with monitoring"""
        
        if name in self.workers:
            print(f"❌ Worker '{name}' already exists")
            return False
        
        if not self.set_env_wizard():
            return False
        
        config = self.get_config(name, prompt)
        session_id = config["session_id"]
        log_file = config["log_file"]
        
        # Build claude command
        cmd = [
            "claude", "--print",
            "--session-id", session_id,
            "--model", model,
            "--max-budget-usd", str(budget),
            "--debug-file", str(log_file),
            "--output-format", "json",
            prompt
        ]
        
        try:
            if background:
                # Use nohup for true background execution
                cmd = ["nohup"] + cmd
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid,  # Create new process group
                    cwd=str(Path.cwd())
                )
                pid = proc.pid
            else:
                # Run in foreground for testing
                result = subprocess.run(cmd, capture_output=True, text=True)
                pid = None
                if result.returncode != 0:
                    print(f"❌ Command failed: {result.stderr}")
                    return False
            
            # Store worker info
            self.workers[name] = {
                "pid": pid,
                "session_id": session_id,
                "model": model,
                "budget": budget,
                "notify_target": notify_target,
                "prompt": prompt,
                "start_time": time.time(),
                "status": "running" if background else "completed",
                "log_file": str(log_file),
                "background": background
            }
            
            self.save_workers()
            
            if background:
                print(f"✅ Started worker '{name}' (PID: {pid})")
            else:
                print(f"✅ Completed worker '{name}' (foreground)")
                self._handle_completion(name)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start worker '{name}': {e}")
            return False
    
    def kill_worker(self, name: str) -> bool:
        """Kill a running worker"""
        if name not in self.workers:
            print(f"❌ Worker '{name}' not found")
            return False
        
        worker = self.workers[name]
        if worker["status"] != "running" or not worker.get("pid"):
            print(f"❌ Worker '{name}' is not running")
            return False
        
        try:
            os.killpg(worker["pid"], signal.SIGTERM)
            worker["status"] = "killed"
            worker["end_time"] = time.time()
            self.save_workers()
            print(f"✅ Killed worker '{name}'")
            return True
        except (OSError, ProcessLookupError):
            worker["status"] = "dead"
            worker["end_time"] = time.time()
            self.save_workers()
            print(f"⚠️ Worker '{name}' was already dead")
            return True
    
    def list_workers(self) -> List[Dict]:
        """Get list of all workers with status"""
        workers_list = []
        for name, worker in self.workers.items():
            age = int(time.time() - worker["start_time"])
            workers_list.append({
                "name": name,
                "status": worker["status"],
                "model": worker["model"],
                "age_seconds": age,
                "pid": worker.get("pid"),
                "notify_target": worker["notify_target"]
            })
        return workers_list
    
    def cleanup_completed(self) -> int:
        """Remove completed workers from tracking"""
        to_remove = [name for name, worker in self.workers.items() 
                    if worker["status"] in ["completed", "killed", "dead"]]
        
        for name in to_remove:
            del self.workers[name]
        
        if to_remove:
            self.save_workers()
            print(f"🗑️ Cleaned up {len(to_remove)} workers")
        
        return len(to_remove)
    
    def _start_status_monitor(self):
        """Start background thread to monitor worker status"""
        def monitor_loop():
            while True:
                self._check_worker_statuses()
                time.sleep(5)  # Check every 5 seconds
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
    
    def _check_worker_statuses(self):
        """Check and update status of running workers"""
        updated = False
        for name, worker in list(self.workers.items()):
            if worker["status"] == "running" and worker.get("pid"):
                try:
                    os.kill(worker["pid"], 0)  # Check if process exists
                except (OSError, ProcessLookupError):
                    # Process is dead - mark as completed
                    worker["status"] = "completed"
                    worker["end_time"] = time.time()
                    updated = True
                    self._handle_completion(name)
        
        if updated:
            self.save_workers()
    
    def _handle_completion(self, name: str):
        """Handle worker completion and notification"""
        from notifier import Notifier
        
        worker = self.workers.get(name)
        if not worker:
            return
        
        duration = int(worker.get("end_time", time.time()) - worker["start_time"])
        
        # Get summary from log file
        summary = self._extract_summary(worker["log_file"])
        
        # Send notification
        notifier = Notifier()
        notifier.notify_completion(name, summary, duration, worker["notify_target"])
    
    def _extract_summary(self, log_file: str) -> str:
        """Extract meaningful summary from worker log file"""
        try:
            log_path = Path(log_file)
            if not log_path.exists():
                return "No output captured"
            
            with open(log_path, 'r') as f:
                content = f.read()
            
            # Try to find JSON result in log
            lines = content.split('\n')
            for line in reversed(lines):
                if '"result":' in line:
                    try:
                        data = json.loads(line)
                        if 'result' in data:
                            result = data['result']
                            # Truncate long results
                            return result[:300] + "..." if len(result) > 300 else result
                    except json.JSONDecodeError:
                        continue
            
            # Fallback to last few non-debug lines
            meaningful_lines = [line for line in lines[-20:] 
                              if line.strip() and not line.startswith("2026-")]
            return '\n'.join(meaningful_lines[-5:])[:200]
            
        except Exception as e:
            return f"Error reading output: {e}"