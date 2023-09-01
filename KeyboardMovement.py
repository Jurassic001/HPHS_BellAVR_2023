from djitellopy import tello
import KeyPressModule as Gk
from time import sleep

Gk.init()
me = tello.Tello()
me.connect()
print(me.get_battery())


def getkeyboardinput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 500
    if Gk.getkey("a"):
        lr = -speed
    elif Gk.getkey("d"):
        lr = speed
    if Gk.getkey("w"):
        fb = speed
    elif Gk.getkey("s"):
        fb = -speed
    if Gk.getkey("r"):
        ud = speed
    elif Gk.getkey("f"):
        ud = -speed
    if Gk.getkey("q"):
        yv = -speed
    elif Gk.getkey("e"):
        yv = speed
    if Gk.getkey("z"):
        me.land()
        sleep(3)
    if Gk.getkey("x"):
        me.takeoff()
    if Gk.getkey("LEFT"):
        yv = -speed
    elif Gk.getkey("RIGHT"):
        yv = speed
    if Gk.getkey("UP"):
        ud = speed
    elif Gk.getkey("DOWN"):
        ud = -speed
    return [lr, fb, ud, yv]


while True:
    vals = getkeyboardinput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)
