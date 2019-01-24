from rover_common import aiolcm
import asyncio
from rover_common.aiohelper import run_coroutines
from rover_msgs import DanesMsg
from rover_msgs import NavStatus


# callback for nav_state, use as an example
# need to return m, make it global, or use it in a larger class
def nav_state_cb(channel, msg):
    m = NavStatus.decode(msg)
    nav_state = m.nav_state
    print(nav_state)


async def publish_test(lcm):
    while True:
        msg = DanesMsg()
        msg.test_var_code = 2
        msg.test_roundtrip = 1
        lcm.publish("\test", msg.encode())
        await asyncio.sleep(1000)


def main():
    # how you get lcm messages
    lcm = aiolcm.AsyncLCM()
    # lcm.subscribe("\auton")
    # lcm.subscribe("\bearing")
    # lcm.subscribe("\course")
    # lcm.subscribe("\obstacle")
    # lcm.subscribe("\odometry")
    # lcm.subscribe("\tennis_ball")
    lcm.subscribe("\nav_state", nav_state_cb)
    # constantly queries lcm server
    run_coroutines(lcm.loop(), publish_test(lcm))
    # some shit for jarvis


if __name__ == "__main__":
    main()
