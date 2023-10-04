from djitellopy import tello
import keyboard as kb
from time import sleep

me = tello.Tello()
me.connect()
print(me.get_battery())


def keyboard_control():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 500
    if kb.is_pressed("a"):
        lr = -speed
    elif kb.is_pressed("d"):
        lr = speed
    if kb.is_pressed("w"):
        fb = speed
    elif kb.is_pressed("s"):
        fb = -speed
    if kb.is_pressed("r"):
        ud = speed
    elif kb.is_pressed("f"):
        ud = -speed
    if kb.is_pressed("q"):
        yv = -speed
    elif kb.is_pressed("e"):
        yv = speed
    if kb.is_pressed("x"):
        me.land()
        sleep(3)
    if kb.is_pressed("z"):
        me.takeoff()
    me.send_rc_control(lr, fb, ud, yv)


while True:
    keyboard_control()
