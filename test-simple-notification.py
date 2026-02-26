#!/usr/bin/env python3
"""
Simple test to verify blaude notifications work
"""
import subprocess
import sys
import time

def test_notification_to_main():
    """Test sending a notification to main agent"""
    print("🧪 Testing notification to main agent...")
    
    try:
        cmd = ["openclaw", "agent", "--agent", "main", "-m", 
               "🎯 **Blaude notification test** completed successfully! System is working!"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Notification sent successfully!")
            print(f"Response: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Notification failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Notification timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_blaude_worker():
    """Test a simple blaude worker that should complete quickly"""
    print("\n🧪 Testing blaude worker with notification...")
    
    try:
        # First test the basic CLI
        cmd = ["python3", "blaude.py", "test-notify", "main"]
        
        print("   Running: python3 blaude.py test-notify main")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Blaude test-notify worked!")
            print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Blaude test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Blaude test timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧶 Blaude Notification Test (Simple)")
    print("=" * 40)
    
    # Test 1: Direct notification
    success1 = test_notification_to_main()
    
    # Test 2: Via blaude CLI
    success2 = test_blaude_worker()
    
    print("\n" + "=" * 40)
    print("📋 RESULTS")
    print("=" * 40)
    print(f"Direct notification: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Blaude CLI test:     {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Ready to spawn workers!")
        return True
    else:
        print("\n⚠️ Some tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)