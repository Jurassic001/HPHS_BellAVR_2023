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

# Set up the position tracking list, speed value, and video feed boolean
current_pos = [0, 0, 180, 0]
feed = True


# noinspection PyUnresolvedReferences
# best way to fix an error is to ignore it
def videofeed():
    global feed
    while feed:
        img = me.get_frame_read().frame
        # img = cv2.resize(img, (600, 400))
        cv2.resize(img, (1200, 800))
        if me.camera_position == "down":
            cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.moveWindow(img, 360, 140)
        cv2.waitKey(1)
        cv2.imshow("Live Feed", img)
        if kb.is_pressed("backspace"):
            me.emergency()
            exit()


livestream = Thread(target=videofeed)
livestream.start()


def setPosition():
    global current_pos
    current_pos[0], current_pos[1], current_pos[2], current_pos[3] = 0, 0, me.get_height(), 0


def waitUntil(targtime):
    """
    Wait until the target time is equal to the actual time
    In the meantime we'll twiddle our thumbs
    """
    print("Waiting for " + str(targtime - time.time()) + " seconds")
    thumbs = 1
    while targtime > time.time():
        thumbs += 1
        thumbs -= 1


def waitUntilKeypressed(key: str):
    """
    Wait until a specified key is pressed
    """
    foo = 1
    while not kb.is_pressed(key):
        foo += 1
        foo -= 1


def takeoff(spd: int):
    me.takeoff()
    current_pos[3] = me.get_height()
    print("Height Calibrated: " + str(current_pos[3]))
    me.set_speed(spd)


def land(state: str):
    if state == "end":
        print("And Alexander wept, for there were no more worlds to conquer.")
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
        me.move_forward(480)
        distance -= 480
    me.move_forward(distance)
    time.sleep(0.25)


def goHomeET(location: str):
    print("Current coordinates: (" + str(current_pos[0]) + "," + str(current_pos[1]) + ")")
    if location == "Firehouse":
        current_pos[0] += 120
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


print("Tello Autonomus Control Online")
print("Press M to start")
waitUntilKeypressed("m")
print("o7")
takeoff(80)
relativeHeight(130)
move(358)
relativeHeight(80)
me.flip_back()
time.sleep(1)
while True:
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
    if kb.is_pressed("l"):
        land("none")
        # me.land()
    if kb.is_pressed("t"):
        takeoff(100)
        # me.takeoff()
    if kb.is_pressed("backspace"):
        me.emergency()
    if kb.is_pressed("space"):
        land("end")
        # me.end()
        exit()
    if kb.is_pressed("down"):
        me.cam("down")
    elif kb.is_pressed("up"):
        me.cam("fwd")
    if kb.is_pressed("k+w"):
        me.flip_forward()
    elif kb.is_pressed("k+a"):
        me.flip_left()
    elif kb.is_pressed("k+d"):
        me.flip_right()
    if kb.is_pressed("m"):
        me.flip_back()
    me.send_rc_control(lr, fb, ud, yv)
