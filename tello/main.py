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
current_pos = [0, 0, 0, 180]
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
            me.pipeDown()


livestream = Thread(target=videofeed)
livestream.start()


def setPosition():
    global current_pos
    current_pos = [0, 0, 0, 180]


def land(state: str):
    if state == "end":
        global feed
        feed = False
        me.pipeDown()
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
    if current_pos[3] + deg < 0:
        current_pos[3] = 360 - (int(pymath.absolute(deg)) - current_pos[3])
    else:
        current_pos[3] += deg
    if current_pos[3] >= 360:
        current_pos[3] -= 360
    time.sleep(0.25)


def faceDeg(angle):
    turn(int(angle-current_pos[3]))


def alt(updown):
    if updown > 0:
        me.move_up(updown)
        current_pos[2] += updown
    elif updown < 0:
        me.move_down(-updown)
        current_pos[2] -= updown
    time.sleep(0.25)


def move(distance):
    me.move_forward(distance)
    if current_pos[3] == 0:
        current_pos[0] -= distance
    elif current_pos[3] == 90:
        current_pos[1] -= distance
    elif current_pos[3] == 180:
        current_pos[0] += distance
    elif current_pos[3] == 270:
        current_pos[1] += distance
    time.sleep(0.25)


def goHomeET():
    if current_pos[1] > 0:
        faceDeg(90)
    elif current_pos[1] < 0:
        faceDeg(270)
    homeAngle = -int(pymath.degrees(pymath.arctan((current_pos[0] / current_pos[1]))))
    turn(homeAngle)
    me.move_forward(int(pymath.sqrt(pymath.square(current_pos[0]) + pymath.square(current_pos[1]))))
    time.sleep(2)
    faceDeg(180)
    setPosition()


def dropoff():
    # front flip average drift: 52 forward, 4 left
    # back flip average drift: 32 backward, 7 right
    """
    me.flip_forward()
    current_pos[0] += 52
    current_pos[1] += 4

    me.flip_back()
    current_pos[0] += -32
    current_pos[1] += -7
    """
    # Experiment with left and right flips
    me.flip_right()
    """ 
    # maybe this command to halt after flipping?
    me.send_rc_control(0, 0, 0, 0)
    """
    # me.flip_left()
    return current_pos[0], current_pos[1]


while True:
    if kb.is_pressed("f"):
        me.takeoff()
        faceDeg(270)
        faceDeg(180)
        faceDeg(0)
        faceDeg(90)
        land("none")
    if kb.is_pressed("w"):
        me.takeoff()
        move(300)
        turn(90)
        move(200)
        goHomeET()
        land("none")
    if kb.is_pressed("s"):
        me.takeoff()
        turn(180)
        move(100)
        turn(90)
        move(100)
        goHomeET()
        land("none")
    if kb.is_pressed("a"):
        me.takeoff()
        move(200)
        turn(-90)
        move(150)
        goHomeET()
        land("none")
    if kb.is_pressed("d"):
        me.takeoff()
        turn(180)
        move(200)
        turn(-90)
        move(150)
        goHomeET()
        land("none")
