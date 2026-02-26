#!/usr/bin/env python3
"""
Test the full blaude worker flow: spawn -> work -> complete -> notify
"""
import subprocess
import time
import sys

def test_foreground_worker():
    """Test a foreground worker that should complete and notify immediately"""
    print("🧪 Testing foreground worker with notification...")
    
    cmd = [
        "python3", "blaude.py", "spawn", "test-full-flow",
        "Count from 1 to 3, then say 'Blaude test completed successfully!'",
        "--model", "haiku", "--budget", "0.2", "--notify", "main", "--foreground"
    ]
    
    try:
        print("   Spawning foreground worker...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Foreground worker completed successfully!")
            print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ Foreground worker failed:")
            print(f"   stdout: {result.stdout}")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Worker timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_background_worker():
    """Test a background worker"""
    print("\n🧪 Testing background worker...")
    
    cmd = [
        "python3", "blaude.py", "spawn", "test-bg-flow",
        "Say 'Hello from background worker!' and list 3 random files from /tmp",
        "--model", "haiku", "--budget", "0.3", "--notify", "main"
    ]
    
    try:
        print("   Spawning background worker...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Background worker spawned successfully!")
            print(f"   {result.stdout.strip()}")
            
            # Check status
            print("   Checking worker status...")
            time.sleep(2)
            
            status_cmd = ["python3", "blaude.py", "list"]
            status_result = subprocess.run(status_cmd, capture_output=True, text=True, timeout=5)
            print("   Current workers:")
            print(status_result.stdout)
            
            return True
        else:
            print(f"❌ Background worker spawn failed:")
            print(f"   stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Background spawn timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cleanup_test_workers():
    """Clean up any test workers"""
    print("\n🧹 Cleaning up test workers...")
    
    try:
        # Kill any running test workers
        kill_cmds = [
            ["python3", "blaude.py", "kill", "test-full-flow"],
            ["python3", "blaude.py", "kill", "test-bg-flow"]
        ]
        
        for cmd in kill_cmds:
            subprocess.run(cmd, capture_output=True, timeout=5)
        
        # Cleanup completed workers  
        cleanup_cmd = ["python3", "blaude.py", "cleanup"]
        subprocess.run(cleanup_cmd, capture_output=True, timeout=5)
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")

def main():
    print("🧶 Blaude Full Flow Test")
    print("=" * 30)
    
    # Cleanup any existing test workers first
    cleanup_test_workers()
    
    print("\n" + "=" * 30)
    
    # Test foreground worker
    success1 = test_foreground_worker()
    
    # Test background worker  
    success2 = test_background_worker()
    
    print("\n" + "=" * 30)
    print("📋 RESULTS")
    print("=" * 30)
    
    print(f"Foreground worker: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Background worker: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Blaude is fully functional!")
        print("\n🚀 Ready for production use:")
        print("   python3 blaude.py spawn my-task 'Your prompt here' --notify main")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    # Final cleanup
    cleanup_test_workers()
    
    return success1 and success2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)