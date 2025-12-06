# Vision System - Quick Start Guide

## Enable Vision Detection for Blue Pieces

Follow these steps to have the camera automatically detect when you place blue pieces on the board.

## Step 1: Calibrate Camera (One-Time Setup)

If you haven't calibrated yet:

```bash
python calibrate_camera.py
```

**Calibration Steps:**

1. **Color Calibration:**
   - Place a **blue piece** on the board
   - Adjust blue HSV trackbars until piece is detected (white in mask window)
   - Press **'b'** to switch to blue mode
   - Place a **red piece** on the board
   - Adjust red HSV trackbars until piece is detected
   - Press **'r'** to switch to red mode

2. **Board Calibration:**
   - Press **'c'** to start corner selection
   - Click 4 corners in order:
     1. Top-Left (position 0)
     2. Top-Right (position 2)
     3. Bottom-Right (position 8)
     4. Bottom-Left (position 6)
   - Press **'s'** to save

✅ Calibration saved to `board_calibration.json`

## Step 2: Start Web Server

```bash
python web_server.py
```

Wait for:
```
Initializing Dobot...
Dobot ready (home position not set - call /api/home to home the device)
 * Running on http://0.0.0.0:5000
```

## Step 3: Enable Vision Monitoring

**Option A: Use Helper Script (Easiest)**

Open a NEW terminal (keep web server running) and run:

```bash
python enable_vision.py
```

Select option **1** to enable vision.

**Option B: Manual API Call**

In a new terminal:

```bash
curl -X POST http://localhost:5000/api/vision/toggle -H "Content-Type: application/json" -d "{\"enable\": true}"
```

**Option C: Enable in Python**

```python
import requests
requests.post('http://localhost:5000/api/vision/toggle',
              json={'enable': True})
```

## Step 4: Start Playing with Vision

1. **Open browser:** http://localhost:5000
2. **Select Blue** (your color)
3. **Physically place** a blue piece on the board
4. **Camera detects** your move automatically
5. **Robot responds** by placing its red piece
6. **Repeat** until game ends

## How Vision Works

```
You place blue piece on board
        ↓
Camera captures frame (2x per second)
        ↓
Vision detects blue piece location
        ↓
Maps location to grid cell (0-8)
        ↓
Registers move in game
        ↓
GUI updates automatically
        ↓
Robot calculates response
        ↓
Robot places red piece
```

## Verification Checklist

Before playing with vision, verify:

- [ ] Calibration file exists: `board_calibration.json`
- [ ] Web server is running
- [ ] Vision is enabled (check with `enable_vision.py` option 3)
- [ ] Camera has clear view of entire board
- [ ] Lighting is consistent
- [ ] Blue pieces are clearly visible

## Testing Vision Detection

**Test 1: Check Vision Status**

```bash
python enable_vision.py
# Select option 3
```

Should show:
```
Vision enabled: True
Calibration file exists: True
```

**Test 2: Live Vision Test**

```bash
python test_vision_live.py
```

- Place blue piece on board
- Should see detection overlay
- Press **'d'** to print board state
- Should show 'B' where blue piece is

**Test 3: Watch Console**

In the web server terminal, you should see:
```
Vision monitoring active - watching for human moves...
Vision detected human move at position 4
```

## Troubleshooting

### Vision Not Detecting Pieces

**Problem:** Blue pieces not detected

**Solutions:**
1. Check calibration is loaded:
   ```bash
   python enable_vision.py  # option 3
   ```

2. Test detection manually:
   ```bash
   python test_vision_live.py
   ```

3. Re-calibrate if needed:
   ```bash
   python calibrate_camera.py
   ```

4. Check console for errors in web server terminal

### Vision Detecting Wrong Positions

**Problem:** Pieces detected in wrong cells

**Solutions:**
1. Re-calibrate board corners:
   ```bash
   python calibrate_camera.py
   # Press 'c' and click corners carefully
   ```

2. Ensure camera hasn't moved since calibration

