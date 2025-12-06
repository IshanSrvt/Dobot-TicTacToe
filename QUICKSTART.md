# Tic-Tac-Toe Robot - Quick Start Guide

Complete setup guide to get your Tic-Tac-Toe robot working with computer vision.

## 🚀 Quick Setup (5 Steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Dobot Connection

```bash
python test_connection.py
```

Select 'y' to test Dobot connection. Should see:
```
✓ Dobot connected successfully
Current position: x=... y=... z=...
```

### 3. Calibrate Camera (First Time Only)

```bash
python calibrate_camera.py
```

**Color Calibration:**
- Place blue piece on board
- Adjust trackbars until blue piece is detected
- Press 'b' to switch to blue mode
- Place red piece on board
- Adjust trackbars until red piece is detected
- Press 'r' to switch to red mode

**Board Calibration:**
- Press 'c' for corner selection
- Click 4 corners: Top-Left → Top-Right → Bottom-Right → Bottom-Left
- Press 's' to save

### 4. Start Web Server

```bash
python web_server.py
```

### 5. Open GUI in Browser

```
http://localhost:5000
```

## 🎮 Playing Without Vision (Manual Mode)

1. Open `http://localhost:5000`
2. Click color button (Blue or Red)
3. Click cells on GUI to make your moves
4. Robot automatically responds
5. Click "Reset Game" to play again

## 👁️ Playing With Vision (Automatic Detection)

### Method 1: Enable via API Before Game

```bash
# In another terminal
curl -X POST http://localhost:5000/api/vision/toggle \
  -H "Content-Type: application/json" \
  -d '{"enable": true}'
```

Then start game normally in GUI.

### Method 2: Future GUI Toggle

A toggle button will be added to the GUI to enable/disable vision.

### How Vision Works

1. Start game by selecting color
2. **Place your colored piece** physically on the board
3. Camera detects the move automatically
4. GUI updates to show your move
5. Robot calculates and executes its move
6. Repeat until game ends

## 📁 File Structure

```
PythonDobot/
├── Python_Dobot_3T.py          # Main game logic and Dobot control
├── Python_Dobot_setup.py       # Dobot hardware interface
├── web_server.py               # Flask server (GUI ↔ Robot bridge)
├── GUI_for_3T.html             # Web-based user interface
├── vision_system.py            # Computer vision detection
├── calibrate_camera.py         # Interactive calibration tool
├── test_connection.py          # System verification script
├── requirements.txt            # Python dependencies
├── board_calibration.json      # Camera calibration data (generated)
├── README_WEB_GUI.md          # Web server documentation
├── README_VISION.md           # Vision system documentation
└── QUICKSTART.md              # This file
```

## 🔧 Configuration

### Dobot COM Port

If your Dobot is on a different port, edit these files:

**Python_Dobot_3T.py** (line 42):
```python
device = Dobot(port="COM4")  # Change to your COM port
```

**test_connection.py** (line 83):
```python
device = Dobot(port="COM4")  # Change to your COM port
```

### Camera Index

If you have multiple cameras, change the index:

**vision_system.py** (line 23):
```python
def __init__(self, camera_index=0):  # Try 1, 2, etc.
```

### Board Positions

Calibrate physical board positions in **Python_Dobot_3T.py** (lines 12-22):
```python
BOARD_POSITIONS = {
    0: [x, y, z],  # Top-left
    1: [x, y, z],  # Top-center
    # ... etc
}
```

### Piece Storage

Set storage locations in **Python_Dobot_3T.py** (lines 25-26):
```python
BLUE_STORAGE = [x, y, z]
RED_STORAGE = [x, y, z]
```

## 🐛 Troubleshooting

### Problem: Dobot not connecting

**Solution:**
1. Check USB cable connected
2. Check Dobot powered on
3. Find correct COM port in Device Manager (Windows)
4. Update port in code (see Configuration above)

### Problem: Web server won't start

