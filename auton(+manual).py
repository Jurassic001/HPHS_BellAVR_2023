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


def videofeed():
    while True:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (750, 500))
        cv2.imshow("Live Feed", img)
        cv2.waitKey(1)
        cv2.moveWindow("Live Feed", 0, 0)
        if keyboard.is_pressed("f"):
            me.land()
            time.sleep(3)
            cv2.destroyAllWindows()
            me.streamoff()
        if keyboard.is_pressed("space"):
            me.emergency()
            cv2.destroyAllWindows()
            me.streamoff()


livestream = Thread(target=videofeed)
livestream.start()


def move(x, y, z):
    me.go_xyz_speed(x, y, z, 100)


def hover(wait):
    me.send_rc_control(0, 0, 0, 0)
    time.sleep(wait)


def turn(degree):
    me.rotate_clockwise(degree)


me.takeoff()
turn(45)
move(500, 0, 50)
move(100, 0, 0)
hover(10)
"""
move(0, 50, 0)
hover(1)
move(0, 0, 50)
hover(1)
"""
me.land()
me.streamoff()
