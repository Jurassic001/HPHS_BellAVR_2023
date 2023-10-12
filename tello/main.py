# Code by Max Haberer
from customTello import CustomTello
from threading import Thread
import keyboard as kb
import numpy as pymath
import time
import cv2


# Connect to tello, get battery level, and set up the live video feed
me = CustomTello()
me.connect()
print("Battery level: " + str(me.get_battery()) + "%")
time.sleep(1)
me.streamoff()
me.streamon()
frame_read = me.get_frame_read()

# Set wifi name and password
# me.set_wifi_credentials("4Runner", "tellorun")

# Set up the position tracking, movement speed, and video feed on/off toggle
current_pos = [0, 0, 180]
me.set_speed(70)
feed = True


def videofeed():
    global feed
    while feed:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (600, 400))
        cv2.waitKey(1)
        cv2.imshow("Live Feed", img)
        cv2.moveWindow("Live Feed", 650, 0)
        cv2.setWindowProperty("Live Feed", cv2.WND_PROP_TOPMOST, 1)
        if kb.is_pressed("space"):
            me.emergency()
            exit()


livestream = Thread(target=videofeed)
livestream.start()


def setPosition():
    global current_pos
    current_pos = [0, 0, 180]


def land(state: str):
    if state == "end":
        global feed
        feed = False
        livestream.join()
        me.pipeDown()
        exit()
    elif state == "none":
        me.land()
    else:
        print("Landing state not specified, maintaining flight")


def turn(deg):
    while deg >= 360:
        deg -= 360
    if deg > 0:
        me.rotate_clockwise(deg)
    elif deg < 0:
        me.rotate_counter_clockwise(-deg)
    if current_pos[2] + deg < 0:
        current_pos[2] = 360 - (int(pymath.absolute(deg)) - current_pos[2])
    else:
        current_pos[2] += deg
    if current_pos[2] >= 360:
        current_pos[2] -= 360
    time.sleep(0.25)


def faceDeg(angle):
    turn(int(angle-current_pos[2]))


def relativeHeight(altitude):
    altitude -= me.get_height()
    if altitude > 0:
        me.move_up(altitude)
    elif altitude < 0:
        me.move_down(-altitude)
    time.sleep(0.25)


def move(distance):
    me.move_forward(distance)
    if current_pos[2] == 0:
        current_pos[0] -= distance
    elif current_pos[2] == 90:
        current_pos[1] -= distance
    elif current_pos[2] == 180:
        current_pos[0] += distance
    elif current_pos[2] == 270:
        current_pos[1] += distance
    time.sleep(0.25)


def goHomeET():
    print("Attempting to return to origin point")
    print("Current coordinates: (" + str(current_pos[0]) + "," + str(current_pos[1]) + ")")
    if current_pos[0] != 0 & current_pos[1] != 0:
        if current_pos[1] > 0:
            faceDeg(90)
        elif current_pos[1] < 0:
            faceDeg(270)
        print("Shoutout to the HPHS math department fr")
        homeAngle = -int(pymath.degrees(pymath.arctan((current_pos[0] / current_pos[1]))))
        turn(homeAngle)
        me.move_forward(int(pymath.sqrt(pymath.square(current_pos[0]) + pymath.square(current_pos[1]))))
    elif current_pos[1] == 0:
        if current_pos[0] > 0:
            faceDeg(0)
            move(current_pos[0])
        elif current_pos[0] < 0:
            faceDeg(180)
            move(-current_pos[0])
    elif current_pos[0] == 0:
        if current_pos[1] > 0:
            faceDeg(90)
            move(current_pos[1])
        elif current_pos[1] < 0:
            faceDeg(270)
            move(-current_pos[1])
    else:
        print("Position Data Failure - Cannot Return Home")
    time.sleep(2)
    faceDeg(180)
    relativeHeight(50)
    setPosition()


def dropoff():
    print("Kid named smokejumper: ")
    """
    the code to drop off the smoke jumper will go here
    """


while True:
    time.sleep(1)
    me.takeoff()
    relativeHeight(120)
    move(500)
    relativeHeight(70)
    dropoff()
    relativeHeight(120)
    goHomeET()
    land("end")
