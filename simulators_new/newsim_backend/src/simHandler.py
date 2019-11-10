# from .__main__ import SimulatorMetaClass
import asyncio
import math
from . import mathUtils
""" 
0. Grab from LCM, or whatever intermediary
1. Detect whether the point is within the radius "r" of the rover's view.
    (a) Find distance between rover and point
    (b) Compare with FOV range
2. Check if the point is within the FOV angle.
    (a) Compute the range using FOV angle and the angle of the rover
    (b) Compute the angle of the point
    (c) Note the range is continuous, 
        but contain points greater than 360, or less than 0, 
        so need to compare the point, and the point + 360 deg
        (TODO: Check logic)
NOTE: Found boolean is equivalent to setting to distance to -1
3. Export to LCM, or whatever intermediary
4. ???
5. PROFIT!!! 
"""

xRover = 0.0
yRover = 0.0
xWay = 0.0
yWay = 0.0
theta = 0.0
r = 1.0
fovAngle = 0.0

rover = [xWay, yWay, theta]
fov = [r, fovAngle]
rover[0] = math.atan(1/pow(2, 0.5))
fov[0] = math.atan(-1/pow(2, 0.5))
waypoint = [xWay, yWay]

def inRadius(xWay, yWay, xRover, yRover):
    d = math.sqrt(pow(xWay - xRover, 2) + pow(yWay - yRover, 2))
    if d > r:
        return False
    else:
        return True

"""
TODO: Convert to python

Accepts (x1, y1, theta) as the robot's pose,
and (x2, y2) as the point's location
Program knows the FOV's angle and range

Step (1): Checks to make sure point is within the radius of the view
        float distance = sqrt((x1 - x2)*(x1 - x2) +
        (y1 - y2)*(y1 - y2));
        if (distance > radius) {
            return false;
        }

Step (2): Check to make sure the point is within the angle range
        float max = theta + fovAngle/2;
        float min = theta - fovAngle/2;
        if (x1 == 0) {
            angle = 0;
        }
        else {
            float angle = atan(y2/x1);
        }
        if ((angle < max) || (angle > min)) {
            return true;
        }
        else if ((angle + 180 < max) || (angle + 180 > min)) {
            return true;
        }
        else if ((angle - 180 < max) || (angle - 180 > min)) {
            return true;
        }
        else {
            return false;
        }

        TODO: Make if-else checking behavior more elegant (and correct)
        once trig function behavior is known
"""


# contains the initialization code for initial setup of the field
def initObjectsOnField(sim):
    startPos = sim.GPS(39, 0, -110, 0, 0, 0)
    field = sim.Field(startPos)  # make field entity and rover
    rover = sim.Rover(startPos, sim.JoystickMsg.dampen, 1, 1)
    return rover, field  # if we init more than this, return a list
    # for future reference, this is where uploaded test cases get init


def addObject(sim, obj_struct, obj_type):  # this may be implemented
    # in a way that it totally not necessary

    # used later to add object from frontend
    if obj_type == "obstacle":
        sim.Obstacles.append(obj_struct)
    elif obj_type == "waypoint":
        sim.Waypoints.append(obj_struct)
    elif obj_type == "tennis ball":
        sim.Tennis_Balls.append(obj_struct)
    else:
        print("Object passed is not valid")


def removeObject(sim, obj_in):
    # used later to remove object from frontend
    # uses built-in id() function to identify instance we seek
    for item in sim.Waypoints:
        if id(item) == id(obj_in):
            sim.Waypoints.remove(obj_in)
            break
    for item in sim.Tennis_Balls:
        if id(item) == id(obj_in):
            sim.Waypoints.remove(obj_in)
            break
    for item in sim.Obstacles:
        if id(item) == id(obj_in):
            sim.Waypoints.remove(obj_in)
            break

    # debug code
    print("Object does not exist in list, can't be removed")
    pass


def calc_move_best_path(sim, object_list, rover, delta_y, delta_x):
    angle = math.atan2(delta_y, delta_x)
    if angle >= 0:
        diff = rover.fov/2 - angle
        rover.move_rot(-diff)
        return -diff
    else:
        diff = rover.fov/2 + angle
        rover.move_rot(-diff)
        return -diff


def calc_visible(sim, object_list):
    delta_x = 0  # needs to be math'd out
    delta_y = 0  # ditto to this m80
    for item in object_list:
        if (math.atan2(delta_y, delta_x) < sim.rover.fov / 2 and
                math.hypot(delta_x, delta_y) < sim.rover.cv_thresh):
            # checking if object is within
            # fov and detection distance (cv_thresh)
            if isinstance(item, sim.TennisBall):  # detect which object
                sim.TennisBallMsg.found = True
                sim.TennisBallMsg.distance = math.hypot(delta_x, delta_y)
                sim.TennisBallMsg.bearing = math.atan2(delta_y, delta_x)
            if isinstance(item, sim.Obstacle):
                sim.ObstacleMsg.detected = True
                sim.ObstacleMsg.bearing = calc_move_best_path(
                    sim, object_list, sim.rover,
                    delta_x, delta_y
                )
                # calculates best path away from the obstacle, not bearing to
    # for obj in object_list:
        # rover loc - obj loc = delta loc
        # use some trig and get your results
        # for tennis balls, mark if found

# a helper function for move_trans


def changeRoverPos(sim, deltaDeg):
    sim.rover.lat_deg = deltaDeg.lat_deg
    sim.rover.lat_min = deltaDeg.lat_min
    sim.rover.lon_deg = deltaDeg.lon_deg
    sim.rover.long_min = deltaDeg.lon_min


# move translationally, if distance is specified you move that many meters,
# otherwise you move at normal velocity
def move_trans(sim):
    # method to move translationally
    # uses joystick input to determine speed
    speed_trans = sim.rover.speed_translational * \
        ((1 - sim.JoystickMsg.dampen) / 2) * sim.JoystickMsg.forward_back
    deltaDeg = mathUtils.meters2deg(sim, speed_trans, sim.rover.bearing)
    changeRoverPos(sim, deltaDeg)


def move_rot(sim):  # method to rotate
    speed_rot = sim.rover.speed_rotational * \
        ((1 - sim.JoystickMsg.dampen) / 2) * sim.JoystickMsg.left_right
    sim.rover.bearing += speed_rot


def move_interpolate(sim, angle, distance):
    pass
    # would be used to calculate rover moving and turning
    # at the same time, since the rover can move and slightly
    # turn at the same time on the IRL rover
    # this is not currently used, but is here for later


async def simulatorOn(sim):
    while True:
        if sim.AutonStateMsg.is_auton is not True:
            break
        else:
            calc_visible(sim, sim.Tennis_Balls)
            calc_visible(sim, sim.Obstacles)
            move_trans(sim)
            move_rot(sim)
        await asyncio.sleep(10)


async def runSimulator(sim):
    sim.rover, sim.field = initObjectsOnField(sim)
    # need a frontend mechanism to actually turn auton_state to true

    while True:
        print("Sim ran!")
        if sim.AutonStateMsg.is_auton is True:
            simulatorOn(sim)
        await asyncio.sleep(10)