3. Check grid overlay in test:
   ```bash
   python test_vision_live.py
   # Press 'g' to toggle grid
   ```

### Multiple Detections

**Problem:** One piece detected multiple times or in multiple cells

**Solutions:**
1. Increase minimum area threshold
2. Improve lighting (reduce shadows)
3. Ensure pieces are solid color
4. Check vision monitoring frequency (currently 2 Hz)

### Vision Not Enabled

**Problem:** Manual clicks still required

**Solution:**
```bash
# Check status
python enable_vision.py  # option 3

# If disabled, enable it
python enable_vision.py  # option 1
```

## Console Output Examples

### When Vision Detects Move:

```
Vision monitoring active - watching for human moves...
Vision detected human move at position 4
Robot's turn...
Robot chooses position 0
Picking up red piece from storage...
Placing piece at position 0...
```

### When Vision is Working:

```
✓ Vision system ready
Vision monitoring started
Camera 1 opened successfully
Vision monitoring active - watching for human moves...
```

### If Vision Fails:

```
✗ Failed to open camera for vision monitoring
# OR
Warning: No calibration found. Vision may not work correctly.
Run calibrate_camera.py to calibrate the system.
```

## Game Flow with Vision

### Complete Game Example:

1. **Start web server:**
   ```bash
   python web_server.py
   ```

2. **Enable vision:**
   ```bash
   python enable_vision.py  # option 1
   ```

3. **Open GUI:** http://localhost:5000

4. **Click "Blue (You)"**
   - Vision monitoring begins
   - You go first (blue always starts)

5. **Place blue piece on position 4 (center)**
   - Camera detects within 0.5 seconds
   - GUI updates automatically
   - Console shows: "Vision detected human move at position 4"

6. **Robot's turn:**
   - Calculates best move
   - Picks up red piece
   - Places on board
   - GUI updates

7. **Place second blue piece**
   - Camera detects again
   - Robot responds
   - Continue until win/lose/tie

8. **Reset and play again**
   - Click "Reset Game"
   - Vision continues monitoring
   - Start new game

## Advanced: Vision Configuration

### Change Detection Frequency

In `web_server.py`, vision_monitor_loop:
```python
time.sleep(0.5)  # Default: check 2x per second
time.sleep(0.25) # Faster: check 4x per second
time.sleep(1.0)  # Slower: check 1x per second
```

### Change Camera Index

In `vision_system.py`:
```python
def __init__(self, camera_index=1):  # Try 0, 1, 2, etc.
```

### Adjust Color Sensitivity

Re-run calibration with different HSV values:
```bash
python calibrate_camera.py
```

## Quick Reference Commands

| Task | Command |
|------|---------|
| Calibrate camera | `python calibrate_camera.py` |
| Enable vision | `python enable_vision.py` (option 1) |
| Disable vision | `python enable_vision.py` (option 2) |
| Check status | `python enable_vision.py` (option 3) |
| Test detection | `python test_vision_live.py` |
| Start server | `python web_server.py` |

## Files Involved

- `vision_system.py` - Core vision detection
- `board_calibration.json` - Saved calibration data
- `calibrate_camera.py` - Calibration tool
- `test_vision_live.py` - Live testing tool
- `enable_vision.py` - Vision control script
- `web_server.py` - Vision monitoring thread

## Next Steps

Once vision is working:
1. ✓ Play a complete game using only physical pieces
2. ✓ Test with different lighting conditions
3. ✓ Adjust calibration if needed
4. Consider adding GUI toggle for vision on/off
5. Consider adding visual feedback when move is detected

## Support

If vision isn't working after following this guide:

1. Check all steps completed
2. Review console output for errors
3. Test components individually:
   - Camera: `python test_vision_live.py`
   - Calibration: `python calibrate_camera.py`
   - Vision status: `python enable_vision.py`
4. Ensure all dependencies installed: `pip install -r requirements.txt`
5. Check camera is not used by another program
