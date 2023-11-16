from customTello import CustomTello
from threading import Thread
import keyboard as kb
import time
import cv2

tello = CustomTello()
tello.connect()
print("Battery level: " + str(tello.get_battery()) + "%")
time.sleep(1)
tello.streamoff()
tello.streamon()
frame_read = tello.get_frame_read()


def keyboard_control():
    print("Manual Control Online")
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
            # land("none")
            tello.land()
        if kb.is_pressed("t"):
            # takeoff(100)
            tello.takeoff()
        if kb.is_pressed("backspace"):
            tello.emergency()
        if kb.is_pressed("space"):
            # land("end")
            tello.end()
            exit()
        if kb.is_pressed("down"):
            tello.cam("down")
        elif kb.is_pressed("up"):
            tello.cam("fwd")
        if kb.is_pressed("k+w"):
            tello.flip_forward()
        elif kb.is_pressed("k+a"):
            tello.flip_left()
        elif kb.is_pressed("k+d"):
            tello.flip_right()
        if kb.is_pressed("m"):
            tello.flip_back()
        tello.send_rc_control(lr, fb, ud, yv)


# noinspection PyUnresolvedReferences
def manual():
    while True:
        img = tello.get_frame_read().frame
        img = cv2.resize(img, (600, 400))
        cv2.waitKey(1)
        cv2.imshow("Tello Interface Program (TIP)", img)


livestream = Thread(target=manual)
livestream.start()
keyboard_control()
