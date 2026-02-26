#!/usr/bin/env python3
"""
Notifier - OpenClaw integration for completion notifications
"""
import subprocess
import time
from typing import Optional

class Notifier:
    """Handles notifications to OpenClaw agents when workers complete"""
    
    def __init__(self):
        pass
    
    def notify_completion(self, worker_name: str, summary: str, duration: int, 
                         target: str = "main") -> bool:
        """
        Notify completion via openclaw agent message
        
        Args:
            worker_name: Name of the completed worker
            summary: Summary of the work done
            duration: Duration in seconds  
            target: Target agent to notify
            
        Returns:
            True if notification sent successfully
        """
        
        # Format duration nicely
        if duration < 60:
            duration_str = f"{duration}s"
        elif duration < 3600:
            duration_str = f"{duration // 60}m {duration % 60}s"
        else:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            duration_str = f"{hours}h {minutes}m"
        
        # Create notification message
        message = self._format_completion_message(worker_name, summary, duration_str)
        
        return self._send_openclaw_message(target, message)
    
    def notify_error(self, worker_name: str, error: str, target: str = "main") -> bool:
        """Notify about worker errors"""
        message = f"❌ Worker **{worker_name}** failed:\n```\n{error}\n```"
        return self._send_openclaw_message(target, message)
    
    def notify_killed(self, worker_name: str, target: str = "main") -> bool:
        """Notify about manually killed workers"""
        message = f"🛑 Worker **{worker_name}** was manually terminated"
        return self._send_openclaw_message(target, message)
    
    def _format_completion_message(self, worker_name: str, summary: str, duration_str: str) -> str:
        """Format a completion notification message"""
        
        # Clean up summary for display
        clean_summary = summary.strip()
        if len(clean_summary) > 500:
            clean_summary = clean_summary[:500] + "..."
        
        # Build message
        message = f"🎯 Worker **{worker_name}** completed ({duration_str})"
        
        if clean_summary and clean_summary != "No output captured":
            # Add summary in code block if it looks like output
            if any(char in clean_summary for char in ['{', '[', ':', '\n']):
                message += f"\n```\n{clean_summary}\n```"
            else:
                message += f"\n\n{clean_summary}"
        
        return message
    
    def _send_openclaw_message(self, target: str, message: str) -> bool:
        """Send message via openclaw agent message command"""
        try:
            cmd = ["openclaw", "agent", "--agent", target, "-m", message]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                print(f"📤 Notified {target}: {message[:50]}...")
                return True
            else:
                print(f"❌ Failed to notify {target}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout sending notification to {target}")
            return False
        except Exception as e:
            print(f"❌ Error sending notification to {target}: {e}")
            return False
    
    def test_notification(self, target: str = "main") -> bool:
        """Send a test notification to verify the system works"""
        test_message = "🧪 Blaude notification test - system is working!"
        print(f"Sending test notification to {target}...")
        return self._send_openclaw_message(target, test_message)