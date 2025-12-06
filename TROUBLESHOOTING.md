# Troubleshooting Guide - Dobot Not Moving

## Debug Features Added

### 1. Real-Time Camera Window
When vision is enabled, a debug window will open showing:
- Live camera feed
- Detected pieces (blue/red contours)
- Grid overlay with cell numbers
- Current game status

### 2. Detailed Console Logging
The console now shows detailed debug information:
```
DEBUG: robot_turn() called
DEBUG: Robot thinking...
DEBUG: Robot chose position 4
DEBUG: Starting physical robot movement to position 4
DEBUG: Calling robot_make_move(4)
DEBUG: robot_make_move - Starting move to position 4
DEBUG: robot_make_move - Robot color: red
DEBUG: robot_make_move - Pieces remaining: {'blue': 5, 'red': 5}
DEBUG: robot_make_move - Calling pickup_piece(red)
Picking up red piece from storage...
DEBUG: robot_make_move - Calling place_piece(4)
Placing piece at position 4...
DEBUG: robot_make_move - Move complete!
```

## Common Issues & Solutions

### Issue 1: Dobot Not Moving At All

**Symptoms:**
- Game progresses but robot doesn't move
- No errors in console
- Console shows "DEBUG: robot_turn() called" but nothing happens

**Diagnosis Steps:**

1. **Check if `device` is initialized:**
   Look for this line in console when server starts:
   ```
   Initializing Dobot...
   Dobot initialized successfully
   Dobot ready
   ```

   If you see:
   ```
   ERROR: Dobot device is None! Robot cannot move.
   ```
   The device wasn't initialized.

2. **Check console output:**
   When robot's turn comes, you should see:
   ```
   DEBUG: robot_turn() called
   DEBUG: Robot thinking...
   DEBUG: Robot chose position X
   DEBUG: Starting physical robot movement
   ```

   If you DON'T see these messages, the robot_turn function isn't being called.

3. **Check if Dobot responds to commands:**
   The console should show:
   ```
   Picking up red piece from storage...
   Placing piece at position X...
   ```

**Solutions:**

**A. Device Not Initialized:**
```python
# Check in Python console:
from Python_Dobot_3T import device
print(device)  # Should NOT be None
```

If None, manually initialize:
```python
from Python_Dobot_3T import initialize_dobot
device = initialize_dobot(port="COM4", home_on_init=True)
```

**B. Commands Not Executing:**
The issue was `wait=True` parameter which we fixed. Verify the fix is in place:
```bash
# Check Python_Dobot_3T.py for correct pattern
grep -n "wait_for_cmd" Python_Dobot_3T.py
```

Should see multiple lines like:
```python
cmd_id = device.move_to(x, y, z, 0)
device.wait_for_cmd(cmd_id)
```

### Issue 2: Vision Not Detecting Pieces

**Symptoms:**
- Camera window shows feed
- Blue pieces visible but not detected
- No contours drawn around pieces

**Diagnosis Steps:**

1. **Check calibration exists:**
   ```bash
   dir board_calibration.json
   ```

2. **Check detection in real-time:**
   - Look at the camera debug window
   - Blue pieces should have blue contours
   - Red pieces should have red contours
   - Cell numbers should overlay grid

3. **Check console for detection:**
   ```
   DEBUG: Detected state: [None, None, 'blue', None, None, None, None, None, None]
   ```

**Solutions:**

**A. No Calibration:**
```bash
python calibrate_camera.py
# Calibrate colors and corners
# Press 's' to save
```

**B. Poor Detection:**
```bash
# Test detection separately
python test_vision_live.py
# Press 'd' to see what's detected
```

Adjust HSV ranges if needed.

**C. Wrong Camera:**
Change camera index in vision_system.py:
```python
def __init__(self, camera_index=0):  # Try 0, 1, 2
```

### Issue 3: Robot Turn Not Triggering

**Symptoms:**
- Human move registered
- No robot response
- Console doesn't show "DEBUG: robot_turn() called"

**Diagnosis:**

Check if robot_turn is called after human move:
- Manual move (GUI click): Should trigger immediately
- Vision move: Should trigger after detection

**Solutions:**

**A. Check GUI Move Handler:**
Look for in console:
```
DEBUG: robot_turn() called
```

If missing, check that the `/api/move/human` endpoint calls `robot_turn()`.

**B. Check Vision Detection:**
Console should show:
```
Vision detected human move at position X
DEBUG: robot_turn() called
```

If only first line appears, check vision_monitor_loop triggers robot_turn.

### Issue 4: Camera Window Not Opening

**Symptoms:**
- Vision enabled
- No camera window appears
- Console says "Vision monitoring active"

**Solutions:**

**A. Check OpenCV Installation:**
```python
import cv2
print(cv2.__version__)  # Should show version number
```

