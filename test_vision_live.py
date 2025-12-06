"""
Live Vision Testing Tool
Real-time visualization of vision system detection
"""

import cv2
import numpy as np
from vision_system import TicTacToeVision

def main():
    """Run live vision testing with visualization"""
    print("=" * 70)
    print("LIVE VISION TESTING")
    print("=" * 70)
    print("\nThis tool shows real-time detection of the game board.")
    print("\nControls:")
    print("  q - Quit")
    print("  d - Print current board state")
    print("  s - Save current frame")
    print("  g - Toggle grid overlay")
    print("  c - Check calibration status")
    print("=" * 70)

    vision = TicTacToeVision()

    # Check calibration
    if vision.cell_centers is None:
        print("\n⚠ WARNING: Board not calibrated!")
        print("Run 'python calibrate_camera.py' first.")
        print("Continuing anyway for color detection testing...\n")

    if not vision.open_camera():
        print("❌ Failed to open camera!")
        return

    show_grid = True
    frame_count = 0

    print("\n✓ Camera opened successfully")
    print("✓ Vision system ready\n")

    try:
        while True:
            frame = vision.capture_frame()
            if frame is None:
                print("Failed to capture frame")
                break

            # Create visualization
            viz_frame = vision.visualize_detection(frame, draw_grid=show_grid)

            # Add status text
            status_y = 30
            cv2.putText(viz_frame, "Live Vision Test", (10, status_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Add calibration status
            if vision.cell_centers is not None:
                cal_status = "Calibrated"
                cal_color = (0, 255, 0)
            else:
                cal_status = "Not Calibrated"
                cal_color = (0, 0, 255)

            cv2.putText(viz_frame, cal_status, (10, status_y + 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, cal_color, 2)

            # Add frame counter
            frame_count += 1
            cv2.putText(viz_frame, f"Frame: {frame_count}", (10, viz_frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            # Show the visualization
            cv2.imshow('Live Vision Test', viz_frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("\nExiting...")
                break

            elif key == ord('d'):
                # Detect and print board state
                print("\n" + "=" * 50)
                print("CURRENT BOARD STATE")
                print("=" * 50)

                board_state = vision.detect_board_state()

                if board_state is None:
                    print("Failed to detect board state")
                else:
                    # Print as 3x3 grid
                    for row in range(3):
                        row_cells = []
                        for col in range(3):
                            idx = row * 3 + col
                            cell = board_state[idx]
                            if cell == 'blue':
                                row_cells.append('B')
                            elif cell == 'red':
                                row_cells.append('R')
                            else:
                                row_cells.append('.')
                        print(f"  {' '.join(row_cells)}")

                    # Count pieces
                    blue_count = board_state.count('blue')
                    red_count = board_state.count('red')
                    empty_count = board_state.count(None)

                    print(f"\nBlue pieces: {blue_count}")
                    print(f"Red pieces: {red_count}")
                    print(f"Empty cells: {empty_count}")

                print("=" * 50 + "\n")

            elif key == ord('s'):
                # Save current frame
                filename = f"vision_test_frame_{frame_count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"\n✓ Frame saved to {filename}")

            elif key == ord('g'):
                # Toggle grid overlay
                show_grid = not show_grid
                status = "ON" if show_grid else "OFF"
                print(f"\n✓ Grid overlay: {status}")

            elif key == ord('c'):
                # Check calibration status
                print("\n" + "=" * 50)
                print("CALIBRATION STATUS")
                print("=" * 50)

                print(f"Blue HSV: {vision.blue_lower} to {vision.blue_upper}")
                print(f"Red HSV: {vision.red_lower} to {vision.red_upper}")

                if vision.board_corners is not None:
                    print(f"\nBoard corners defined: ✓")
                    for i, corner in enumerate(vision.board_corners):
                        print(f"  Corner {i+1}: ({corner[0]:.1f}, {corner[1]:.1f})")
                else:
                    print(f"\nBoard corners defined: ✗")
                    print("Run 'python calibrate_camera.py' to calibrate")

                if vision.cell_centers is not None:
                    print(f"\nCell centers calculated: ✓")
                    print(f"Total cells: {len(vision.cell_centers)}")
                else:
                    print(f"\nCell centers calculated: ✗")

                print("=" * 50 + "\n")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        vision.close_camera()
        cv2.destroyAllWindows()
        print("\n✓ Camera closed")
        print("✓ Vision test complete\n")

if __name__ == "__main__":
    main()
