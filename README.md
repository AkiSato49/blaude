# Blaude - Background Claude Worker Manager

Background Claude runner + monitoring with TUI for OpenClaw.

## 🚀 Quick Start

```bash
# Test the system
blaude test-notify main

# Spawn workers  
blaude spawn my-task "Your prompt here" --notify main
blaude spawn test-fixer "Fix failing tests" --model haiku --budget 2.0
blaude spawn deploy "Deploy to staging" --model sonnet --budget 5.0 --notify ops-lob

# Monitor workers
blaude list       # Show all workers
blaude status     # System overview
blaude cleanup    # Remove completed workers

# Control workers
blaude kill my-task
```

## ⚡ Installation

**Permanent location**: `/home/d-law/projects/blaude/`  
**Global command**: `blaude` (available from anywhere)

## 🎯 Features

- ✅ **Background execution** - Workers run while you do other things
- ✅ **Automatic notifications** - Get notified when workers complete
- ✅ **Multi-agent support** - Notify any OpenClaw agent (main, dev-general, rent-lob, etc.)
- ✅ **Budget controls** - Set spending limits per worker
- ✅ **Process monitoring** - Track status, age, tokens, costs
- ✅ **Persistent state** - Workers survive across restarts
- ✅ **Clean termination** - Proper cleanup and process management

## 🏗️ Architecture

```
blaude/
├── blaude.py         # Main CLI coordinator
├── runner.py         # Worker management + monitoring  
├── notifier.py       # OpenClaw integration
├── tui.py           # TUI dashboard (coming soon)
├── blaude-minimal.py # Single-file version
└── test-*.py        # Test suite
```

## 📋 Commands

### Spawn Workers
```bash
blaude spawn <name> "<prompt>" [options]

Options:
  --model MODEL     Claude model (haiku, sonnet, opus) [default: haiku]
  --budget AMOUNT   Budget in USD [default: 2.0] 
  --notify AGENT    Agent to notify when complete [default: main]
  --foreground      Run in foreground instead of background
```

### Monitor & Control
```bash
blaude list           # List all workers with status
blaude status         # System overview
blaude kill <name>    # Terminate a worker
blaude cleanup        # Remove completed workers  
blaude test-notify <agent>  # Test notifications
```

## 💡 Usage Examples

### Development Workflow
```bash
# Fix tests while you work on features
blaude spawn test-fixer "Fix all failing tests in rent-manager" --budget 3.0

# Update docs in background  
blaude spawn docs "Update README and API documentation" --model haiku

# Deploy when ready
blaude spawn deploy "Deploy rent-manager to staging environment" --model sonnet --budget 5.0
```

### Multi-Agent Coordination
```bash
# Notify different agents for different tasks
blaude spawn rent-analysis "Analyze rental market data" --notify rent-lob
blaude spawn server-deploy "Deploy to production" --notify ops-lob --model sonnet
blaude spawn docs-update "Update project docs" --notify dev-general
```

## 🔧 Technical Details

- **Process Management**: Uses nohup + process groups for clean background execution
- **Session Tracking**: Each worker gets a unique Claude session ID  
- **Monitoring**: Background threads monitor worker completion
- **Notifications**: Uses `openclaw agent --agent <target> -m <message>`
- **Storage**: Worker state in `/tmp/blaude-workers.json`
- **Logs**: Worker output in `/tmp/blaude-logs/`

## 📊 Status

**Current Version**: v0.2 - Full Architecture  
**Status**: ✅ Production Ready

**Completed**: Core worker management, notifications, CLI, monitoring  
**Next**: TUI dashboard, worker templates, cost tracking, session resumption

## 🎯 Maximum Uptime Strategy

```
Aki ↔ OpenClaw Agent (orchestrator) ↔ blaude ↔ [Claude Code workers]
     ↖                                        ↙
       Instant notifications when complete
```

You stay connected to your OpenClaw agent for maximum responsiveness while workers handle heavy lifting in the background. Perfect for distributed AI development!

## 🔗 Links

- **Repository**: https://github.com/AkiSato49/blaude
- **OpenClaw**: https://openclaw.ai
- **Issues & Features**: See `backlog.md`