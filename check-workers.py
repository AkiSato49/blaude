#!/usr/bin/env python3
"""
Quick script for me to check if any workers completed
"""
import json
import time
from pathlib import Path

def check_recent_completions():
    """Check for recently completed workers"""
    workers_file = Path("/tmp/blaude-workers.json")
    if not workers_file.exists():
        return []
    
    try:
        with open(workers_file, 'r') as f:
            workers = json.load(f)
    except:
        return []
    
    recent_completions = []
    current_time = time.time()
    
    for name, worker in workers.items():
        if worker["status"] == "completed":
            end_time = worker.get("end_time", worker.get("start_time", 0))
            age_since_completion = current_time - end_time
            
            # Recently completed (within last 5 minutes)
            if age_since_completion < 300:
                duration = int(end_time - worker["start_time"])
                recent_completions.append({
                    "name": name,
                    "duration": duration,
                    "age_since_completion": int(age_since_completion),
                    "model": worker.get("model", "unknown")
                })
    
    return recent_completions

if __name__ == "__main__":
    completions = check_recent_completions()
    if completions:
        print("Recent completions:")
        for comp in completions:
            print(f"  {comp['name']}: {comp['duration']}s ({comp['model']}) - completed {comp['age_since_completion']}s ago")
    else:
        print("No recent completions")