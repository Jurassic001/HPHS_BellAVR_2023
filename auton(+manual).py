# Code by Max Haberer
from djitellopy import tello
import time
import cv2
from threading import Thread
import keyboard

me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()
frame_read = me.get_frame_read()
current_pos = [0, 0, 0, 0]


def videofeed():
    while True:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (750, 500))
        cv2.imshow("Live Feed", img)
        cv2.waitKey(1)
        cv2.moveWindow("Live Feed", 0, 0)
        if keyboard.is_pressed("p"):
            me.streamoff()
            cv2.destroyAllWindows()
            me.land()
        if keyboard.is_pressed("space"):
            me.streamoff()
            cv2.destroyAllWindows()
            me.emergency()


livestream = Thread(target=videofeed)
livestream.start()


def move(x, y, z):
    me.go_xyz_speed(x-current_pos[0], y-current_pos[1], z-current_pos[2], 100)
    current_pos[0], current_pos[1], current_pos[2] = current_pos[0]+x, current_pos[1]+y, current_pos[2]+z
    return current_pos[0], current_pos[1], current_pos[2]


def dropoff():
    time.sleep(1)
    me.flip_forward()
    current_pos[0] += 5
    return current_pos[0]


def hover(wait):
    numWait = 0
    if wait < 14:
        me.send_rc_control(0, 0, 0, 0)
        time.sleep(wait)
    else:
        while wait > 14:
            wait -= 14
            numWait += 1
        while numWait > 0:
            me.send_rc_control(0, 0, 0, 0)
            time.sleep(14)
        time.sleep(wait)


def turn(degree):
    me.rotate_clockwise(degree-current_pos[3])
    current_pos[3] += degree
    return current_pos[3]


me.takeoff()
move(100, 0, 0)
dropoff()
move(0, 0, 0)
hover(3)
"""
move(0, 50, 0)
hover(1)
move(0, 0, 50)
hover(1)
"""
me.land()
time.sleep(3)
me.end()
