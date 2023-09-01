# paste code from other .py files into this file to run them
from djitellopy import tello
import KeyPressModule as Gk
import time
import cv2

Gk.init()
me = tello.Tello()
me.connect()
print(me.get_battery())
has_launched = False

global img

me.streamon()


def movement(left_right, fwd_back, up_down, turn):
    me.send_rc_control(left_right, fwd_back, up_down, turn)


def halt():
    while me.get_speed_x() or me.get_speed_y() or me.get_speed_z():
        left_right, fwd_back, up_down, turn = 0, 0, 0, 0
        me.send_rc_control(left_right, fwd_back, up_down, turn)


if not has_launched:
    me.takeoff()
    time.sleep(5)
    has_launched = True


while has_launched:
    me.go_xyz_speed(100, -100, 0, 100)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (450, 300))
    cv2.imshow("Image", img)
    cv2.waitKey(1)
    if Gk.getkey("f"):
        me.land()
        me.streamoff()
        time.sleep(3)
        break
    if Gk.getkey("c"):
        cv2.imwrite(f'Resources/Images/{time.time()}.jpg', img)
