from customTello import CustomTello
import keyboard as kb
import time
import cv2

me = CustomTello()
me.connect()
print("Battery level: " + str(me.get_battery()) + "%")
time.sleep(1)
me.streamoff()
me.streamon()
frame_read = me.get_frame_read()


def keyboard_control():
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
        me.land()
        time.sleep(3)
    if kb.is_pressed("t"):
        me.takeoff()
    if kb.is_pressed("backspace"):
        me.emergency()
    if kb.is_pressed("space"):
        me.end()
    if kb.is_pressed("down"):
        me.cam("down")
    elif kb.is_pressed("up"):
        me.cam("fwd")
    me.send_rc_control(lr, fb, ud, yv)


# noinspection PyUnresolvedReferences
def manual():
    while True:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (600, 400))
        cv2.waitKey(1)
        cv2.imshow("Live Feed", img)
        keyboard_control()


manual()
