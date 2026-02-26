# Blaude Minimal

Background Claude worker manager for OpenClaw.

## Features

- ✅ **Spawn workers** in background with budget controls
- ✅ **Track workers** with persistent storage  
- ✅ **Auto-notify** configurable agents when complete
- ✅ **Kill workers** with proper cleanup
- ✅ **Monitor progress** via logs

## Usage

```bash
# Spawn a worker
python3 blaude-minimal.py spawn my-task "Fix all the tests" --model haiku --budget 2.0 --notify dev-general

# List running workers  
python3 blaude-minimal.py list

# Kill a worker
python3 blaude-minimal.py kill my-task

# Clean up completed workers
python3 blaude-minimal.py cleanup
```

## How It Works

1. **Spawns** Claude workers using `nohup` + session IDs
2. **Tracks** workers in `/tmp/blaude-workers.json`
3. **Monitors** completion via background threads
4. **Notifies** target agents via `openclaw agent message`
5. **Logs** worker output to `/tmp/blaude-logs/`

## Integration Example

```python
# From your agent code
import subprocess

# Spawn a worker that reports back to you
subprocess.run([
    "python3", "/path/to/blaude-minimal.py", "spawn",
    "test-fixer", "Fix failing tests in rent-manager",
    "--model", "haiku", "--budget", "3.0", 
    "--notify", "dev-general"
])
```

## Files

- `blaude-minimal.py` - Main worker manager
- `test-blaude.sh` - Test script
- `/tmp/blaude-workers.json` - Worker persistence
- `/tmp/blaude-logs/` - Worker output logs

## Next Steps

For the full version, add:
- Textual TUI dashboard
- Worker templates
- Session resumption
- Cost tracking dashboard
- Steering capabilities