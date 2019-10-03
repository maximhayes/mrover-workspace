# from .__main__ import SimulatorMetaClass
import asyncio
import math
from . import mathUtils
# Globals List:


# contains the initialization code for initial setup of the field
def initObjectsOnField(sim):
    startPos = sim.GPS(39, 0, -110, 0, 0)
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
    elif obj_type == "post":
        sim.Posts.append(obj_struct)
    else:
        print("Object passed is not valid")


def removeObject(sim, obj_in):
    # used later to remove object from frontend
    # uses built-in id() function to identify instance we seek
    for item in sim.Waypoints:
        if id(item) == id(obj_in):
            sim.Waypoints.remove(obj_in)
            break
    for item in sim.Posts:
        if id(item) == id(obj_in):
            sim.Posts.remove(obj_in)
            break
    for item in sim.Obstacles:
        if id(item) == id(obj_in):
            sim.Obstacles.remove(obj_in) #was sims.Waypoints... just error?
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
            # checking if object is within fov and detection distance (cv_thresh)
            if isinstance(item, sim.Post): # detect which object
                sim.PostMsg.found = True
                sim.PostMsg.distance = math.hypot(delta_x, delta_y)
                sim.PostMsg.bearing = math.atan2(delta_y, delta_x)
            if isinstance(item, sim.Obstacle):
                sim.ObstacleMsg.detected = True
                sim.ObstacleMsg.bearing = calc_move_best_path(sim, object_list, sim.rover, 
                                                              delta_x, delta_y)
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
    speed_trans = sim.rover.speed_translational * ((1 - sim.JoystickMsg.dampen) / 2) * sim.JoystickMsg.forward_back
    deltaDeg = meters2deg(sim, speed_trans, sim.rover.bearing)
    changeRoverPos(sim, deltaDeg)



def move_rot(sim):  # method to rotate
    speed_rot = sim.rover.speed_rotational * ((1 - sim.JoystickMsg.dampen) / 2) * sim.JoystickMsg.left_right
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
            calc_visible(sim, sim.Posts)
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

# old move trans code
# if distance is not -999:    
#         while(distance > 0):
#             # if it needs to travel less than the displacement from velocity/unit time
#             if distance <= sim.rover.speed_translational:
#                 # moves rover remaining distance and changes distance to 0, exiting function
#                 deltaDeg = meters2deg(sim, distance, sim.rover.bearing)
#                 changeRoverPos(sim, deltaDeg)
#                 distance = 0
#                 return
#             else:
#                 deltaDeg = meters2deg(sim, sim.rover.speed_translational, sim.rover.bearing)
#                 changeRoverPos(sim, deltaDeg)
#     # moves at rate of velocity, regardless of intended destination
#     else: