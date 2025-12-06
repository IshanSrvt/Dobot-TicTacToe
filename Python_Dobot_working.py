from Python_Dobot_setup import MODE_PTP, Dobot
import pydobot
import time

device = Dobot(port="COM3")

device.home() # Home the robot

(pose, joint) = device.get_pose() #Get current position and joint angles

print(f"pose: {pose}, j: {joint}")

[x,y,z,r] = pose
[j1,j2,j3,j4] = joint

print(pose)

device.speed(75,75)

# Iteration 0 (Block 1): Pick at (230, 30), Drop at (230, 99)
device.move_to(230, 30, 10, r, mode=MODE_PTP.MOVJ_XYZ) # "Above" pickup
device.move_to(230, 30, -42, r, mode=MODE_PTP.MOVJ_XYZ) # "AT" pickup (absolute Z=-42)
device.suck(True) # Suction on
device.move_to(230, 30, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Lift block to safe height
device.move_to(230, 99, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Move to drop-off at safe height
device.move_to(230, 99, -42, r, mode=MODE_PTP.MOVJ_XYZ) # Lower to placement height
device.suck(False) # Suction off
device.move_to(230, 99, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Safe exit

# Iteration 1 (Block 2): Pick at (230, -29), Drop at (230, 40)
device.move_to(230, -29, 10, r, mode=MODE_PTP.MOVJ_XYZ) # "Above" pickup
device.move_to(230, -29, -42, r, mode=MODE_PTP.MOVJ_XYZ) # "AT" pickup (absolute Z=-42)
device.suck(True) # Suction on
device.move_to(230, -29, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Lift block to safe height
device.move_to(230, 40, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Move to drop-off at safe height (69mm right)
device.move_to(230, 40, -42, r, mode=MODE_PTP.MOVJ_XYZ) # Lower to placement height
device.suck(False) # Suction off
device.move_to(230, 40, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Safe exit

# Iteration 2 (Block 3): Pick at (289, -29), Drop at (289, 40)

device.move_to(289, -29, 10, r, mode=MODE_PTP.MOVJ_XYZ)  # "Above" pickup
device.move_to(289, -29, -42, r, mode=MODE_PTP.MOVJ_XYZ) # "AT" pickup (absolute Z=-42)
device.suck(True) # Suction on
device.move_to(289, -29, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Lift block to safe height
device.move_to(289, 40, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Move to drop-off at safe height (69mm right)
device.move_to(289, 40, -42, r, mode=MODE_PTP.MOVJ_XYZ) # Lower to placement height
device.suck(False) # Suction off
device.move_to(289, 40, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Safe exit

# Iteration 3 (Block 4): Pick at (289, 30), Drop at (289, 99)

device.move_to(289, 30, 10, r, mode=MODE_PTP.MOVJ_XYZ) # "Above" pickup
device.move_to(289, 30, -42, r, mode=MODE_PTP.MOVJ_XYZ) # "AT" pickup (absolute Z=-42)
device.suck(True) # Suction on
device.move_to(289, 30, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Lift block to safe height
device.move_to(289, 99, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Move to drop-off at safe height
device.move_to(289, 99, -42, r, mode=MODE_PTP.MOVJ_XYZ) # Lower to placement height
device.suck(False) # Suction off
device.move_to(289, 99, 10, r, mode=MODE_PTP.MOVJ_XYZ) # Safe exit

#Control gripper and suction cup
# device.grip(True) # Close gripper
# device.grip(False) # Open the gripper

#device.suck(True) # Turn on the suction cup
# device.suck(False) # Turn off the suction cup

device.close()