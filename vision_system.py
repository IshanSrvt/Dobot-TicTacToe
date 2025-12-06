"""
Computer Vision System for Tic-Tac-Toe Board Detection
Detects blue and red pieces on a 3x3 game board using a camera
"""

import cv2
import numpy as np
import json
import os
from typing import List, Tuple, Optional, Dict

# ============================================================================
# CONFIGURATION
# ============================================================================

# File to store calibration data
CALIBRATION_FILE = "board_calibration.json"

# Default HSV color ranges (these will be adjusted during calibration)
DEFAULT_BLUE_HSV_LOWER = np.array([90, 50, 50])
DEFAULT_BLUE_HSV_UPPER = np.array([130, 255, 255])

DEFAULT_RED_HSV_LOWER = np.array([0, 50, 50])
DEFAULT_RED_HSV_UPPER = np.array([10, 255, 255])

# Alternative red range (wraps around hue)
RED_HSV_LOWER_ALT = np.array([170, 50, 50])
RED_HSV_UPPER_ALT = np.array([180, 255, 255])

# Minimum contour area to be considered a game piece
MIN_PIECE_AREA = 100

# ============================================================================
# VISION SYSTEM CLASS
# ============================================================================

class TicTacToeVision:
    """Computer vision system for detecting game pieces on the board"""

    def __init__(self, camera_index=1):
        """
        Initialize the vision system.

        Args:
            camera_index: Camera device index (default 0)
        """
        self.camera_index = camera_index
        self.cap = None
        self.calibration_data = None

        # Color ranges (HSV)
        self.blue_lower = DEFAULT_BLUE_HSV_LOWER
        self.blue_upper = DEFAULT_BLUE_HSV_UPPER
        self.red_lower = DEFAULT_RED_HSV_LOWER
        self.red_upper = DEFAULT_RED_HSV_UPPER

        # Board corners (will be set during calibration)
        self.board_corners = None  # [top_left, top_right, bottom_right, bottom_left]

        # Grid cell centers (calculated from board corners)
        self.cell_centers = None

        # Load calibration if it exists
        self.load_calibration()

    def open_camera(self) -> bool:
        """Open the camera connection"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return False
        print(f"Camera {self.camera_index} opened successfully")
        return True

    def close_camera(self):
        """Close the camera connection"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera.

        Returns:
            Frame as numpy array, or None if capture failed
        """
        if self.cap is None or not self.cap.isOpened():
            if not self.open_camera():
                return None

        ret, frame = self.cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            return None

        return frame

    def save_calibration(self):
        """Save calibration data to file"""
        data = {
            'blue_lower': self.blue_lower.tolist(),
            'blue_upper': self.blue_upper.tolist(),
            'red_lower': self.red_lower.tolist(),
            'red_upper': self.red_upper.tolist(),
            'board_corners': self.board_corners.tolist() if self.board_corners is not None else None
        }

        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Calibration saved to {CALIBRATION_FILE}")

    def load_calibration(self) -> bool:
        """
        Load calibration data from file.

        Returns:
            True if calibration loaded successfully
        """
        if not os.path.exists(CALIBRATION_FILE):
            print("No calibration file found. Please run calibration first.")
            return False

        try:
            with open(CALIBRATION_FILE, 'r') as f:
                data = json.load(f)

            self.blue_lower = np.array(data['blue_lower'])
            self.blue_upper = np.array(data['blue_upper'])
            self.red_lower = np.array(data['red_lower'])
            self.red_upper = np.array(data['red_upper'])

            if data['board_corners'] is not None:
                self.board_corners = np.array(data['board_corners'])
                self.calculate_cell_centers()

            print("Calibration loaded successfully")
            return True

        except Exception as e:
            print(f"Error loading calibration: {e}")
            return False

    def calculate_cell_centers(self):
        """Calculate the center points of each cell in the 3x3 grid"""
        if self.board_corners is None:
            return

        # Get board corners
        tl, tr, br, bl = self.board_corners

        # Calculate grid points
        self.cell_centers = []
        for row in range(3):
            for col in range(3):
                # Interpolate position in grid
                # Calculate position as fraction (1/6, 3/6, 5/6 for centers)
                row_frac = (row + 0.5) / 3
                col_frac = (col + 0.5) / 3

                # Interpolate between corners
                top = tl + (tr - tl) * col_frac
                bottom = bl + (br - bl) * col_frac
                center = top + (bottom - top) * row_frac

                self.cell_centers.append(center)

        self.cell_centers = np.array(self.cell_centers)

    def detect_color(self, frame: np.ndarray, color: str) -> List[np.ndarray]:
        """
        Detect pieces of a specific color in the frame.

        Args:
            frame: Input frame (BGR)
            color: 'blue' or 'red'

        Returns:
            List of contours for detected pieces
        """
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask based on color
        if color == 'blue':
            mask = cv2.inRange(hsv, self.blue_lower, self.blue_upper)
        elif color == 'red':
            # Red can wrap around hue, so use two ranges
            mask1 = cv2.inRange(hsv, self.red_lower, self.red_upper)
            mask2 = cv2.inRange(hsv, RED_HSV_LOWER_ALT, RED_HSV_UPPER_ALT)
            mask = cv2.bitwise_or(mask1, mask2)
        else:
            return []

        # Morphological operations to clean up noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter by minimum area
        filtered_contours = [c for c in contours if cv2.contourArea(c) > MIN_PIECE_AREA]

        return filtered_contours

    def get_contour_center(self, contour: np.ndarray) -> Tuple[int, int]:
        """Get the center point of a contour"""
        M = cv2.moments(contour)
        if M['m00'] == 0:
            return None
        cx = int(M['m10'] / M['m00'])
        cy = int(M['m01'] / M['m00'])
        return (cx, cy)

    def map_point_to_cell(self, point: Tuple[int, int]) -> Optional[int]:
        """
        Map a point to the nearest cell (0-8).

        Args:
            point: (x, y) coordinate

        Returns:
            Cell index 0-8, or None if out of bounds
        """
        if self.cell_centers is None:
            return None

        point = np.array(point)
        distances = np.linalg.norm(self.cell_centers - point, axis=1)
        nearest_cell = np.argmin(distances)

        # Check if point is reasonably close to a cell
        # (avoid mapping pieces outside the board)
        if distances[nearest_cell] > 100:  # Max distance threshold
            return None

        return int(nearest_cell)

    def detect_board_state(self) -> Optional[List[Optional[str]]]:
        """
        Detect the current state of the game board.

        Returns:
            List of 9 values: 'blue', 'red', or None for each cell (0-8)
            Returns None if detection failed
        """
        frame = self.capture_frame()
        if frame is None:
            return None

        if self.cell_centers is None:
            print("Error: Board not calibrated. Run calibration first.")
            return None

        # Initialize board state (all empty)
        board_state = [None] * 9

        # Detect blue pieces
        blue_contours = self.detect_color(frame, 'blue')
        for contour in blue_contours:
            center = self.get_contour_center(contour)
            if center is not None:
                cell = self.map_point_to_cell(center)
                if cell is not None:
                    board_state[cell] = 'blue'

        # Detect red pieces
        red_contours = self.detect_color(frame, 'red')
        for contour in red_contours:
            center = self.get_contour_center(contour)
            if center is not None:
                cell = self.map_point_to_cell(center)
                if cell is not None:
                    board_state[cell] = 'red'

        return board_state

    def detect_new_move(self, previous_state: List[Optional[str]]) -> Optional[Tuple[int, str]]:
        """
        Detect a new move by comparing current state to previous state.

        Args:
            previous_state: Previous board state (list of 9 values)

        Returns:
            Tuple of (position, color) for new move, or None if no new move
        """
        current_state = self.detect_board_state()
        if current_state is None:
            return None

        # Find differences
        for i in range(9):
            if previous_state[i] is None and current_state[i] is not None:
                return (i, current_state[i])

        return None

    def visualize_detection(self, frame: np.ndarray, draw_grid=True) -> np.ndarray:
        """
        Draw visualization overlay on frame.

        Args:
            frame: Input frame
            draw_grid: Whether to draw grid lines and cell numbers

        Returns:
            Frame with visualization overlay
        """
        output = frame.copy()

        # Draw board corners
        if self.board_corners is not None:
            corners = self.board_corners.astype(int)
            for i in range(4):
                cv2.circle(output, tuple(corners[i]), 10, (0, 255, 0), -1)
                cv2.line(output, tuple(corners[i]), tuple(corners[(i+1) % 4]), (0, 255, 0), 2)

        # Draw cell centers and grid
        if self.cell_centers is not None and draw_grid:
            for i, center in enumerate(self.cell_centers):
                cx, cy = int(center[0]), int(center[1])
                cv2.circle(output, (cx, cy), 5, (255, 255, 0), -1)
                cv2.putText(output, str(i), (cx+10, cy+10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Detect and draw pieces
        blue_contours = self.detect_color(frame, 'blue')
        cv2.drawContours(output, blue_contours, -1, (255, 0, 0), 2)
        for contour in blue_contours:
            center = self.get_contour_center(contour)
            if center:
                cv2.circle(output, center, 8, (255, 0, 0), -1)
                cell = self.map_point_to_cell(center)
                if cell is not None:
                    cv2.putText(output, f"Blue-{cell}", (center[0]+15, center[1]),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        red_contours = self.detect_color(frame, 'red')
        cv2.drawContours(output, red_contours, -1, (0, 0, 255), 2)
        for contour in red_contours:
            center = self.get_contour_center(contour)
            if center:
                cv2.circle(output, center, 8, (0, 0, 255), -1)
                cell = self.map_point_to_cell(center)
                if cell is not None:
                    cv2.putText(output, f"Red-{cell}", (center[0]+15, center[1]),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        return output

# ============================================================================
# STANDALONE TESTING
# ============================================================================

def main():
    """Test the vision system"""
    vision = TicTacToeVision()

    if not vision.open_camera():
        return

    print("\nVision System Test")
    print("=" * 50)
    print("Press 'q' to quit")
    print("Press 's' to save current frame")
    print("Press 'd' to detect and print board state")
    print("=" * 50)

    while True:
        frame = vision.capture_frame()
        if frame is None:
            break

        # Show visualization
        viz_frame = vision.visualize_detection(frame)
        cv2.imshow('Vision System Test', viz_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite('captured_frame.jpg', frame)
            print("Frame saved to captured_frame.jpg")
        elif key == ord('d'):
            board_state = vision.detect_board_state()
            print("\nCurrent board state:")
            for i in range(3):
                row = board_state[i*3:(i+1)*3]
                row_str = [cell if cell else '.' for cell in row]
                print(f"  {' '.join(row_str)}")

    vision.close_camera()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
