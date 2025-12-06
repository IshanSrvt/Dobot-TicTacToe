# Computer Vision System for Tic-Tac-Toe Robot

This guide explains how to set up and use the computer vision system to automatically detect human moves on the physical game board.

## Overview

The vision system uses a camera to:
1. Detect blue and red game pieces on the board
2. Map their positions to the 3x3 grid
3. Automatically register human moves without manual input
4. Trigger the robot to respond

## Prerequisites

- Camera (USB webcam or built-in camera)
- Consistent lighting conditions
- Blue and red game pieces with distinct colors
- Physical game board clearly visible to camera

## Setup Process

### Step 1: Camera Calibration

Before using the vision system, you must calibrate it for your specific setup.

```bash
python calibrate_camera.py
```

#### Part A: Color Calibration

1. Place a **blue piece** on the board where the camera can see it
2. Use the trackbars to adjust HSV values until the blue piece is clearly detected:
   - `Blue H Min/Max`: Hue range (color)
   - `Blue S Min/Max`: Saturation range (color intensity)
   - `Blue V Min/Max`: Value range (brightness)
3. Press **'b'** to test blue detection
4. Repeat for a **red piece** using the red trackbars
5. Press **'r'** to test red detection

**Tips for color calibration:**
- Start with default values and adjust minimally
- Watch the "Mask" window - white areas show what's detected
- Avoid detecting shadows or background objects
- Test with multiple pieces to ensure consistency

#### Part B: Board Corner Calibration

1. Press **'c'** to enter corner selection mode
2. Click on the 4 corners of your game board in this exact order:
   - **Top-Left** corner (position 0)
   - **Top-Right** corner (position 2)
   - **Bottom-Right** corner (position 8)
   - **Bottom-Left** corner (position 6)
3. Green circles will mark each selected corner
4. Press **'s'** to **SAVE** the calibration

The calibration is saved to `board_calibration.json`.

### Step 2: Test Vision System

Test the vision system before using it in a game:

```bash
python vision_system.py
```

This opens a test window showing:
- Detected blue and red pieces
- Cell numbers (0-8)
- Grid overlay

**Keyboard commands:**
- **'d'**: Detect and print current board state
- **'s'**: Save current camera frame
- **'q'**: Quit

### Step 3: Enable Vision in Web Server

The vision system integrates with the web server automatically.

#### Option 1: Enable at Game Start (via GUI - Future Feature)
The GUI will have a toggle to enable vision when starting a game.

#### Option 2: Enable via API

```bash
# Enable vision
curl -X POST http://localhost:5000/api/vision/toggle \
  -H "Content-Type: application/json" \
  -d '{"enable": true}'

# Disable vision
curl -X POST http://localhost:5000/api/vision/toggle \
  -H "Content-Type: application/json" \
  -d '{"enable": false}'

# Check vision status
curl http://localhost:5000/api/vision/status
```

#### Option 3: Enable in Game Start Request

Modify the start game request to include vision:

```javascript
fetch('http://localhost:5000/api/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    human_color: 'blue',
    use_vision: true  // Enable vision
  })
})
```

## How It Works

### Game Flow with Vision Enabled

1. **Game starts**: Vision monitoring thread begins
2. **Human's turn**: Camera continuously monitors the board
3. **Move detected**: When a new piece appears in the human's color:
   - Position is automatically registered
   - GUI is updated via WebSocket
   - Robot calculates its response
4. **Robot's turn**: Vision monitoring pauses during robot movement
5. **Repeat** until game ends

### Technical Details

The vision system runs in a separate thread and:
- Captures frames at 2 Hz (twice per second)
- Compares current board state with game state
- Detects new pieces by color and position
- Maps physical positions to grid cells (0-8)
- Only registers moves in the human's color

## Troubleshooting

### Pieces Not Detected

**Problem**: Blue or red pieces aren't being detected

**Solutions**:
1. Re-run calibration (`calibrate_camera.py`)
2. Adjust HSV ranges for your lighting conditions
3. Ensure pieces are fully visible to camera
4. Check that pieces are solid colored (not reflective/shiny)
5. Improve lighting - avoid shadows and glare

### Wrong Cell Detection

**Problem**: Pieces detected in wrong grid positions

**Solutions**:
1. Re-calibrate board corners (`calibrate_camera.py`)
2. Ensure camera isn't moved after calibration
3. Click corners more precisely during calibration
4. Make sure board is flat and parallel to camera view

### False Detections

**Problem**: System detects pieces that aren't there

**Solutions**:
1. Increase minimum area threshold in `vision_system.py`:
   ```python
   MIN_PIECE_AREA = 200  # Increase from 100
   ```
