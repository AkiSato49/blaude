#!/usr/bin/env python3
"""
Test script to verify Blaude notification system works with dev-general
"""
import sys
import time
import subprocess
from pathlib import Path

def test_direct_notification():
    """Test direct notification to dev-general"""
    print("🧪 Testing direct notification to dev-general...")
    
    try:
        cmd = ["openclaw", "agent", "--agent", "dev-general", "-m", 
               "🧶 Blaude notification test - direct message works!"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Direct notification successful!")
            return True
        else:
            print(f"❌ Direct notification failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Direct notification error: {e}")
        return False

def test_notifier_class():
    """Test the Notifier class"""
    print("🧪 Testing Notifier class...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        from notifier import Notifier
        
        notifier = Notifier()
        success = notifier.test_notification("dev-general")
        
        if success:
            print("✅ Notifier class test successful!")
            return True
        else:
            print("❌ Notifier class test failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Notifier test error: {e}")
        return False

def test_full_worker_flow():
    """Test a complete worker spawn -> completion -> notification flow"""
    print("🧪 Testing full worker flow (spawn -> complete -> notify)...")
    
    try:
        # Spawn a quick worker using the main blaude CLI
        cmd = [
            "python3", "blaude.py", "spawn", "notification-test",
            "Just say 'Hello from blaude worker test!' and nothing else",
            "--model", "haiku", "--budget", "0.1", "--notify", "dev-general", "--foreground"
        ]
        
        print("   Spawning test worker...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Worker spawned and completed successfully!")
            print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ Worker failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Worker timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Full worker flow error: {e}")
        return False

def test_background_worker():
    """Test a background worker that should notify when complete"""
    print("🧪 Testing background worker with notification...")
    
    try:
        # Spawn background worker
        cmd = [
            "python3", "blaude.py", "spawn", "bg-notification-test",
            "Count from 1 to 3, then say 'Background worker complete!'",
            "--model", "haiku", "--budget", "0.2", "--notify", "dev-general"
        ]
        
        print("   Spawning background worker...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Background worker spawned!")
            print("   Worker should notify dev-general when complete...")
            
            # Show status
            time.sleep(2)
            status_cmd = ["python3", "blaude.py", "list"]
            status_result = subprocess.run(status_cmd, capture_output=True, text=True)
            print("   Current workers:")
            print(status_result.stdout)
            
            return True
        else:
            print(f"❌ Background worker spawn failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Background worker test error: {e}")
        return False

def main():
    """Run all notification tests"""
    print("🧶 Blaude Notification System Tests")
    print("=" * 50)
    
    tests = [
        ("Direct OpenClaw Message", test_direct_notification),
        ("Notifier Class", test_notifier_class),
        ("Full Worker Flow (Foreground)", test_full_worker_flow),
        ("Background Worker", test_background_worker),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Notification system is working!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)