**Solutions:**
1. Check Flask installed: `pip install flask flask-socketio`
2. Check port 5000 not in use
3. Try different port in `web_server.py`:
   ```python
   socketio.run(app, host='0.0.0.0', port=5001)
   ```

### Problem: Camera not opening

**Solutions:**
1. Check camera connected
2. Try different camera index (0, 1, 2)
3. Close other apps using camera (Zoom, Teams, etc.)
4. Check camera permissions in Windows settings

### Problem: Vision not detecting pieces

**Solutions:**
1. Re-run calibration: `python calibrate_camera.py`
2. Check lighting conditions
3. Ensure pieces are solid blue/red colors
4. Test detection: `python vision_system.py` then press 'd'

### Problem: Robot moves to wrong position

**Solutions:**
1. Calibrate board positions in `Python_Dobot_3T.py`
2. Test positions: Run game, choose option 2 (Test board positions)
3. Adjust coordinates and test again

## 📊 System Architecture

```
┌─────────────────┐
│   Web Browser   │  (User Interface)
│  GUI_for_3T.html│
└────────┬────────┘
         │ HTTP/WebSocket
         ↓
┌─────────────────┐
│   Web Server    │  (Control Logic)
│  web_server.py  │
└────┬──────┬─────┘
     │      │
     │      └─────────────┐
     ↓                    ↓
┌─────────────┐    ┌──────────────┐
│  Vision     │    │   Dobot      │
│  System     │    │   Control    │
│ vision_     │    │ Python_      │
│ system.py   │    │ Dobot_3T.py  │
└─────────────┘    └──────────────┘
     │                    │
     ↓                    ↓
┌─────────────┐    ┌──────────────┐
│   Camera    │    │   Dobot      │
│  Hardware   │    │   Hardware   │
└─────────────┘    └──────────────┘
```

## 🎯 Gameplay Modes

### Mode 1: GUI Only (No Vision)
- Click cells in web interface
- Robot responds automatically
- Good for testing and demo

### Mode 2: Vision Enabled (Automatic)
- Place physical pieces on board
- Camera detects moves
- Robot responds automatically
- Full hands-free gameplay

### Mode 3: Testing Functions
Run `python Python_Dobot_3T.py` directly:
1. Play tic-tac-toe (manual input mode)
2. Test board positions
3. Test pickup/place operations

## 📝 Workflow Summary

### Initial Setup (One Time)
1. Install Python dependencies
2. Connect and test Dobot
3. Calibrate camera
4. Configure board positions

### Each Game Session
1. Power on Dobot
2. Start web server
3. Open browser to localhost:5000
4. (Optional) Enable vision
5. Play game
6. Reset and play again

### Recalibration (When Needed)
- Camera moved → Re-calibrate camera
- Board moved → Re-calibrate board positions
- Lighting changed → Re-calibrate colors

## 🎓 Learning Path

**Beginner:**
1. ✓ Test Dobot connection
2. ✓ Run web server and GUI
3. ✓ Play game using GUI clicks

**Intermediate:**
4. ✓ Calibrate camera
5. ✓ Test vision detection
6. ✓ Play game with vision enabled

**Advanced:**
7. Adjust board positions for your setup
8. Fine-tune color detection ranges
9. Modify game logic or add features
10. Optimize robot movement speed

## 📚 Documentation

- **[README_WEB_GUI.md](README_WEB_GUI.md)**: Web server and GUI details
- **[README_VISION.md](README_VISION.md)**: Computer vision system guide
- **Python_Dobot_3T.py**: Well-commented game logic and robot control

## ✅ System Check

Before playing, verify:
- [ ] Dobot connected (COM port correct)
- [ ] Web server running (port 5000)
- [ ] Browser can access GUI
- [ ] Camera working (if using vision)
- [ ] Calibration file exists (if using vision)
- [ ] Board positions calibrated
- [ ] Piece storage locations set

## 🎉 You're Ready!

Everything is set up and documented. Start with manual mode (GUI clicks), then progress to vision mode once you're comfortable.

**Enjoy your AI-powered Tic-Tac-Toe robot!** 🤖
