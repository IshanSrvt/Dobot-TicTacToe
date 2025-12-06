# Final Dobot Lab Report: Tic Tac Toe with the Dobot Magician Lite
Student: Ishan Srivastava
Class: RAS 101
Team Members: Aadi Kadam, Nick Nekrasov
 






















## Introduction and Game Style
For this project we built a Tic Tac Toe system where the Dobot Magician Lite plays the game by placing colored blocks. The robot uses red blocks and the human plays with blue blocks. The human always plays first.
We used a second Dobot only to hold the camera steady. This camera allowed us to detect the board state after each move. The main robot then picked up red blocks using the suction cup and placed them on the board based on the game logic.

## Finding the Coordinates
To make the robot place blocks accurately, we first needed the coordinates for all nine squares.
we did this by:
Opening DobotLab
Moving the end effector to the center of each square
Recording the X Y and Z values
Saving a safe hover height for travel
Saving the pickup point for red blocks
These values were stored in a calibration file so the code could load them each time. This helped the robot reach the exact spot for every move.
Camera System and Board Detection
The camera was mounted on the second Dobot which acted like a tripod. We calibrated the camera by taking an image of the empty board and dividing it into nine regions.
The vision program then checked:
If a region had a red block
If a region had a blue block
Or if it was empty
This allowed the robot to understand the board before making its turn. The vision system ran in the background and updated the board in real time.
Game Logic and Robot Decisions
The robot used the minimax algorithm to decide its moves. This method checks all possible future moves and chooses the best one. Because of this the robot cannot lose.
Each turn followed a simple cycle:
The human places a blue block.
The camera updates the board.
The minimax algorithm finds the best red block move.
The robot picks up a red block and places it in the correct square.
This created a smooth and complete game flow.
Robot Movements
The movement steps of the robot were:
Move to a safe hover point
Go down to pick up a red block
Turn suction on
Move to the target board square
Lower and place the block
Turn suction off
Return to a safe height
All these steps were controlled by Python functions in the main server file.
Web Interface
We made a simple web interface using Flask and SocketIO. It showed:
The Tic Tac Toe board
Whose turn it is
The final result of the game
This made the system easy to use and gave a clear visual display during gameplay.
Challenges and Learning
Some challenges we faced were:
Calibrating the camera for consistent color detection
Getting the block placement centered in every square
Syncing the robot movement with the web interface and vision data
Through these steps I learned how different parts of a robotics system must work together. I also learned how to debug movement issues and how vision and logic can guide the robot in real time.

## Conclusion
The final system plays a full Tic Tac Toe game from start to finish. The human makes a move, the camera detects it and the robot responds with the best possible move. The robot always chooses the perfect red block move through the minimax algorithm.
This project brought together motion control vision and artificial intelligence and helped me understand robotics in a very practical way.
