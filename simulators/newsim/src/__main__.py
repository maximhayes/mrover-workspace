from rover_common import aiolcm
import asyncio
from rover_common.aiohelper import run_coroutines
# from rover_msgs import DanesMsg
from rover_msgs import NavStatus
from rover_msgs import Joystick
from rover_msgs import Bearing
from rover_msgs import AutonState
from rover_msgs import GPS


# async def publish_nav_state(lcm):
#     while True:
#         msg = nav_state()
#         msg.


class LCMInterface:

    # variables defined here are common to all classes
    # ideally it shouldn't matter bc we only ever need one instance
    # this is bad practice imho, just defined vars in the block below
    def __init__(self):  # other args if ya want em
        # all initially defined variables should be here
        # this is effectively the class ctor, made of classes of messages
        # use according to https://docs.python.org/3/tutorial/classes.html
        # self.var = var_val (from __init__ input)
        # variables defined here are unique to each instance of the class
        # self.heres_a_var = "i'm a var"

        # below: class list, one class for each message type
        # published or recieved. instantiate them at the bottom
        # of this message definition block
        class NavStatusClass:
            nav_state = 0
            completed_wps = 0
            missed_wps = 0
            total_wps = 0

        class JoystickClass:
            foward_back = 0
            left_right = 0

        class GPSClass:
            latitude_deg = 39.4
            latitude_min = 0
            longitude_deg = -110.5
            longitude_min = 0

        class BearingClass:
            bearing = 0.0

        class ObstacleClass:
            rocks = []

        class TennisBallClass:
            tennis_balls = []

        class CourseClass:
            waypoints = []

        class AutonStateClass:
            is_auton = False

        self.NavStatusMsg = NavStatusClass()
        self.JoystickMsg = JoystickClass()
        self.GPSMsg = GPSClass()
        self.BearingMsg = BearingClass()
        self.ObstacleMsg = ObstacleClass()
        self.TennisBallMsg = TennisBallClass()
        self.CourseMsg = CourseClass()
        self.AutonStateMsg = AutonStateClass()

    # definitions for message processing are below, with callbacks (cb)
    # at the top and publishing at the bottom
    # in this setup, camelCasing denotes a class instance
    # while under_scored_variables indicate a variable within the class
    # to avoid confusion

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
        self.JoystickMsg.kill = m.kill
        self.JoystickMsg.restart = m.restart

    async def publish_bearing(self, lcm):
        while True:
            msg = Bearing()
            msg.bearing = self.BearingMsg.bearing
            lcm.publish("\bearing", msg.encode())
            await asyncio.sleep(10)

    async def publish_auton_state(self, lcm):
        while True:
            msg = AutonState()
            msg.is_auton = self.AutonStateMsg.is_auton
            lcm.publish("\auton", msg.encode())
            await asyncio.sleep(10)

    async def publish_gps_state(self, lcm):
        while True:
            msg = GPS()
            msg.latitude_deg = self.GPSMsg.latitude_deg
            msg.latitude_min = self.GPSMsg.latitude_min
            msg.longitude_deg = self.GPSMsg.longitude_deg
            msg.longitude_min = self.GPSMsg.longitude_min
            lcm.publish("\GPS", msg.encode())
            await asyncio.sleep(10)
    # test message code as a reference for subscription/publishing
    # with a simple intermediate operation

    # def sampleMethod(self):
    #   self.heres_a_var = self.heres_a_var + " again"

    # def test_cb(self, channel, msg):
    #     m = DanesMsg.decode(msg)
    #     self.heres_a_var = m.test_roundtrip
    #     print(self.heres_a_var)
    #     self.sampleMethod()

    # async def publish_test(self, lcm):
    #     while True:
    #         msg = DanesMsg()
    #         msg.test_var_code = 2
    #         msg.test_roundtrip = self.heres_a_var
    #         lcm.publish("\test", msg.encode())
    #         await asyncio.sleep(1000)

    # definitions of other methods should go below here


def main():
    # how you get lcm messages
    lcm = aiolcm.AsyncLCM()

    # instantiates LCMInterface class
    interface = LCMInterface()

    # message subscriptions should appear below
    # lcm.subscribe("\test", interface.test_cb)
    # uncomment this code to see test code of lcm subscription/publishing
    # with the associated callbacks

    # don't uncomment these, I"m just using them as a channel list
    # while I'm coding, i'll delete these when I"m done with them
    # lcm.subscribe("\auton")
    # lcm.subscribe("\bearing")
    # lcm.subscribe("\course")
    # lcm.subscribe("\obstacle")
    # lcm.subscribe("\odometry")
    # lcm.subscribe("\tennis_ball")

    # constantly queries lcm server
    lcm.subscribe("\nav_state", interface.nav_state_cb)
    lcm.subscribe("\drive_control", interface.joystick_cb)

    # testing out a method
    # interface.sampleMethod()

    # creates loop to execute this code repeatedly with the lcm
    run_coroutines(lcm.loop(), interface.publish_bearing(lcm))


# also necessary for the build system, idk why
if __name__ == "__main__":
    main()
