# Code by Max Haberer
from djitellopy import tello
import KeyPressModule as Gk
import time
import cv2
from threading import Thread

Gk.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
has_launched = False
keepRecording = True

me.streamon()
frame_read = me.get_frame_read()


def videoRecorder():
    while keepRecording:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (360, 240))
        cv2.imshow("Image", img)
        cv2.waitKey(1)


recorder = Thread(target=videoRecorder)
recorder.start()


me.takeoff()
me.go_xyz_speed(100, 0, 0, 20)
me.land()
