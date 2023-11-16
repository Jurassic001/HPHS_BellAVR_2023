# Code by Max Haberer
from customTello import CustomTello
from threading import Thread
import keyboard as kb
import numpy as pymath
import time
import cv2


# Initialize the tello object, connect to the tello, print its battery level, and set up some stuff for the video feed
tello = CustomTello()
tello.connect()
time.sleep(1)
tello.streamoff()
tello.streamon()
frame_read = tello.get_frame_read()


# Set up the position tracking list and video feed boolean
current_pos = [0, 0, 180, 0]
feed = True


# noinspection PyUnresolvedReferences
# cv2 causes a bunch of "cannot find refrence in __init__.py" errors, but they don't actually cause issues (afaik), so we just ignore them
def videofeed():
    """
    Constantly get frames from the tello's camera and displays them, will shut off all motors if backspace is pressed.

    :return: Void
    """
    global feed
    while feed:
        img = tello.get_frame_read().frame
        img = cv2.resize(img, (750, 500))
        if tello.camera_position == "down":
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        cv2.waitKey(1)
        cv2.imshow("Tello Interface Program (TIP)", img)
        cv2.moveWindow("Tello Interface Program (TIP)", 500, 0)
        if kb.is_pressed("backspace"):
            tello.emergency()
            exit()


livestream = Thread(target=videofeed)
livestream.start()


def setWifiCreds():
    """
    Sets tello's wifi signal name and password. Signal name will appear as "TELLO-{NAME}".
    Calling this function will restart the Tello.

    :return: Void
    """
    NAME = "4Runner"
    PASSWORD = "tellorun"
    tello.set_wifi_credentials(NAME, PASSWORD)


def setPosition():
    """
    Sets X and Y values to 0, Angle value to 180°. Sets height value to current height.

    :return: Void
    """
    global current_pos
    current_pos[0], current_pos[1], current_pos[2], current_pos[3] = 0, 0, 180, tello.get_height()


def waitUntil(targtime):
    """
    Wait until a predetermined target time is passed. Good for timing out autonomous phases during competitions.
    If the target time has been passed a message will print and the code will continue as normal.

    :param targtime: Should be set beforehand using the syntax "time.time() + {Number of seconds}".
    :return: Void
    """
    if targtime > time.time():
        print("Waiting for " + str(targtime - time.time()) + " seconds")
        time.sleep(targtime - time.time())
    else:
        print("ERROR: Attempted to wait for " + str(targtime - time.time()) + " seconds")


def keychecks_timeout(key: str, timeout: int):
    """
    Wait until a specified key is pressed, or until the request times out.

    :param key: Any key, formatted as "key_name".
    :param timeout: Should be in seconds. A value <= 0 will lead to the program locking up until the desired key is pressed.
    :return: True if the key is pressed, False if the request times out.
    """
    if timeout <= 0:
        print("Press the \"" + key + "\" key to continue.")
        kb.wait(key)
        return True
    else:
        print("Waiting for the \"" + key + "\" key to be pressed. Will wait for " + str(timeout) + " seconds.")
        targtime = time.time() + timeout
        while targtime < time.time():
            if kb.is_pressed(key):
                return True
        return False


def keychecks_eitheror(key1: str, key2: str):
    """
    Constantly checks until one of two keys are pressed.

    :param key1: Any key, formatted as "key_name".
    :param key2: Any key except key1, formatted the same way.
    :return: The value of key1 or key2, whichever is pressed first
    """
    while True:
        if kb.is_pressed(key1):
            return key1
        elif kb.is_pressed(key2):
            return key2


def takeoff(spd: int):
    """
    My own takeoff command, that sets speed and calibrates height upon takeoff.

    :param spd: Must be less than or equal to 100 and greater than 0
    :return: Void
    """
    tello.takeoff()
    current_pos[3] = tello.get_height()
    print("Height Calibrated: " + str(current_pos[3]))
    tello.set_speed(spd)


def land(state: str):
    """
    My own land command, with two different states depending on if you're landing temporarily or shutting off

    :param state: "none" for temp landing, "end" for landing + shutoff
    :return: Void
    """
    print("Landing with state: " + state)
    if state == "end":
        global feed
        feed = False
        print("And Alexander wept, for there were no more worlds to conquer.")
        livestream.join()
        tello.pipeDown()
        exit()
    elif state == "none":
        tello.land()
    else:
        print("Landing state not recognized, maintaining flight")


def turn(deg):
    """
    Command that turns the specificed distance in degrees, positive for clockwise, negative for counter-clockwise

    :param deg: Positive for clockwise, negative for counter-clockwise. Should be a multiple of 90 if you intend to use special navigation functions.
    :return: Void
    """
    while deg >= 360:
        deg -= 360
    if deg > 0:
        tello.rotate_clockwise(deg)
    elif deg < 0:
        tello.rotate_counter_clockwise(-deg)
    if current_pos[2] + deg < 0:
        current_pos[2] = 360 - (int(pymath.absolute(deg)) - current_pos[2])
    else:
        current_pos[2] += deg
    if current_pos[2] >= 360:
        current_pos[2] -= 360
    time.sleep(0.2)


def faceDeg(angle):
    """
    Faces the desired angle. Not much else to it.

    :param angle: Just a humble degree measurement
    :return: Void
    """
    turn(int(angle-current_pos[2]))


