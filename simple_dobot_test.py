"""
Simple Dobot test without wait_for_cmd
Tests if basic Dobot connection and movement works
"""

print("Starting simple Dobot test...")
print("=" * 60)

# Test 1: Import
print("\n1. Testing imports...")
try:
    from Python_Dobot_setup import Dobot, MODE_PTP
    print("   ✓ Imported from Python_Dobot_setup.py")
except Exception as e:
    print(f"   ✗ Import failed: {e}")
    exit(1)

# Test 2: Check if Dobot class has wait_for_cmd
print("\n2. Checking Dobot class methods...")
if hasattr(Dobot, 'wait_for_cmd'):
    print("   ✓ Dobot has wait_for_cmd method")
else:
    print("   ✗ Dobot missing wait_for_cmd method")
    print("   Available methods:", [m for m in dir(Dobot) if not m.startswith('_')])

# Test 3: Connect to Dobot
print("\n3. Connecting to Dobot on COM4...")
try:
    device = Dobot(port="COM4")
    print(f"   ✓ Connected: {device}")
    print(f"   Type: {type(device)}")
except Exception as e:
    print(f"   ✗ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Check device methods
print("\n4. Checking connected device methods...")
if hasattr(device, 'wait_for_cmd'):
    print("   ✓ Device instance has wait_for_cmd")
else:
    print("   ✗ Device instance missing wait_for_cmd")
    print("   Available methods:", [m for m in dir(device) if not m.startswith('_') and callable(getattr(device, m))])

# Test 5: Try to get current position
print("\n5. Testing get_pose...")
try:
    pose = device.get_pose()
    print(f"   ✓ Current position:")
    print(f"     x={pose.position.x:.2f}")
    print(f"     y={pose.position.y:.2f}")
    print(f"     z={pose.position.z:.2f}")
except Exception as e:
    print(f"   ✗ get_pose failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Try simple movement
print("\n6. Testing movement (without wait_for_cmd)...")
try:
    import time

    # Just send the command, don't wait
    cmd_id = device.move_to(250, 0, 50, 0)
    print(f"   Command sent, ID: {cmd_id}")
    print(f"   Waiting 3 seconds for movement...")
    time.sleep(3)
    print("   ✓ Movement command sent")

except Exception as e:
    print(f"   ✗ Movement failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Try with wait_for_cmd if available
print("\n7. Testing with wait_for_cmd...")
try:
    if hasattr(device, 'wait_for_cmd'):
        cmd_id = device.move_to(200, 0, 50, 0)
        print(f"   Command ID: {cmd_id}")
        device.wait_for_cmd(cmd_id)
        print("   ✓ Movement with wait completed")
    else:
        print("   ⊘ Skipping (wait_for_cmd not available)")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

print("\nIf movements worked:")
print("  → Dobot hardware is functioning")
print("  → Problem is in game integration")
print("\nIf wait_for_cmd missing:")
print("  → Wrong Dobot library being used")
print("  → Check imports in Python_Dobot_3T.py")
print("\nIf no movement:")
print("  → Check Dobot power and USB")
print("  → Check COM port is correct")

print("\n")
