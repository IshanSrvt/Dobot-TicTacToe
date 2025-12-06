"""
Quick verification that the GUI fix was applied correctly
Checks if startGame() function calls the backend API
"""

import os
import re
import sys

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_gui_file():
    """Check if GUI_for_3T.html has the correct API calls"""

    print("=" * 70)
    print("VERIFYING GUI FIX")
    print("=" * 70)

    gui_path = "GUI_for_3T.html"

    if not os.path.exists(gui_path):
        print(f"❌ ERROR: {gui_path} not found!")
        return False

    print(f"\n✓ Found {gui_path}")

    with open(gui_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check 1: Does startGame function exist?
    if 'function startGame(humanColor)' not in content:
        print("❌ ERROR: startGame function not found!")
        return False
    print("✓ startGame function exists")

    # Check 2: Does it call fetch to /api/start?
    if "fetch('http://localhost:5000/api/start'" not in content:
        print("❌ ERROR: startGame doesn't call /api/start!")
        print("   The GUI is NOT calling the backend API")
        print("   You need to refresh your browser with Ctrl+Shift+R")
        return False
    print("✓ startGame calls fetch('/api/start')")

    # Check 3: Does it send use_vision: true?
    if 'use_vision: true' not in content:
        print("⚠️  WARNING: use_vision flag not found")
        print("   Vision might not enable automatically")
    else:
        print("✓ Vision enabled by default (use_vision: true)")

    # Check 4: Does resetGame call /api/reset?
    if "fetch('http://localhost:5000/api/reset'" not in content:
        print("⚠️  WARNING: resetGame doesn't call /api/reset")
    else:
        print("✓ resetGame calls fetch('/api/reset')")

    # Check 5: Socket.IO library included?
    if 'socket.io' not in content.lower():
        print("❌ ERROR: Socket.IO library not included!")
        return False
    print("✓ Socket.IO library included")

    # Check 6: Socket.IO event handlers for moves?
    if 'human_move_detected' not in content:
        print("⚠️  WARNING: No handler for 'human_move_detected' event")
    else:
        print("✓ Handler for vision-detected moves exists")

    if 'robot_move_complete' not in content:
        print("⚠️  WARNING: No handler for 'robot_move_complete' event")
    else:
        print("✓ Handler for robot moves exists")

    print("\n" + "=" * 70)
    print("GUI FILE CHECK: ✓ PASSED")
    print("=" * 70)
    return True

def check_python_file():
    """Check if Python_Dobot_3T.py has correct imports and methods"""

    print("\n" + "=" * 70)
    print("VERIFYING PYTHON FILE")
    print("=" * 70)

    py_path = "Python_Dobot_3T.py"

    if not os.path.exists(py_path):
        print(f"❌ ERROR: {py_path} not found!")
        return False

    print(f"\n✓ Found {py_path}")

    with open(py_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check for conflicting import
    for i, line in enumerate(lines[:10], 1):  # Check first 10 lines
        if 'from pydobot import Dobot' in line and not line.strip().startswith('#'):
            print(f"❌ ERROR: Line {i} has conflicting import!")
            print(f"   {line.strip()}")
            print("   This will cause 'wait_for_cmd' errors")
            print("   Comment out or remove this line")
            return False

    print("✓ No conflicting 'from pydobot import Dobot'")

    # Check for correct import
    content = ''.join(lines)
    if 'from Python_Dobot_setup import' not in content:
        print("❌ ERROR: Missing 'from Python_Dobot_setup import'")
        return False
    print("✓ Correct import from Python_Dobot_setup")

    # Check for wait_for_cmd usage
    wait_for_cmd_count = content.count('wait_for_cmd')
    if wait_for_cmd_count == 0:
        print("⚠️  WARNING: No wait_for_cmd calls found")
        print("   Robot movements might not wait for completion")
    else:
        print(f"✓ Found {wait_for_cmd_count} wait_for_cmd calls")

    # Check for home after move
    if 'Returning to home position' in content:
        print("✓ Robot homes after move (found debug message)")
    else:
        print("⚠️  WARNING: Home after move might not be implemented")

    print("\n" + "=" * 70)
    print("PYTHON FILE CHECK: ✓ PASSED")
    print("=" * 70)
    return True

def check_web_server():
    """Check if web_server.py has vision integration"""

    print("\n" + "=" * 70)
    print("VERIFYING WEB SERVER")
    print("=" * 70)

    server_path = "web_server.py"

    if not os.path.exists(server_path):
        print(f"❌ ERROR: {server_path} not found!")
        return False

    print(f"\n✓ Found {server_path}")

    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for API endpoints
    endpoints = [
        ('/api/start', 'Game start endpoint'),
        ('/api/reset', 'Game reset endpoint'),
        ('/api/vision/toggle', 'Vision toggle endpoint'),
        ('/api/move/human', 'Human move endpoint'),
    ]

    for endpoint, description in endpoints:
        if endpoint in content:
            print(f"✓ {description}: {endpoint}")
        else:
            print(f"⚠️  WARNING: Missing {endpoint}")

    # Check for Socket.IO
    if 'socketio' in content.lower():
        print("✓ Socket.IO integration present")
    else:
        print("❌ ERROR: Socket.IO not found!")
        return False

    # Check for vision system
    if 'vision_system' in content:
        print("✓ Vision system integrated")
    else:
        print("⚠️  WARNING: Vision system might not be integrated")

    print("\n" + "=" * 70)
    print("WEB SERVER CHECK: ✓ PASSED")
    print("=" * 70)
    return True

def main():
    """Run all verification checks"""

    print("\n")
    print("=" * 70)
    print(" " * 18 + "DOBOT TIC-TAC-TOE FIX VERIFICATION")
    print("=" * 70)
    print()

    results = {
        'GUI': check_gui_file(),
        'Python': check_python_file(),
        'Server': check_web_server()
    }

    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    all_passed = True
    for component, passed in results.items():
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{component:15} {status}")
        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n>>> ALL CHECKS PASSED <<<")
        print("\nYour system is ready to test!")
        print("\nNext steps:")
        print("1. Start web server: python web_server.py")
        print("2. Enable vision: python enable_vision.py (option 1)")
        print("3. Open browser: http://localhost:5000")
        print("4. Click 'Blue (You)' button")
        print("5. Check server console for 'POST /api/start'")
        print("6. Camera window should show 'Game Active'")
        print("\nSee TESTING_STEPS.md for detailed testing guide")
    else:
        print("\n>>> SOME CHECKS FAILED <<<")
        print("\nPlease fix the errors above before testing")
        print("See FINAL_FIXES.md for what should be in place")

    print()

if __name__ == "__main__":
    main()
