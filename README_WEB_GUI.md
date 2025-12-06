# Tic-Tac-Toe Robot Web GUI

This guide explains how to run the Tic-Tac-Toe robot with the web-based GUI interface.

## Prerequisites

1. Python 3.8 or higher
2. Dobot Magician connected to COM3 (or update the port in `Python_Dobot_3T.py`)
3. All required Python packages installed

## Installation

1. Install the required Python packages:
```bash
pip install -r requirements.txt
```

## Running the Application

### Step 1: Start the Web Server

Run the Flask web server that connects the GUI to the Dobot:

```bash
python web_server.py
```

You should see output like:
```
============================================================
TIC-TAC-TOE ROBOT WEB SERVER
============================================================
Starting server...
Open your browser to: http://localhost:5000
============================================================
```

### Step 2: Open the Web GUI

Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Play

1. **Choose Your Color**: Click either "Blue (You)" or "Red (Robot)" to start the game
   - If you choose Blue, you'll go first
   - If you choose Red, the robot goes first

2. **Make Your Move**:
   - Click on any empty cell on the board to place your piece
   - The GUI will send your move to the Python backend
   - The robot will physically pick up and place the piece

3. **Robot's Turn**:
   - After your move, the robot automatically calculates its best move using minimax AI
   - You'll see status updates: "Robot is thinking..." → "Robot is moving..."
   - The robot will physically execute the move

4. **Game End**:
   - The game ends when someone wins or the board is full (tie)
   - Click "New Game" to reset and play again

## Architecture

### Components

1. **web_server.py**: Flask server that bridges the HTML GUI with Python Dobot control
   - API endpoints for game actions (`/api/start`, `/api/move/human`, `/api/reset`)
   - WebSocket events for real-time communication
   - Game state management

2. **GUI_for_3T.html**: Web-based user interface
   - Interactive 3x3 game board
   - Color selection
   - Real-time status updates
   - WebSocket connection to backend

3. **Python_Dobot_3T.py**: Core game logic and Dobot control
   - TicTacToeGame class for game state
   - Minimax AI algorithm
   - Physical movement functions
   - Board position definitions

### Communication Flow

```
User clicks cell in GUI
    ↓
HTML sends HTTP POST to /api/move/human
    ↓
Flask receives move and updates game state
    ↓
Flask triggers robot_turn() in separate thread
    ↓
Robot calculates best move (minimax)
    ↓
Robot executes physical movement
    ↓
WebSocket emits 'robot_move_complete' event
    ↓
GUI updates board display
```

## API Endpoints

### GET /api/status
Returns current game status and board state.

### POST /api/start
Start a new game.
```json
{
  "human_color": "blue"  // or "red"
}
```

### POST /api/move/human
Register a human player move.
```json
{
  "position": 4  // 0-8, board position
}
```

### POST /api/reset
Reset the game and return robot to home position.

## WebSocket Events

### Server → Client
- `game_started`: Game has started with color assignments
- `robot_thinking`: Robot is calculating its move
- `robot_move_start`: Robot begins physical movement
- `robot_move_complete`: Robot has placed its piece
- `game_end`: Game has ended with winner information
- `robot_error`: An error occurred during robot operation

### Client → Server
- `request_game_state`: Request current game state

## Troubleshooting

### Connection Issues
- Ensure the web server is running on port 5000
- Check that no other application is using port 5000
- Verify the Dobot is connected to the correct COM port

### Robot Not Moving
- Check that the Dobot is properly connected and powered on
- Verify the COM port in `Python_Dobot_3T.py` (line 42)
- Check the console for error messages

### GUI Not Updating
- Open browser console (F12) to check for JavaScript errors
- Verify WebSocket connection (should see "Connected to server")
- Refresh the page to reconnect

## Configuration

### Board Positions
Board positions can be calibrated in `Python_Dobot_3T.py`:
```python
BOARD_POSITIONS = {
    0: [x, y, z],  # Top-left
    1: [x, y, z],  # Top-center
    ...
}
```

### Storage Locations
Adjust piece storage positions:
```python
BLUE_STORAGE = [x, y, z]
RED_STORAGE = [x, y, z]
```

### Server Port
Change the server port in `web_server.py`:
```python
socketio.run(app, host='0.0.0.0', port=5000)  # Change 5000 to desired port
```

And update the HTML file (`GUI_for_3T.html`):
```javascript
const socket = io('http://localhost:5000');  // Match the port
```

## Next Steps

Before implementing vision logic, test the connection:

1. Start the web server
2. Open the GUI in your browser
3. Play a complete game using manual moves
4. Verify the robot executes moves correctly
5. Check that game state synchronizes between GUI and backend

Once the basic connection is working, you can integrate the computer vision system for automatic move detection.