2. Narrow HSV color ranges in calibration
3. Remove colored objects from camera view
4. Improve lighting consistency

### Camera Not Opening

**Problem**: "Failed to open camera" error

**Solutions**:
1. Check camera is connected
2. Try different camera index:
   ```python
   vision = TicTacToeVision(camera_index=1)  # or 2, 3, etc.
   ```
3. Close other applications using the camera
4. Check camera permissions in Windows settings

### Vision Monitoring Not Starting

**Problem**: Vision enabled but moves not detected

**Solutions**:
1. Check calibration file exists: `board_calibration.json`
2. Run `python calibrate_camera.py` to create calibration
3. Check console for error messages
4. Verify camera has clear view of entire board

## Configuration Files

### board_calibration.json

Contains calibration data:
```json
{
  "blue_lower": [90, 50, 50],
  "blue_upper": [130, 255, 255],
  "red_lower": [0, 50, 50],
  "red_upper": [10, 255, 255],
  "board_corners": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
}
```

### vision_system.py Configuration

Key parameters you can adjust:

```python
# Minimum contour area to be considered a piece
MIN_PIECE_AREA = 100

# HSV color ranges (adjusted during calibration)
DEFAULT_BLUE_HSV_LOWER = np.array([90, 50, 50])
DEFAULT_BLUE_HSV_UPPER = np.array([130, 255, 255])

DEFAULT_RED_HSV_LOWER = np.array([0, 50, 50])
DEFAULT_RED_HSV_UPPER = np.array([10, 255, 255])
```

### web_server.py Configuration

Vision monitoring settings:

```python
# Monitoring frequency (in vision_monitor_loop)
time.sleep(0.5)  # Check twice per second

# Maximum distance from cell center to map position
# (in map_point_to_cell function)
if distances[nearest_cell] > 100:  # pixels
```

## Best Practices

### Camera Setup
- **Position**: Mount camera directly above board, facing down
- **Height**: 30-50cm above board (adjust to fit entire board in frame)
- **Angle**: Keep camera parallel to board (avoid tilted view)
- **Stability**: Secure camera so it doesn't move during game

### Lighting
- Use consistent, diffuse lighting (avoid direct spotlights)
- Minimize shadows on the board
- Avoid backlighting or glare
- Test in the same lighting conditions you'll use for games

### Game Pieces
- Use solid, opaque colored pieces
- Avoid reflective or translucent materials
- Ensure pieces are clearly blue/red (not purple, orange, etc.)
- Keep pieces the same size and shape

### Calibration
- Calibrate each time you move the camera
- Re-calibrate if lighting changes significantly
- Save calibration for your setup
- Test detection before starting a game

## Advanced Features

### Custom Color Detection

To use different colors (e.g., green and yellow):

1. Modify HSV ranges in `vision_system.py`
2. Add new color detection in `detect_color()` method
3. Update game logic to use new color names

### Multiple Camera Support

To use multiple cameras for better coverage:

1. Initialize multiple `TicTacToeVision` instances
2. Use different camera indices
3. Combine detections from all cameras
4. Choose position with highest confidence

### Debug Visualization

Enable real-time visualization during gameplay:

```python
# In vision_monitor_loop, add:
viz_frame = vision_system.visualize_detection(frame)
cv2.imshow('Vision Debug', viz_frame)
cv2.waitKey(1)
```

## API Reference

### Vision System Class

```python
from vision_system import TicTacToeVision

# Initialize
vision = TicTacToeVision(camera_index=0)

# Calibration
vision.save_calibration()
vision.load_calibration()

# Detection
board_state = vision.detect_board_state()  # Returns list of 9 colors
new_move = vision.detect_new_move(previous_state)  # Returns (position, color)

# Visualization
frame = vision.capture_frame()
viz = vision.visualize_detection(frame)
```

### Web Server Endpoints

```
POST /api/vision/toggle
  Body: {"enable": true/false}
  Enable or disable vision monitoring

GET /api/vision/status
  Returns: {"vision_enabled": bool, "calibration_exists": bool}
  Check vision system status
```

## Next Steps

Once vision is working:

1. ✓ Test with manual piece placement
2. ✓ Play a complete game using vision
3. ✓ Verify robot responds correctly to detected moves
4. Consider adding GUI toggle for vision enable/disable
5. Add confidence scoring for detections
6. Implement move verification (ask human to confirm ambiguous moves)

## Support

If you encounter issues:
1. Check console output for error messages
2. Verify calibration file exists and is valid
3. Test each component separately (camera, detection, server)
4. Review troubleshooting section above
5. Ensure all dependencies are installed (`requirements.txt`)
