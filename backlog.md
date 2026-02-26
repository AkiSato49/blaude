# Blaude Development Backlog

## ✅ Completed (v0.1 - Minimal)

### Core Architecture
- ✅ **blaude-minimal.py** - Single-file working implementation
- ✅ **runner.py** - Full Claude Code worker management with PM2-style tracking
- ✅ **notifier.py** - OpenClaw integration for completion notifications  
- ✅ **blaude.py** - Main CLI coordinator with argparse interface
- ✅ **Background execution** - nohup + session tracking + monitoring
- ✅ **Budget controls** - Claude CLI budget limits
- ✅ **Configurable notifications** - Target any OpenClaw agent
- ✅ **Persistent state** - JSON worker tracking across restarts
- ✅ **Process monitoring** - Status tracking + completion detection

### CLI Interface
- ✅ `blaude spawn <name> <prompt> --model --budget --notify`
- ✅ `blaude list` - Worker table with status/age/PID
- ✅ `blaude kill <name>` - Terminate workers cleanly
- ✅ `blaude cleanup` - Remove completed workers
- ✅ `blaude status` - System overview
- ✅ `blaude test-notify <target>` - Test notification system

## 🚧 In Progress (v0.2 - Full)

### TUI Dashboard
- 🚧 **tui.py** - Textual interface (placeholder completed)
- 📋 Worker boxes (max 8) with live status
- 📋 Real-time log tailing
- 📋 Color-coded cost/token tracking
- 📋 Interactive controls (spawn/kill/steer)
- 📋 Auto-refresh every 2-5 seconds

## 📋 TODO (Future Versions)

### v0.3 - Enhanced Features
- [ ] **Worker templates** - Saved prompt + model + budget combinations
- [ ] **Session resumption** - Resume interrupted Claude sessions
- [ ] **Steering capabilities** - Send new directions to running workers
- [ ] **Cost dashboard** - Real-time spend tracking with alerts
- [ ] **Log archival** - Compress and store completed worker logs
- [ ] **Health checks** - Auto-restart failed workers
- [ ] **Dependency chains** - Worker B waits for Worker A completion

### v0.4 - Advanced Integration
- [ ] **Project context injection** - Auto-include relevant project files
- [ ] **Git integration** - Auto-commit worker outputs
- [ ] **Batch operations** - Process multiple tasks simultaneously  
- [ ] **Worker specialization** - Different types (test, docs, deploy)
- [ ] **Resource limits** - Memory/time limits per worker
- [ ] **Notification channels** - Email/Slack in addition to OpenClaw

### v1.0 - Production Ready
- [ ] **Configuration system** - YAML/TOML config files
- [ ] **Multi-user support** - Worker isolation
- [ ] **API server mode** - HTTP API for external integrations
- [ ] **Metrics & observability** - Prometheus/Grafana integration
- [ ] **Docker support** - Containerized deployment
- [ ] **Plugin system** - Custom worker types and notifications

## 🐛 Known Issues

### Fixed in v0.1
- ✅ Process monitoring race condition (fast completion detection)
- ✅ UUID generation for Claude sessions
- ✅ Import path issues in modular architecture

### Current Issues  
- [ ] TUI not yet implemented (placeholder only)
- [ ] No cost tracking in runner (logs only)
- [ ] No session resumption after system restart

## 🎯 Next Sprint Priorities

1. **Complete TUI implementation** - Based on subagent-dashboard proven code
2. **Test notification system** - Verify OpenClaw integration works
3. **Worker templates** - Save/load common task patterns
4. **Cost tracking** - Parse token usage from Claude logs

## 📊 Architecture Status

```
blaude/
├── ✅ blaude.py         # CLI coordinator
├── ✅ runner.py         # Worker management  
├── ✅ notifier.py       # OpenClaw notifications
├── 🚧 tui.py           # TUI dashboard (placeholder)
├── ✅ blaude-minimal.py # Single-file version
├── ✅ test-blaude.sh    # Test suite
└── 📋 templates/        # Worker templates (TODO)
```

**Status**: **Core functionality complete and working!** 🎯