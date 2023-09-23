# Code by Max Haberer
from djitellopy import tello
import time
import cv2
from threading import Thread
import keyboard as kb


# Connect to tello, get battery level, and set up the live video feed
me = tello.Tello()
me.connect()
print("Battery level: " + str(me.get_battery()) + "%")
time.sleep(1)
me.streamon()
frame_read = me.get_frame_read()

# Set wifi name and password
# me.set_wifi_credentials("4Runner", "tellorun")

# Set up the position tracking
current_pos = [0, 0, 0]


def videofeed():
    while True:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (600, 400))
        cv2.imshow("Live Feed", img)
        cv2.waitKey(1)
        cv2.moveWindow("Live Feed", 650, 0)
        cv2.setWindowProperty("Live Feed", cv2.WND_PROP_TOPMOST, 1)
        if kb.is_pressed("space"):
            cv2.destroyWindow("Live Feed")
            me.land()
            me.streamoff()
            exit()
        if kb.is_pressed("shift"):
            me.emergency()
            exit()
        # print("ToF reading: " + str(me.get_distance_tof() - 10))


livestream = Thread(target=videofeed)
livestream.start()


def land():
    me.land()
    livestream.daemon = True
    cv2.destroyWindow("Live Feed")
    me.streamoff()
    exit()


def move(x, y, z):
    me.go_xyz_speed(x, y, z, 50)
    current_pos[0], current_pos[1], current_pos[2] = current_pos[0]+int((x*1.1)), current_pos[1]+int((y*1.1)), current_pos[2]+z
    return current_pos[0], current_pos[1], current_pos[2]


def goHomeET():
    me.go_xyz_speed(0 - current_pos[0], 0 - current_pos[1], 0 - current_pos[2], 50)
    time.sleep(1)
    current_pos[0], current_pos[1], current_pos[2] = 0, 0, 0


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


if True:
    fwd = 100
    while True:
        if kb.is_pressed("f"):
            me.takeoff()
            dropoff()
            me.land()
        if kb.is_pressed("w"):
            me.takeoff()
            move(100, 0, 0)
            time.sleep(2)
            goHomeET()
            me.land()
        if kb.is_pressed("e"):
            fwd += 100
            me.takeoff()
            time.sleep(2)
            move(fwd, 0, 50)
            goHomeET()
            me.land()
        if kb.is_pressed("s"):
            me.takeoff()
            time.sleep(1)
            me.cam("down")
            time.sleep(3)
            move(100, 0, 0)
            time.sleep(3)
            move(0, -100, 0)
            time.sleep(3)
            goHomeET()
            land()
