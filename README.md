# Tic Tac Toe with the Dobot Magician Lite  
- Team Members: Ishan Srivastava, Nick Nekrasov, Aadi Kadam
- Course: RAS 101  
- Project: Final Dobot Lab – Tic Tac Toe

## 1. Introduction

This project is a fully working Tic Tac Toe game where the Dobot Magician Lite plays against a human. The robot places red blocks using the suction cup, while the human plays with blue blocks. The human always plays first.

A second Dobot was used as a stable camera stand so that the camera could capture the board clearly. The camera feeds were processed to detect the human move, and then the robot responded with the best possible move.

The entire system is built in Python and uses a web based interface for interaction.

## 2. Coordinate Calibration

To place blocks accurately, all nine board positions were measured inside DobotLab.  
For each square:

- The end effector was moved to the center
- The X, Y and Z coordinates were recorded
- A safe hover height was set for travel movements
- A pickup location for red blocks was also recorded

These coordinates were stored in a calibration file so the game logic could use them directly.

## 3. Vision System

A camera mounted on the second Dobot captured images of the board during the game.  
The program divided the board into nine regions and identified:

- Red blocks (robot moves)
- Blue blocks (human moves)
- Empty tiles

The vision system updated the board state in real time and allowed the robot to understand where the human placed their block.

## 4. Game Logic

To decide its move, the robot used the minimax algorithm. This gives the robot a perfect strategy and ensures it cannot lose.

The turn cycle was:

1. Human places a blue block  
2. The camera detects the updated board  
3. The robot computes the best move  
4. The robot picks up a red block and places it on the chosen square  

This produced a complete and smooth game experience.

## 5. Robot Movements

The robot followed a simple set of steps for each move:

- Move to a safe hover point  
- Drop down and pick up a red block  
- Turn suction on  
- Move to the chosen board position  
- Lower and place the block  
- Turn suction off  
- Return to a safe position  

These movements were handled by Python functions inside the control scripts.

## 6. Web Interface

A lightweight web interface was created using Flask and SocketIO. It displayed:

- The current board  
- Whose turn it was  
- The final game result  

This made the game very clear and easy to play.

## 7. Challenges and Learning

Some challenges in the project were:

- Calibrating the camera for accurate color detection
- Making sure the block is placed in the center each time
- Syncing the camera system with the robot movements and game logic

Through this project I learned how different parts of a robotics system work together. It helped me understand how vision, movement, and decision making can be combined to create a real interactive experience.

## 8. Conclusion

The final system plays a full Tic Tac Toe match from start to finish. The human makes a move, the camera detects it, and the robot responds with the best possible move. The robot uses a perfect strategy through the minimax algorithm, which makes the experience feel complete and intelligent.

This project brought together vision processing, robot motion, and artificial intelligence in a practical and meaningful way.