def relativeHeight(altitude):
    """
    Goes up or down in an attempt to reach a specific height. Height is relative to the floor and calibrated on takeoff.

    :param altitude: Any value except a negative or a high (500+) number should work. Do not try and descend into the floor.
    :return: Void
    """
    altitude -= current_pos[3]
    current_pos[3] += altitude
    if altitude > 0:
        tello.move_up(altitude)
    elif altitude < 0:
        tello.move_down(-altitude)
    time.sleep(0.1)


def move(distance: int):
    """
    Move the specified number of centimeters forward. Will keep track of position assuming you're facing a cardinal direction.

    :param distance: Can handle any non-negative number. Bigger distances will be split into multiple commands because tello's can't comprehend distances of over 500 cm.
    :return: Void
    """
    if current_pos[2] == 0:
        current_pos[0] -= distance
    elif current_pos[2] == 90:
        current_pos[1] -= distance
    elif current_pos[2] == 180:
        current_pos[0] += distance
    elif current_pos[2] == 270:
        current_pos[1] += distance
    while distance > 500:
        tello.move_forward(480)
        distance -= 480
    tello.move_forward(distance)
    time.sleep(0.1)


def move_back(distance: int):
    """
    Move the specified number of centimeters backwards. Will keep track of position assuming you're facing a cardinal direction.

    :param distance: Can handle any non-negative number. Bigger distances will be split into multiple commands because tello's can't comprehend distances of over 500 cm.
    :return: Void
    """
    if current_pos[2] == 0:
        current_pos[0] += distance
    elif current_pos[2] == 90:
        current_pos[1] += distance
    elif current_pos[2] == 180:
        current_pos[0] -= distance
    elif current_pos[2] == 270:
        current_pos[1] -= distance
    while distance > 500:
        tello.move_back(480)
        distance -= 480
    tello.move_back(distance)
    time.sleep(0.1)


def goHomeET(location: str):
    """
    Can take the tello home from anywhere on the field. Can designate multiple targets to return to, and assign appropriate offset values.

    :param location: Can be used to designate different return targets and their respective positions relative to the tello's starting position.
    :return: Void
    """
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


# noinspection PyUnresolvedReferences
# Same cv2 issue as videofeed(), same fix
def display_controls():
    """
    Displays the keybinds for manual control.

    :return: Void
    """
    img = pymath.zeros((400, 350, 3), dtype=pymath.uint8)
    controls_text = [
        "Controls:",
        "  W: Move Forward",
        "  S: Move Backward",
        "  A: Move Left",
        "  D: Move Right",
        "  R: Move Up",
        "  F: Move Down",
        "  Q: Rotate Counter-Clockwise",
        "  E: Rotate Clockwise",
        "  P: Land/Takeoff",
        "  Space: Land and Shutdown",
        "  K + W: Set Camera Forward",
        "  K + S: Set Camera Downward",
        "  Up Arrow: Flip Forward",
        "  Left Arrow: Flip Left",
        "  Right Arrow: Flip Right",
        "  Down Arrow: Flip Backward",
        "  0: End Manual Control"
    ]
    for i, text in enumerate(controls_text):
        cv2.putText(img, text, (10, 20 * (i + 1)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.imshow("Controls", img)
    cv2.moveWindow("Controls", 0, 0)
    cv2.waitKey(1)


def keyboard_control():
    """
    Function that, when activated, will enable manual control over the tello.
    Press 0 to end manual control. It will ask you to confirm cancellation.

    :return: Void
    """
    print("Manual Control: Online")
    display_controls()
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
        if kb.is_pressed("p"):
            if tello.is_flying:
                land("none")
            else:
                takeoff(100)
        if kb.is_pressed("backspace"):
            tello.emergency()
        if kb.is_pressed("space"):
            land("end")
        if kb.is_pressed("k+s"):
            tello.cam("down")
        elif kb.is_pressed("k+w"):
            tello.cam("fwd")
        if kb.is_pressed("up"):
            tello.flip_forward()
        elif kb.is_pressed("left"):
            tello.flip_left()
        elif kb.is_pressed("right"):
            tello.flip_right()
        elif kb.is_pressed("down"):
            tello.flip_back()
        if kb.is_pressed("0"):
            print("Are you sure you want to end manual control?")
            print("Press 0 again to confirm. You have 5 seconds.")
            if keychecks_timeout("0", 5):
                print("Manual Control: Offline")
                # noinspection PyUnresolvedReferences
                cv2.destroyWindow("Controls")
                break
        tello.send_rc_control(lr, fb, ud, yv)


# Here it all comes together
print("Welcome to the Tello Interface Program (TIP)")
print("Battery level: " + str(tello.get_battery()) + "%")
print("")
print("Press the M key to run phase 1 auton + manual")
print("Press Enter to initiate manual control")
if keychecks_eitheror("m", "enter") == "m":
    print("o7")
    takeoff(80)
    relativeHeight(130)
    move(358)
    relativeHeight(80)
    tello.cam("down")
    tello.flip_back()
    time.sleep(1)
    tello.cam("up")
    relativeHeight(130)
    move_back(358)
    land("none")
    keyboard_control()
else:
    keyboard_control()
