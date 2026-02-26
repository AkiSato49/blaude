#!/usr/bin/env python3
"""
Quick script to manually check and fix worker completion status
"""
import json
import os
import time
from pathlib import Path

WORKERS_FILE = "/tmp/blaude-workers.json"

def check_and_fix_workers():
    if not Path(WORKERS_FILE).exists():
        print("No workers file found")
        return
    
    with open(WORKERS_FILE, 'r') as f:
        workers = json.load(f)
    
    updated = False
    for name, worker in workers.items():
        if worker["status"] == "running":
            pid = worker["pid"]
            try:
                # Check if process exists
                os.kill(pid, 0)  # Doesn't kill, just checks existence
                print(f"✅ {name}: still running (PID {pid})")
            except (OSError, ProcessLookupError):
                # Process is dead
                print(f"🎯 {name}: completed! Updating status...")
                worker["status"] = "completed"  
                worker["end_time"] = time.time()
                updated = True
                
                # Simulate completion notification
                duration = int(worker.get("end_time", time.time()) - worker["start_time"])
                print(f"   Duration: {duration}s")
                
                # Check if log file has results
                log_file = worker.get("log_file", f"/tmp/blaude-logs/{name}.log")
                if Path(log_file).exists():
                    print(f"   Log: {log_file}")
    
    if updated:
        with open(WORKERS_FILE, 'w') as f:
            json.dump(workers, f, indent=2)
        print("✅ Worker statuses updated")

if __name__ == "__main__":
    check_and_fix_workers()