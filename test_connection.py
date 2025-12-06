"""
Quick test script to verify the web server and GUI connection
Run this before starting the full application
"""
import sys

def test_imports():
    """Test that all required packages are installed"""
    print("Testing imports...")

    try:
        import flask
        print("✓ Flask installed")
    except ImportError:
        print("✗ Flask not installed. Run: pip install flask")
        return False

    try:
        import flask_socketio
        print("✓ Flask-SocketIO installed")
    except ImportError:
        print("✗ Flask-SocketIO not installed. Run: pip install flask-socketio")
        return False

    try:
        import cv2
        print("✓ OpenCV installed")
    except ImportError:
        print("✗ OpenCV not installed. Run: pip install opencv-python")
        return False

    try:
        import numpy
        print("✓ NumPy installed")
    except ImportError:
        print("✗ NumPy not installed. Run: pip install numpy")
        return False

    try:
        import pydobot
        print("✓ PyDobot installed")
    except ImportError:
        print("✗ PyDobot not installed. Run: pip install pydobot")
        return False

    return True

def test_files():
    """Test that all required files exist"""
    print("\nTesting files...")
    import os

    files = [
        'Python_Dobot_3T.py',
        'Python_Dobot_setup.py',
        'web_server.py',
        'GUI_for_3T.html'
    ]

    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            all_exist = False

    return all_exist

def test_dobot_connection():
    """Test connection to Dobot"""
    print("\nTesting Dobot connection...")

    try:
        from Python_Dobot_setup import Dobot
        print("✓ Dobot module loaded")

        # Note: This will actually try to connect to the Dobot
        # If no Dobot is connected, this will fail
        print("  Attempting to connect to COM4...")
        print("  (This may take a few seconds)")

        device = Dobot(port="COM4")
        print("✓ Dobot connected successfully")

        # Get current position
        pose = device.get_pose()
        print(f"  Current position: x={pose.position.x:.2f}, y={pose.position.y:.2f}, z={pose.position.z:.2f}")

        return True

    except Exception as e:
        print(f"✗ Dobot connection failed: {e}")
        print("  Make sure:")
        print("  - Dobot is powered on")
        print("  - USB cable is connected")
        print("  - Correct COM port (check Device Manager)")
        return False

def test_port_availability():
    """Test if port 5000 is available"""
    print("\nTesting port availability...")

    import socket

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))

    if result == 0:
        print("✗ Port 5000 is already in use")
        print("  Another application may be using it")
        sock.close()
        return False
    else:
        print("✓ Port 5000 is available")
        sock.close()
        return True

def main():
    print("=" * 60)
    print("TIC-TAC-TOE ROBOT - CONNECTION TEST")
    print("=" * 60)

    # Run all tests
    imports_ok = test_imports()
    files_ok = test_files()
    port_ok = test_port_availability()

    # Optional: Test Dobot (may fail if not connected)
    print("\n" + "=" * 60)
    test_dobot = input("Test Dobot connection? (y/n): ").lower()

    if test_dobot == 'y':
        dobot_ok = test_dobot_connection()
    else:
        dobot_ok = None
        print("Skipping Dobot test")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    print(f"Files: {'✓ PASS' if files_ok else '✗ FAIL'}")
    print(f"Port 5000: {'✓ PASS' if port_ok else '✗ FAIL'}")

    if dobot_ok is not None:
        print(f"Dobot: {'✓ PASS' if dobot_ok else '✗ FAIL'}")
    else:
        print("Dobot: SKIPPED")

    print("=" * 60)

    if imports_ok and files_ok and port_ok:
        print("\n✓ All basic tests passed!")
        print("You can now run: python web_server.py")
        if dobot_ok is False:
            print("\nNote: Dobot connection failed, but you can still test the GUI")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
