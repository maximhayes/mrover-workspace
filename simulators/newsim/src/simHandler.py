# from .__main__ import SimulatorMetaClass
import asyncio
import math
from . import mathUtils
# Globals List:


# contains the initialization code for initial setup of the field
def initObjectsOnField(sim):
    startPos = sim.Odom(39, 0, -110, 0, 0)
    field = sim.Field(startPos)  # make field entity and rover
    rover = sim.Rover(startPos)
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
            # checking if object is within fov and detection distance (cv_thresh)
            if isinstance(item, sim.TennisBall): # detect which object
                sim.TennisBallMsg.found = True
                sim.TennisBallMsg.distance = math.hypot(delta_x, delta_y)
                sim.TennisBallMsg.bearing = math.atan2(delta_y, delta_x)
                break
            if isinstance(item, sim.Obstacle):
                sim.ObstacleMsg.detected = True
                sim.ObstacleMsg.bearing = calc_move_best_path(sim, object_list, sim.rover, 
                                                              delta_x, delta_y)
                break
                # calculates best path away from the obstacle, not bearing to


    # for obj in object_list:
        # rover loc - obj loc = delta loc
        # use some trig and get your results
        # for tennis balls, mark if found

def move_trans(sim, distance):  # method to move translationally
    # not done, but basically it needs to mvoe and scan at the same time
    calc_visible(sim, sim.Tennis_Balls)
    calc_visible(sim, sim.Obstacles)
            # use bearing to calculate components to add to 

def move_rot(sim, angle):  # method to rotate
    # input angle must be properly signed
    while abs(angle) > 2:
        if angle <= 0:
            sim.rover.bearing -= 2 * sim.rover.speed_rotational
            angle -= 2
        else:
            sim.rover.bearing += 2 * sim.rover.speed_rotational
            angle += 2
    sim.rover.bearing += angle


def move_interpolate(self, angle, distance):
    pass 
    # would be used to calculate rover moving and turning
    # at the same time

async def simulatorOn(sim):
    while True:
        if sim.AutonStateMsg.is_auton is not True:
            break
        else:
            calc_visible(sim, sim.Tennis_Balls)
            calc_visible(sim, sim.Obstacles)
        await asyncio.sleep(10)


async def runSimulator(sim):
    sim.rover, sim.field = initObjectsOnField(sim)
    # need a frontend mechanism to actually turn auton_state to true

    while True:
        print("Sim ran!")
        if sim.AutonStateMsg.is_auton is True:
            simulatorOn(sim)
        await asyncio.sleep(10)
