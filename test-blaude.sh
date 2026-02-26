#!/bin/bash
set -e

echo "🧶 Testing Blaude Minimal..."
echo

# Clean start
echo "📝 Cleaning up any existing workers..."
python3 blaude-minimal.py cleanup

echo "📋 Initial worker list:"
python3 blaude-minimal.py list
echo

# Spawn a few test workers
echo "🚀 Spawning test workers..."
python3 blaude-minimal.py spawn quick-test "Just say hello briefly" --budget 0.1 --notify dev-general
python3 blaude-minimal.py spawn file-check "List files in /tmp and explain what you see" --model haiku --budget 0.5 --notify dev-general

echo "📋 Workers after spawning:"
python3 blaude-minimal.py list
echo

echo "⏳ Waiting 5 seconds for workers to progress..."
sleep 5

echo "📋 Workers after 5 seconds:"
python3 blaude-minimal.py list
echo

echo "🗑️ Killing quick-test worker:"
python3 blaude-minimal.py kill quick-test

echo "📋 Final worker status:"
python3 blaude-minimal.py list
echo

echo "✅ Test complete! Check /tmp/blaude-logs/ for worker output."
ls -la /tmp/blaude-logs/