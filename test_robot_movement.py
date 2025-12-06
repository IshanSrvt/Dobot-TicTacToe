"""
Test robot movement directly without GUI or vision
This will help diagnose if the Dobot hardware is responding
"""

from Python_Dobot_3T import (
    initialize_dobot,
    TicTacToeGame,
    robot_make_move,
    BOARD_POSITIONS,
    device
)
import time

def test_direct_movement():
    """Test Dobot movement directly"""
    print("=" * 60)
    print("DOBOT MOVEMENT TEST")
    print("=" * 60)

    # Initialize Dobot
    print("\n1. Initializing Dobot...")
    dev = initialize_dobot(port="COM4", home_on_init=True)

    if dev is None:
        print("ERROR: Failed to initialize Dobot!")
        return

    print(f"✓ Dobot initialized: {dev}")
    print(f"✓ Global device variable: {device}")

    # Wait for homing to complete
    print("\n2. Waiting for homing to complete...")
    time.sleep(3)

    # Test 1: Simple movement
    print("\n3. Test 1: Moving to safe position...")
    try:
        from Python_Dobot_3T import SAFE_HEIGHT
        cmd_id = device.move_to(250, 0, SAFE_HEIGHT, 0)
        print(f"   Command ID: {cmd_id}")
        device.wait_for_cmd(cmd_id)
        print("   ✓ Movement complete")
        time.sleep(1)
    except Exception as e:
        print(f"   ✗ Movement failed: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Full robot move
    print("\n4. Test 2: Full robot move (pickup + place)...")
    try:
        game = TicTacToeGame(human_color='blue')
        print(f"   Created game: human={game.human_color}, robot={game.robot_color}")
        print(f"   Pieces remaining: {game.pieces_remaining}")

        print("\n   Executing robot_make_move to position 4 (center)...")
        robot_make_move(4, game)
        print("   ✓ Robot move complete!")

    except Exception as e:
        print(f"   ✗ Robot move failed: {e}")
        import traceback
        traceback.print_exc()

    # Return home
    print("\n5. Returning to home position...")
    try:
        cmd_id = device.home()
        device.wait_for_cmd(cmd_id)
        print("   ✓ Returned home")
    except Exception as e:
        print(f"   ✗ Home failed: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

    # Summary
    print("\nIf you saw the robot move:")
    print("  ✓ Hardware is working")
    print("  ✓ Code is correct")
    print("  → Problem is in web server integration")
    print("\nIf robot didn't move:")
    print("  → Check console for error messages")
    print("  → Check Dobot is powered on")
    print("  → Check USB connection")
    print("  → Check COM port is correct")

if __name__ == "__main__":
    test_direct_movement()
