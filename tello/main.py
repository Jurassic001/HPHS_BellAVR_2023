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

# Set up the position tracking list, speed value, video and autonomous booleans
current_pos = [0, 0, 180, 0]
me.set_speed(70)
feed = True
auton = True


# noinspection PyUnresolvedReferences
# best way to fix an error is to ignore it
def videofeed():
    global feed
    global auton
    while feed:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (600, 400))
        cv2.waitKey(1)
        cv2.imshow("Live Feed", img)
        if kb.is_pressed("backspace"):
            me.emergency()
            exit()


livestream = Thread(target=videofeed)
livestream.start()


def setPosition():
    global current_pos
    current_pos = [0, 0, 180, 0]


def waitUntil(targtime):
    """
    Wait until the target time is equal to the actual time
    In the meantime we'll twiddle out thumbs
    """
    print("Waiting for " + str(targtime - time.time()) + " seconds")
    thumbs = 1
    while targtime > time.time():
        thumbs += 1
        thumbs -= 1


def takeoff():
    me.takeoff()
    time.sleep(0.50)
    current_pos[3] = me.get_height()
    print("Height Calibrated")


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
    altitude -= current_pos[3]
    current_pos[3] += altitude
    if altitude > 0:
        me.move_up(altitude)
    elif altitude < 0:
        me.move_down(-altitude)
    time.sleep(1)


def move(distance):
    if current_pos[2] == 0:
        current_pos[0] -= distance
    elif current_pos[2] == 90:
        current_pos[1] -= distance
    elif current_pos[2] == 180:
        current_pos[0] += distance
    elif current_pos[2] == 270:
        current_pos[1] += distance
    while distance > 500:
        me.move_forward(500)
        distance -= 500
    me.move_forward(distance)
    time.sleep(0.25)


def goHomeET(location: str):
    print("Current coordinates: (" + str(current_pos[0]) + "," + str(current_pos[1]) + ")")
    if location == "Firehouse":
        current_pos[0] -= 130
    print("Attempting to return to " + location)
    if current_pos[0] != 0 and current_pos[1] != 0:
        if current_pos[1] > 0:
            faceDeg(90)
        elif current_pos[1] < 0:
            faceDeg(270)
        print("Calculating origin direction")
        homeAngle = -int(pymath.degrees(pymath.arctan((current_pos[0] / current_pos[1]))))
        turn(homeAngle)
        print("Calculating origin distance")
        move(int(pymath.sqrt(pymath.square(current_pos[0]) + pymath.square(current_pos[1]))))
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
    setPosition()


while auton:
    targetTime = time.time() + 30
    time.sleep(1)
    takeoff()
    time.sleep(3)
    relativeHeight(110)
    move(358)
    relativeHeight(80)
    time.sleep(2)
    # this is where my smokejumper release would go... IF I HAD ONE
    goHomeET("Landing pad")
    land("none")
    waitUntil(targetTime)
    takeoff()
    turn(180)
    relativeHeight(300-80)
    move(650)
    turn(90)
    move(80)
    turn(90)
    relativeHeight(230-80)
    time.sleep(10)
    relativeHeight(250 - 80)
    goHomeET("Firehouse")
    land("end")
