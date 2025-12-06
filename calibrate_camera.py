"""
Interactive Camera Calibration Tool
Calibrate color ranges and board corners for the vision system
"""

import cv2
import numpy as np
from vision_system import TicTacToeVision

# ============================================================================
# CALIBRATION STATE
# ============================================================================

calibration_mode = 'color'  # 'color' or 'board'
current_color = 'blue'  # 'blue' or 'red'
corner_index = 0  # 0-3 for four corners
selected_corners = []

# Trackbar values
blue_h_min = 90
blue_h_max = 130
blue_s_min = 50
blue_s_max = 255
blue_v_min = 50
blue_v_max = 255

red_h_min = 0
red_h_max = 10
red_s_min = 50
red_s_max = 255
red_v_min = 50
red_v_max = 255

# ============================================================================
# TRACKBAR CALLBACKS
# ============================================================================

def nothing(x):
    """Dummy callback for trackbars"""
    pass

def update_blue_h_min(val):
    global blue_h_min
    blue_h_min = val

def update_blue_h_max(val):
    global blue_h_max
    blue_h_max = val

def update_blue_s_min(val):
    global blue_s_min
    blue_s_min = val

def update_blue_s_max(val):
    global blue_s_max
    blue_s_max = val

def update_blue_v_min(val):
    global blue_v_min
    blue_v_min = val

def update_blue_v_max(val):
    global blue_v_max
    blue_v_max = val

def update_red_h_min(val):
    global red_h_min
    red_h_min = val

def update_red_h_max(val):
    global red_h_max
    red_h_max = val

def update_red_s_min(val):
    global red_s_min
    red_s_min = val

def update_red_s_max(val):
    global red_s_max
    red_s_max = val

def update_red_v_min(val):
    global red_v_min
    red_v_min = val

def update_red_v_max(val):
    global red_v_max
    red_v_max = val

# ============================================================================
# MOUSE CALLBACK FOR BOARD CORNER SELECTION
# ============================================================================

def mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks for corner selection"""
    global selected_corners, corner_index

    if event == cv2.EVENT_LBUTTONDOWN:
        if calibration_mode == 'board' and corner_index < 4:
            selected_corners.append([x, y])
            corner_index += 1
            print(f"Corner {corner_index}/4 selected: ({x}, {y})")

            if corner_index == 4:
                print("All corners selected! Press 's' to save calibration.")

# ============================================================================
# MAIN CALIBRATION FUNCTION
# ============================================================================

def calibrate():
    """Run the interactive calibration tool"""
    global calibration_mode, current_color, corner_index, selected_corners

    vision = TicTacToeVision()

    if not vision.open_camera():
        print("Failed to open camera!")
        return

    # Create windows
    cv2.namedWindow('Calibration')
    cv2.namedWindow('Mask')

    # Set mouse callback
    cv2.setMouseCallback('Calibration', mouse_callback)

    # Create trackbars for blue color
    cv2.createTrackbar('Blue H Min', 'Calibration', blue_h_min, 179, update_blue_h_min)
    cv2.createTrackbar('Blue H Max', 'Calibration', blue_h_max, 179, update_blue_h_max)
    cv2.createTrackbar('Blue S Min', 'Calibration', blue_s_min, 255, update_blue_s_min)
    cv2.createTrackbar('Blue S Max', 'Calibration', blue_s_max, 255, update_blue_s_max)
    cv2.createTrackbar('Blue V Min', 'Calibration', blue_v_min, 255, update_blue_v_min)
    cv2.createTrackbar('Blue V Max', 'Calibration', blue_v_max, 255, update_blue_v_max)

    # Create trackbars for red color
    cv2.createTrackbar('Red H Min', 'Calibration', red_h_min, 179, update_red_h_min)
    cv2.createTrackbar('Red H Max', 'Calibration', red_h_max, 179, update_red_h_max)
    cv2.createTrackbar('Red S Min', 'Calibration', red_s_min, 255, update_red_s_min)
    cv2.createTrackbar('Red S Max', 'Calibration', red_s_max, 255, update_red_s_max)
    cv2.createTrackbar('Red V Min', 'Calibration', red_v_min, 255, update_red_v_min)
    cv2.createTrackbar('Red V Max', 'Calibration', red_v_max, 255, update_red_v_max)

    print("\n" + "=" * 60)
    print("CAMERA CALIBRATION TOOL")
    print("=" * 60)
    print("\nMODE 1: COLOR CALIBRATION")
    print("  - Adjust trackbars to detect blue and red pieces")
    print("  - Press 'b' to test BLUE detection")
    print("  - Press 'r' to test RED detection")
    print("\nMODE 2: BOARD CALIBRATION")
    print("  - Press 'c' to enter corner selection mode")
    print("  - Click on 4 corners in order:")
    print("    1. Top-Left")
    print("    2. Top-Right")
    print("    3. Bottom-Right")
    print("    4. Bottom-Left")
    print("\nGENERAL:")
    print("  - Press 's' to SAVE calibration")
    print("  - Press 'q' to QUIT")
    print("=" * 60)

    while True:
        frame = vision.capture_frame()
        if frame is None:
            break

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Update vision system color ranges
        vision.blue_lower = np.array([blue_h_min, blue_s_min, blue_v_min])
        vision.blue_upper = np.array([blue_h_max, blue_s_max, blue_v_max])
        vision.red_lower = np.array([red_h_min, red_s_min, red_v_min])
        vision.red_upper = np.array([red_h_max, red_s_max, red_v_max])

        # Create mask based on current color
        if current_color == 'blue':
            mask = cv2.inRange(hsv, vision.blue_lower, vision.blue_upper)
            label = "BLUE Detection Mode"
            color_bgr = (255, 0, 0)
        else:  # red
            mask1 = cv2.inRange(hsv, vision.red_lower, vision.red_upper)
            mask2 = cv2.inRange(hsv, np.array([170, red_s_min, red_v_min]),
                               np.array([180, red_s_max, red_v_max]))
            mask = cv2.bitwise_or(mask1, mask2)
            label = "RED Detection Mode"
            color_bgr = (0, 0, 255)

        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw on output frame
        output = frame.copy()

        # Draw mode label
        cv2.putText(output, label, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, color_bgr, 2)

        # Draw calibration mode
        if calibration_mode == 'board':
            cv2.putText(output, f"Board Corner Selection: {corner_index}/4", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Draw contours and centers
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Minimum area
                cv2.drawContours(output, [contour], -1, color_bgr, 2)

                # Calculate and draw center
                M = cv2.moments(contour)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    cv2.circle(output, (cx, cy), 5, color_bgr, -1)
                    cv2.putText(output, f"A:{int(area)}", (cx+10, cy+10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_bgr, 1)

        # Draw selected corners
        for i, corner in enumerate(selected_corners):
            cv2.circle(output, tuple(corner), 10, (0, 255, 0), -1)
            cv2.putText(output, str(i+1), (corner[0]+15, corner[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Draw lines between corners if we have multiple
        if len(selected_corners) > 1:
            for i in range(len(selected_corners)):
                if i < len(selected_corners) - 1:
                    cv2.line(output, tuple(selected_corners[i]),
                            tuple(selected_corners[i+1]), (0, 255, 0), 2)
            # Close the quadrilateral if all 4 corners selected
            if len(selected_corners) == 4:
                cv2.line(output, tuple(selected_corners[3]),
                        tuple(selected_corners[0]), (0, 255, 0), 2)

        # Show frames
        cv2.imshow('Calibration', output)
        cv2.imshow('Mask', mask)

        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("\nCalibration cancelled")
            break

        elif key == ord('b'):
            current_color = 'blue'
            print("\nSwitched to BLUE detection mode")

        elif key == ord('r'):
            current_color = 'red'
            print("\nSwitched to RED detection mode")

        elif key == ord('c'):
            calibration_mode = 'board'
            corner_index = 0
            selected_corners = []
            print("\n" + "=" * 60)
            print("BOARD CORNER SELECTION MODE")
            print("=" * 60)
            print("Click on the 4 corners of the game board in order:")
            print("  1. Top-Left corner")
            print("  2. Top-Right corner")
            print("  3. Bottom-Right corner")
            print("  4. Bottom-Left corner")
            print("=" * 60)

        elif key == ord('s'):
            # Save calibration
            vision.board_corners = np.array(selected_corners) if len(selected_corners) == 4 else None
            if vision.board_corners is not None:
                vision.calculate_cell_centers()

            vision.save_calibration()
            print("\n✓ Calibration saved successfully!")

            # Print summary
            print("\nCalibration Summary:")
            print(f"  Blue HSV: [{blue_h_min}, {blue_s_min}, {blue_v_min}] to [{blue_h_max}, {blue_s_max}, {blue_v_max}]")
            print(f"  Red HSV: [{red_h_min}, {red_s_min}, {red_v_min}] to [{red_h_max}, {red_s_max}, {red_v_max}]")
            if vision.board_corners is not None:
                print(f"  Board corners: {len(selected_corners)} corners defined")
            else:
                print(f"  Board corners: NOT SET (need 4 corners)")

    vision.close_camera()
    cv2.destroyAllWindows()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    calibrate()
