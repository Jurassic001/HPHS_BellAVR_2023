from djitellopy import tello
import keyboard as kb
from time import sleep
import time
import cv2

me = tello.Tello()
me.connect()
print(me.get_battery())

global img

me.streamon()


def keyboard_input():
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
    if kb.is_pressed("LEFT"):
        yv = -speed
    elif kb.is_pressed("RIGHT"):
        yv = speed
    if kb.is_pressed("UP"):
        ud = speed
    elif kb.is_pressed("DOWN"):
        ud = -speed
    elif kb.is_pressed("c"):
        cv2.imwrite(f'Resources/Images/{time.time()}.jpg', img)
    return [lr, fb, ud, yv]


while True:
    vals = keyboard_input()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    img = me.get_frame_read().frame
    img = cv2.resize(img, (600, 400))
    cv2.imshow("Live Feed", img)
    cv2.waitKey(1)
    cv2.moveWindow("Live Feed", 650, 0)
    cv2.setWindowProperty("Live Feed", cv2.WND_PROP_TOPMOST, 1)
