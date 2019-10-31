from .simHandler import runSimulator
from rover_common import aiolcm
from abc import ABC
# import math  # , abstractmethod
# import threading  # for later for perf improvements
# import time  # for later, for more accurate information and logging
import asyncio
from rover_common.aiohelper import run_coroutines
# from rover_msgs import DanesMsg
from rover_msgs import (NavStatus, Joystick, GPS, AutonState,
                        Course, Obstacle, TennisBall)
# import mathUtils

# 0. Grab from LCM, or whatever intermediary
# 1. Detect whether the point is within the radius "r" of the rover's view.
#   (a) Find distance between rover and point
#   (b) Compare with FOV range
# 2. Check if the point is within the FOV angle.
#   (a) Compute the range using FOV angle and the angle of the rover
#   (b) Compute the angle of the point
#   (c) Note the range is continuous,
#       but contain points greater than 360, or less than 0,
#       so need to compare the point, and the point + 360 deg
#       (TODO: Check logic)
# NOTE: Found boolean is equivalent to setting to distance to -1
# 3. Export to LCM, or whatever intermediary
#   (a) ???
# 4. PROFIT!!!

# Algorithm, LCM


class SimulatorMetaClass:

    # variables defined here are common to all classes
    # ideally it shouldn't matter bc we only ever need one instance
    # this is bad practice imho, just defined vars in the block below
    def __init__(self):  # other args if ya want em
        # all initially defined variables should be here
        # while not technically globals, this is basically where they are
        # defined for the sim, since the entire instance is the SimMetaClass
        """
        xCoord = 0.0
        yCoord = 0.0
        theta = 0.0
        r = 0.0
        fovAngle = 0.0

        rover = [xCoord, yCoord, theta]
        fov = [r, fovAngle]
        rover[0] = math.atan(1/pow(2, 0.5))
        fov[0] = math.atan(-1/pow(2, 0.5))
        """
        # below: class list, one class for each message type
        # published or recieved. instantiate them at the bottom
        # of this message definition block
        # use the provided imported classes and dump these later
        # you still need to set all the defaults

        self.NavStatusMsg = NavStatus()
        self.JoystickMsg = Joystick()
        # self.GPSMsg = GPS()
        # self.BearingMsg = Bearing()
        self.GPSMsg = GPS()
        self.ObstacleMsg = Obstacle()
        self.TennisBallMsg = TennisBall()
        self.CourseMsg = Course()
        self.AutonStateMsg = AutonState()

        self.NavStatusMsg.nav_state = 0
        self.NavStatusMsg.completed_wps = 0
        self.NavStatusMsg.missed_wps = 0
        self.NavStatusMsg.total_wps = 0

        self.JoystickMsg.forward_back = 0
        self.JoystickMsg.left_right = 0
        self.JoystickMsg.dampen = 0

        self.GPSMsg.latitude_deg = 39
        self.GPSMsg.latitude_min = 0
        self.GPSMsg.longitude_deg = -110
        self.GPSMsg.longitude_min = 0
        self.GPSMsg.bearing_deg = 0
        self.GPSMsg.speed = -999  # this value is never used
        # so it's being set to a dummy value. DO NOT USE IT

        self.ObstacleMsg.detected = 0
        self.ObstacleMsg.bearing = 0

        self.TennisBallMsg.bearing = 0
        self.TennisBallMsg.distance = -1

        self.CourseMsg.num_waypoints = 0
        self.CourseMsg.hash = 0
        self.CourseMsg.waypoints = []

        self.AutonStateMsg.is_auton = False
    # definitions for message processing are below, with callbacks (cb)
    # at the top and publishing at the bottom
    # in this setup, camelCasing denotes a class instance
    # while under_scored_variables indicate a variable within the class
    # to avoid confusion

    def nav_test(self, channel, msg):
        pass
        # define this as per the spec

    # callback function: takes in variable from LCM, sets values locally
    def nav_state_cb(self, channel, msg):
        m = NavStatus.decode(msg)
        self.NavStatusMsg.nav_state = m.nav_state
        self.NavStatusMsg.completed_wps = m.completed_wps
        self.NavStatusMsg.missed_wps = m.missed_wps
        self.NavStatusMsg.total_wps = m.total_wps

    def joystick_cb(self, channel, msg):
        m = Joystick.decode(msg)
        self.JoystickMsg.forward_back = m.forward_back
        self.JoystickMsg.left_right = m.left_right
        self.JoystickMsg.dampen = m.dampen
        # 1-dampen/2
        self.JoystickMsg.kill = m.kill
        self.JoystickMsg.restart = m.restart

    # async def publish_bearing(self, lcm):
    #     while True:
    #         lcm.publish("\bearing", self.BearingMsg.encode())
    #         await asyncio.sleep(10)

    async def publish_auton_state(self, lcm):
        while True:
            lcm.publish("\auton", self.AutonStateMsg.encode())
            await asyncio.sleep(10)

    # async def publish_gps_state(self, lcm):
    #     while True:
    #         lcm.publish("\GPS", self.GPSMsg.encode())
    #         await asyncio.sleep(10)

    # bearing publish

    async def publish_GPS(self, lcm):
        while True:
            lcm.publish("\GPS", self.GPSMsg.encode())
            await asyncio.sleep(10)

    async def publish_course(self, lcm):
        while True:
            lcm.publish("\course", self.CourseMsg.encode())
            await asyncio.sleep(10)

    async def publish_obstacle(self, lcm):
        while True:
            lcm.publish("\obstacle", self.ObstacleMsg.encode())
            await asyncio.sleep(10)

    async def publish_tennis_ball(self, lcm):
        while True:
            lcm.publish("\tennis_ball", self.TennisBallMsg.encode())
            await asyncio.sleep(10)

    # SimObject definitions are below
    # SimObj is the abstract base class that contains properties
    # common to all objects. define additional simulator objects
    # as if you would the Rover class, including proper
    # superclass init

    # identical to the GPS message, minus speed, bc it's a useful
    # object to have internally
    class GPS:
        def __init__(self, lat0, latm0, lon0, lonm0, bearing, speed):
            self.lat_deg = lat0
            self.lat_min = latm0
            self.lon_deg = lon0
            self.lon_min = lonm0
            self.bearing = bearing
            self.speed = speed

    # parent class of sim objects. Has all properties common to all
    # objects

    class SimObj(ABC):
        # define initial location and other properties
        def __init__(self, GPS):
            self.lat_deg = GPS.lat0
            self.lat_min = GPS.latm0
            self.lon_deg = GPS.lon0
            self.lon_min = GPS.lonm0
            self.bearing = GPS.bearing0
            self.shape = 0  # need to create a seed system?

        # any methods common to all classes should be defined
        def get_coords(self):
            return [self.lat_deg, self.lat_min,
                    self.lon_deg, self.lon_min]

        def get_bearing(self):
            return self.bearing

        # here is an abstract method, may be useful
        # @abstractmethod
        # def sample_abs_method(self):
        #     pass
    class Field(SimObj):
        def __init__(self, GPS, radius=2):  # other properties
            super().__init__(GPS)
            self.radius = radius  # in degrees, if not specified
            # radius is 2

    class Rover(SimObj):
        def __init__(self, GPS, speed_trans=1,
                     speed_rot=1):
            super().__init__(GPS)
            self.fov = 120  # units of degrees,
            # 120 if not specified
            self.cv_thresh = 5
            self.speed_translational = speed_trans
            # speed multiplier, 1 if not specified
            self.speed_rotational = speed_rot

    class TennisBall(SimObj):
        def __init__(self, GPS):  # other properties
            super().__init__(GPS)
            self.other_prop = 0

    class Obstacle(SimObj):
        def __init__(self, GPS):  # other properties
            super().__init__(GPS)

    class Waypoint(SimObj):
        def __init__(self, GPS, searchable=0):
            super().__init__(GPS)
            self.search = searchable  # defaults to false if not set


def main():
    # how you get lcm messages
    lcm = aiolcm.AsyncLCM()

    # instantiates Simulator class
    Simulator = SimulatorMetaClass()

    # constantly queries lcm server
    lcm.subscribe("\nav_state", Simulator.nav_state_cb)
    lcm.subscribe("\drive_control", Simulator.joystick_cb)

    # creates loop to execute this code repeatedly with the lcm
    run_coroutines(lcm.loop(), Simulator.publish_auton_state(lcm),
                   Simulator.publish_course(lcm),
                   Simulator.publish_GPS(lcm),
                   Simulator.publish_obstacle(lcm),
                   Simulator.publish_tennis_ball(lcm),
                   runSimulator(Simulator))
    # as a general improvement, it may be worth threading all of the
    # lcm-related bruhaha to offload the worst of the performance hits
    # as the sim becomes more complex and computationally intensive

    # time to run this mf'er
    runSimulator(Simulator)


# also necessary for the build system, idk why
if __name__ == "__main__":
    main()

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