**B. Camera in Use:**
Close other apps using camera (Zoom, Teams, etc.)

**C. Manual Window Check:**
```bash
python test_vision_live.py
# Should open window immediately
```

## Step-by-Step Debug Process

### Step 1: Verify Dobot Connection

```bash
python test_connection.py
# Select 'y' to test Dobot
```

Expected output:
```
✓ Dobot connected successfully
Current position: x=... y=... z=...
```

### Step 2: Test Robot Movement Directly

```bash
python Python_Dobot_3T.py
# Select option 3 (Test pickup/place)
```

Robot should physically move and pick/place pieces.

If this works → Problem is in web server integration
If this fails → Problem is in Dobot control code

### Step 3: Check Web Server Console

Start web server and look for:
```
Initializing Dobot...
Dobot initialized successfully
 * Running on http://0.0.0.0:5000
```

### Step 4: Enable Vision and Check Camera

```bash
python enable_vision.py
# Option 1
```

Expected:
```
✓ Vision monitoring enabled
Vision enabled: True
Calibration file exists: True
```

Camera window should appear showing live feed.

### Step 5: Make Test Move

**Option A: GUI Click**
1. Open http://localhost:5000
2. Click Blue
3. Click a cell
4. Watch console for DEBUG messages

**Option B: Physical Piece**
1. Enable vision
2. Start game (click Blue)
3. Place blue piece on board
4. Watch camera window for detection
5. Watch console for DEBUG messages

### Step 6: Analyze Console Output

**Expected flow:**
```
DEBUG: robot_turn() called
DEBUG: Robot thinking...
DEBUG: Robot chose position 4
DEBUG: Starting physical robot movement to position 4
DEBUG: Calling robot_make_move(4)
DEBUG: robot_make_move - Starting move to position 4
DEBUG: robot_make_move - Robot color: red
DEBUG: robot_make_move - Calling pickup_piece(red)
Picking up red piece from storage...
[Physical movement happens here]
DEBUG: robot_make_move - Calling place_piece(4)
Placing piece at position 4...
[Physical movement happens here]
DEBUG: robot_make_move - Move complete!
```

**Find where it stops:**
- Stops at "robot_turn() called" → Function not completing
- Stops at "Calling robot_make_move" → robot_make_move failing
- Stops at "Calling pickup_piece" → Dobot commands failing
- Shows all messages but no movement → `wait_for_cmd` issue

## Console Message Reference

### Normal Operation:
```
✓ Dobot initialized successfully
✓ Vision monitoring enabled
✓ Vision monitoring active
✓ Camera window opened
✓ DEBUG: Detected state: [...]
✓ Vision detected human move
✓ DEBUG: robot_turn() called
✓ DEBUG: Robot chose position X
✓ Picking up [color] piece
✓ Placing piece at position X
```

### Error Indicators:
```
✗ ERROR: Dobot device is None
✗ Failed to open camera
✗ No calibration found
✗ DEBUG: No board state detected
✗ No valid moves available
✗ Failed to capture frame
```

## Quick Fixes

### Fix 1: Restart Everything
```bash
# Stop web server (Ctrl+C)
# Restart web server
python web_server.py

# Re-enable vision
python enable_vision.py  # option 1
```

### Fix 2: Reinitialize Dobot
```bash
# In Python console while server running:
from Python_Dobot_3T import initialize_dobot
initialize_dobot(port="COM4", home_on_init=True)
```

### Fix 3: Re-calibrate Vision
```bash
python calibrate_camera.py
# Re-do calibration
# Press 's' to save
```

### Fix 4: Check File Permissions
```bash
# Ensure files are not read-only
# Check board_calibration.json is writable
```

## Still Not Working?

If Dobot still won't move after all debug steps:

1. **Capture console output:**
   - Start fresh server
   - Make one move
   - Copy ALL console output

2. **Check specific error:**
   - Look for "ERROR:" messages
   - Look for Python tracebacks
   - Note where DEBUG messages stop

3. **Verify hardware:**
   - Dobot powered on
   - USB connected
   - Correct COM port
   - Dobot not in error state (check lights)

4. **Test components separately:**
   - Test Dobot: `python test_connection.py`
   - Test vision: `python test_vision_live.py`
   - Test game logic: `python Python_Dobot_3T.py`

## Debug Checklist

Before reporting issue, verify:
- [ ] Dobot powers on and connects
- [ ] `test_connection.py` passes
- [ ] Console shows "Dobot initialized successfully"
- [ ] Console shows DEBUG messages
- [ ] Camera window appears (if vision enabled)
- [ ] Calibration file exists
- [ ] All files have latest fixes
- [ ] No Python errors in console

## Contact Information

Include this info when asking for help:
- Console output (full log)
- Which step fails
- Error messages
- Dobot model and COM port
- Camera type and index
- Python version
- OS (Windows/Linux/Mac)
