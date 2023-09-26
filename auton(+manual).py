# Code by Max Haberer
from customTello import CustomTello
import time
import cv2
from threading import Thread
import keyboard as kb


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


def move(x, y, z):
    me.go_xyz_speed(x, y, z, 50)
    current_pos[0], current_pos[1], current_pos[2] = current_pos[0]+int((x*1.1)), current_pos[1]+int((y*1.1)), current_pos[2]+z
    return current_pos[0], current_pos[1], current_pos[2]


def goHomeET():
    if current_pos[3] >= 360:
        me.rotate_clockwise(current_pos[3] % 360)
    else:
        me.rotate_clockwise(current_pos[3])
    me.go_xyz_speed(current_pos[0], current_pos[1], current_pos[2], 50)
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


def turn(deg):
    current_pos[3] += deg
    me.rotate_clockwise(deg)


while True:
    if kb.is_pressed("f"):
        me.takeoff()
        dropoff()
        me.land()
    if kb.is_pressed("w"):
        me.takeoff()
        move(100, 0, 0)
        turn(180)
        goHomeET()
        land()
    if kb.is_pressed("e"):
        me.takeoff()
        move(100, 0, 0)
        goHomeET()
        land()
    if kb.is_pressed("s"):
        me.takeoff()
        time.sleep(2)
        move(100, 0, 0)
        turn(90)
        move(100, 0, 0)
        turn(135)
        move(141, 0, 0)
        me.end()
    if kb.is_pressed("space") or kb.is_pressed("shift"):
        break
