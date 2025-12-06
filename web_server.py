from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from Python_Dobot_setup import MODE_PTP, Dobot
import threading
import time
import os

# ============================================================================
# FLASK WEB SERVER FOR TIC-TAC-TOE GUI
# ============================================================================

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# Import game logic from main file
from Python_Dobot_3T import (
    TicTacToeGame,
    get_best_move,
    robot_make_move,
    initialize_dobot,
    EMPTY, HUMAN, ROBOT
)
import Python_Dobot_3T

# Import vision system
from vision_system import TicTacToeVision

# ============================================================================
# GLOBAL GAME STATE
# ============================================================================

current_game = None
game_lock = threading.Lock()

# Vision system
vision_system = None
vision_enabled = False
vision_thread = None
vision_stop_event = threading.Event()

# Initialize Dobot on server startup
print("Initializing Dobot...")
dobot_device = initialize_dobot(port="COM4", home_on_init=False)
print("Dobot ready (home position not set - call /api/home to home the device)")

# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Serve the HTML GUI"""
    return app.send_static_file('GUI_for_3T.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current game status"""
    with game_lock:
        if current_game is None:
            return jsonify({
                'status': 'no_game',
                'message': 'No active game'
            })

        return jsonify({
            'status': 'active',
            'board': current_game.board,
            'human_color': current_game.human_color,
            'robot_color': current_game.robot_color,
            'pieces_remaining': current_game.pieces_remaining
        })

@app.route('/api/start', methods=['POST'])
def start_game():
    """Start a new game"""
    global current_game, vision_enabled

    data = request.json
    human_color = data.get('human_color', 'blue')
    use_vision = data.get('use_vision', False)

    if human_color not in ['blue', 'red']:
        return jsonify({'error': 'Invalid color. Choose blue or red'}), 400

    with game_lock:
        current_game = TicTacToeGame(human_color=human_color)

    # Enable/disable vision based on request
    vision_enabled = use_vision
    if vision_enabled:
        start_vision_monitoring()

    socketio.emit('game_started', {
        'human_color': human_color,
        'robot_color': current_game.robot_color,
        'vision_enabled': vision_enabled
    })

    # If robot goes first (red), make the first move
    if current_game.robot_color == 'blue':
        threading.Thread(target=robot_turn).start()

    return jsonify({
        'success': True,
        'human_color': human_color,
        'robot_color': current_game.robot_color,
        'vision_enabled': vision_enabled
    })

@app.route('/api/move/human', methods=['POST'])
def human_move():
    """Register human player move"""
    global current_game

    if current_game is None:
        return jsonify({'error': 'No active game'}), 400

    data = request.json
    position = data.get('position')

    if position is None or not isinstance(position, int):
        return jsonify({'error': 'Invalid position'}), 400

    with game_lock:
        if not current_game.is_valid_move(position):
            return jsonify({'error': 'Invalid move'}), 400

        # Register human move
        current_game.set_cell(position, HUMAN)

        # Check for winner
        winner = current_game.check_winner()
        if winner:
            result = handle_game_end(winner)
            return jsonify(result)

        if current_game.is_board_full():
            result = handle_game_end(None)
            return jsonify(result)

    # Trigger robot turn
    threading.Thread(target=robot_turn).start()

    return jsonify({
        'success': True,
        'position': position
    })

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the game"""
    global current_game

    with game_lock:
        current_game = None

    # Return Dobot to home position
    try:
        Python_Dobot_3T.device.wait_for_cmd(Python_Dobot_3T.device.home())
    except Exception as e:
        print(f"Error homing device: {e}")

    socketio.emit('game_reset', {})

    # Stop vision monitoring if active
    stop_vision_monitoring()

    return jsonify({'success': True})

@app.route('/api/vision/toggle', methods=['POST'])
def toggle_vision():
    """Enable or disable vision monitoring"""
    global vision_enabled

    data = request.json
    enable = data.get('enable', False)

    if enable:
        if not initialize_vision():
            return jsonify({
                'success': False,
                'error': 'Failed to initialize vision system. Check camera and calibration.'
            }), 500
        start_vision_monitoring()
        vision_enabled = True
        message = 'Vision monitoring enabled'
    else:
        stop_vision_monitoring()
        vision_enabled = False
        message = 'Vision monitoring disabled'

    return jsonify({
        'success': True,
        'vision_enabled': vision_enabled,
        'message': message
    })

@app.route('/api/vision/status', methods=['GET'])
def vision_status():
    """Get vision system status"""
    return jsonify({
        'vision_enabled': vision_enabled,
        'calibration_exists': os.path.exists('board_calibration.json')
    })

# ============================================================================
# VISION MONITORING
# ============================================================================

def initialize_vision():
    """Initialize the vision system"""
    global vision_system

    if vision_system is None:
        try:
            vision_system = TicTacToeVision()
            if not vision_system.load_calibration():
                print("Warning: No calibration found. Vision may not work correctly.")
                print("Run calibrate_camera.py to calibrate the system.")
            return True
        except Exception as e:
            print(f"Error initializing vision system: {e}")
            return False
    return True

def start_vision_monitoring():
    """Start the vision monitoring thread"""
    global vision_thread, vision_stop_event

    if not initialize_vision():
        print("Failed to initialize vision system")
        return

    if vision_thread is not None and vision_thread.is_alive():
        print("Vision monitoring already running")
        return

    vision_stop_event.clear()
    vision_thread = threading.Thread(target=vision_monitor_loop, daemon=True)
    vision_thread.start()
    print("Vision monitoring started")

def stop_vision_monitoring():
    """Stop the vision monitoring thread"""
    global vision_thread, vision_stop_event, vision_system

    if vision_thread is not None:
        vision_stop_event.set()
        vision_thread.join(timeout=2)
        vision_thread = None

    if vision_system is not None:
        vision_system.close_camera()

    print("Vision monitoring stopped")

def vision_monitor_loop():
    """Main loop for vision monitoring (runs in separate thread)"""
    global current_game, vision_system

    if vision_system is None or not vision_system.open_camera():
        print("Failed to open camera for vision monitoring")
        return

    # Import cv2 for debug window
    import cv2

    # Wait a moment for game to stabilize
    time.sleep(1)

    # Get initial board state
    previous_state = [None] * 9

    print("Vision monitoring active - watching for human moves...")
    print("DEBUG: Opening camera window - press 'q' in window to close")

    # Create debug window
    cv2.namedWindow('Vision Debug - Camera Feed', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Vision Debug - Camera Feed', 800, 600)

    while not vision_stop_event.is_set():
        try:
            # Capture and display frame
            frame = vision_system.capture_frame()
            if frame is None:
                print("DEBUG: Failed to capture frame")
                time.sleep(0.5)
                continue

            # Create visualization
            viz_frame = vision_system.visualize_detection(frame, draw_grid=True)

            # Add status text
            with game_lock:
                if current_game is not None:
                    status_text = f"Game Active | Human: {current_game.human_color} | Robot: {current_game.robot_color}"
                else:
                    status_text = "No active game"

            cv2.putText(viz_frame, status_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show the frame
            cv2.imshow('Vision Debug - Camera Feed', viz_frame)

            # Check for 'q' key to close window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("DEBUG: User closed camera window")
                break

            # Check if we're waiting for human move
            with game_lock:
                if current_game is None:
                    time.sleep(0.5)
                    continue

                # Only monitor during human's turn
                current_board = current_game.board.copy()
                human_color = current_game.human_color
                robot_color = current_game.robot_color

            # Detect board state
            detected_state = vision_system.detect_board_state()

            if detected_state is None:
                print("DEBUG: No board state detected")
                time.sleep(0.5)
                continue

            # Debug: print detected state
            print(f"DEBUG: Detected state: {detected_state}")

            # Convert game board state to color format for comparison
            color_board = []
            for cell in current_board:
                if cell == EMPTY:
                    color_board.append(None)
                elif cell == HUMAN:
                    color_board.append(current_game.human_color)
                elif cell == ROBOT:
                    color_board.append(current_game.robot_color)
                else:
                    color_board.append(None)

            # Find new moves
            for i in range(9):
                if color_board[i] is None and detected_state[i] is not None:
                    # New piece detected!
                    detected_color = detected_state[i]

                    # Verify it's the human's color
                    if detected_color == current_game.human_color:
                        print(f"Vision detected human move at position {i}")

                        # Register the move
                        with game_lock:
                            if current_game.is_valid_move(i):
                                current_game.set_cell(i, HUMAN)

                                # Notify GUI
                                socketio.emit('human_move_detected', {
                                    'position': i,
                                    'color': detected_color
                                })

                                # Check for winner
                                winner = current_game.check_winner()
                                if winner:
                                    result = handle_game_end(winner)
                                    socketio.emit('game_end', result)
                                    break
                                elif current_game.is_board_full():
                                    result = handle_game_end(None)
                                    socketio.emit('game_end', result)
                                    break

                        # Trigger robot turn
                        threading.Thread(target=robot_turn).start()
                        break

            time.sleep(0.5)  # Check twice per second

        except Exception as e:
            print(f"Error in vision monitoring: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(1)

    print("Vision monitoring loop ended")

    # Close debug window
    try:
        cv2.destroyWindow('Vision Debug - Camera Feed')
    except:
        pass

# ============================================================================
# ROBOT TURN LOGIC
# ============================================================================

def robot_turn():
    """Execute robot's turn in a separate thread"""
    global current_game

    print("DEBUG: robot_turn() called")

    if current_game is None:
        print("DEBUG: No current game, exiting robot_turn")
        return

    # Notify GUI that robot is thinking
    socketio.emit('robot_thinking', {})
    print("DEBUG: Robot thinking...")

    # Small delay for realism
    time.sleep(0.5)

    with game_lock:
        # Get best move using minimax
        best_move = get_best_move(current_game)

        if best_move is None:
            print("DEBUG: No valid moves available")
            return

        print(f"DEBUG: Robot chose position {best_move}")

        # Notify GUI of robot's chosen position
        socketio.emit('robot_move_start', {'position': best_move})

    try:
        print(f"DEBUG: Starting physical robot movement to position {best_move}")

        # Execute physical movement
        with game_lock:
            print(f"DEBUG: Calling robot_make_move({best_move})")
            robot_make_move(best_move, current_game)
            print("DEBUG: robot_make_move completed")

        # Notify GUI that move is complete
        socketio.emit('robot_move_complete', {'position': best_move})

        # Check for winner
        with game_lock:
            winner = current_game.check_winner()
            if winner:
                result = handle_game_end(winner)
                socketio.emit('game_end', result)
                return

            if current_game.is_board_full():
                result = handle_game_end(None)
                socketio.emit('game_end', result)
                return

    except Exception as e:
        print(f"Error during robot move: {e}")
        socketio.emit('robot_error', {'error': str(e)})

def handle_game_end(winner):
    """Handle game end logic"""
    if winner == HUMAN:
        message = "Human wins!"
        result = "human"
    elif winner == ROBOT:
        message = "Robot wins!"
        result = "robot"
    else:
        message = "It's a tie!"
        result = "tie"

    return {
        'game_over': True,
        'winner': result,
        'message': message
    }

# ============================================================================
# WEBSOCKET EVENTS
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('request_game_state')
def handle_game_state_request():
    """Send current game state to client"""
    with game_lock:
        if current_game is None:
            emit('game_state', {'status': 'no_game'})
        else:
            emit('game_state', {
                'status': 'active',
                'board': current_game.board,
                'human_color': current_game.human_color,
                'robot_color': current_game.robot_color
            })

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("TIC-TAC-TOE ROBOT WEB SERVER")
    print("=" * 60)
    print(f"Starting server...")
    print(f"Open your browser to: http://localhost:5000")
    print("=" * 60)

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
