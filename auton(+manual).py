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
me.streamon()
frame_read = me.get_frame_read()

# Set wifi name and password
# me.set_wifi_credentials("4Runner", "tellorun")

# Set up the position tracking and video feed on/off boolean
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
        if kb.is_pressed("shift"):
            me.emergency()
        # print("ToF reading: " + str(me.get_distance_tof() - 10))


livestream = Thread(target=videofeed)
livestream.start()


def land():
    global feed
    feed = False
    me.pipeDown()


def turn(deg):
    if deg > 0:
        me.rotate_clockwise(deg)
    elif deg < 0:
        me.rotate_counter_clockwise(-deg)
    if current_pos[3] + deg < 0:
        current_pos[3] = 360 - (pymath.absolute(deg) - current_pos[3])
    else:
        current_pos[3] += deg
    if current_pos[3] >= 360:
        current_pos[3] -= 360
    time.sleep(0.25)


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
    if current_pos[3] == 90:
        current_pos[1] -= distance
    if current_pos[3] == 180:
        current_pos[0] += distance
    if current_pos[3] == 270:
        current_pos[1] += distance
    time.sleep(0.25)


def goHomeET():
    # Use pythagorean theorem to get the distance between the starting point and the current location
    # Use Tan-1(X distance / Y distance) to get the angle at which we must align ourselves as to go forward unto the starting point
    turnHome = int((90*((current_pos[3]/90)-1)))
    if turnHome >= 0:
        me.rotate_counter_clockwise(turnHome)
    else:
        me.rotate_clockwise(90)
    # me.rotate_counter_clockwise(int(pymath.degrees(pymath.arctan((current_pos[0]/current_pos[1])))))
    turn(-int(pymath.degrees(pymath.arctan((current_pos[0]/current_pos[1])))))
    me.move_forward(int(1.05*pymath.sqrt(pymath.square(current_pos[0])+pymath.square(current_pos[1]))))
    current_pos[0], current_pos[1], current_pos[2] = 0, 0, 0
    time.sleep(2)


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
        dropoff()
        me.land()
    if kb.is_pressed("w"):
        me.takeoff()
        time.sleep(1)
        move(300)
        turn(90)
        move(200)
        goHomeET()
        land()
    if kb.is_pressed("space") or kb.is_pressed("shift"):
        break
