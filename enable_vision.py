"""
Quick script to enable vision monitoring
Run this after starting the web server
"""

import requests
import json

def enable_vision():
    """Enable vision monitoring via API"""
    url = "http://localhost:5000/api/vision/toggle"

    print("=" * 60)
    print("ENABLING VISION SYSTEM")
    print("=" * 60)

    try:
        # Enable vision
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json={'enable': True}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ {data['message']}")
            print(f"  Vision enabled: {data['vision_enabled']}")
        else:
            print(f"\n✗ Failed to enable vision")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to web server")
        print("  Make sure web server is running: python web_server.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")

def disable_vision():
    """Disable vision monitoring via API"""
    url = "http://localhost:5000/api/vision/toggle"

    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            json={'enable': False}
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ {data['message']}")
        else:
            print(f"\n✗ Failed to disable vision")

    except Exception as e:
        print(f"\n✗ Error: {e}")

def check_vision_status():
    """Check vision system status"""
    url = "http://localhost:5000/api/vision/status"

    print("\n" + "=" * 60)
    print("VISION SYSTEM STATUS")
    print("=" * 60)

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(f"\nVision enabled: {data['vision_enabled']}")
            print(f"Calibration file exists: {data['calibration_exists']}")

            if not data['calibration_exists']:
                print("\n⚠ WARNING: No calibration file found!")
                print("  Run: python calibrate_camera.py")
        else:
            print(f"\n✗ Failed to check status")

    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to web server")
        print("  Make sure web server is running: python web_server.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("VISION CONTROL SCRIPT")
    print("=" * 60)
    print("\nWhat would you like to do?")
    print("1. Enable vision monitoring")
    print("2. Disable vision monitoring")
    print("3. Check vision status")
    print("=" * 60)

    choice = input("\nEnter choice (1-3): ").strip()

    if choice == "1":
        enable_vision()
        check_vision_status()
    elif choice == "2":
        disable_vision()
        check_vision_status()
    elif choice == "3":
        check_vision_status()
    else:
        print("Invalid choice")

    print("\n" + "=" * 60)
