# Code by Max Haberer
from djitellopy import Tello
import time


class CustomTello(Tello):
    def __init__(self):
        super().__init__()

    # Two rewritten tello vars
    RESPONSE_TIMEOUT = 15
    TAKEOFF_TIMEOUT = 12
    TIME_BTW_RC_CONTROL_COMMANDS = -1
    # Var to store the camera position, True for forward camera, False for downward camera
    camera_position = True

    def send_control_command(self, command: str, timeout: int = RESPONSE_TIMEOUT) -> bool:
        """
        Modified control command.
        Will stop all motors if the land command fails.
        """
        response = "max retries exceeded"
        for i in range(0, self.retry_count):
            response = self.send_command_with_return(command, timeout=timeout)

            if response.lower() == 'ok':
                return True

            self.LOGGER.debug("Command attempt #{} failed for command: '{}'".format(i, command))
        if command == "land":
            print("Land command failed, killing all motors")
            self.emergency()
            exit()
        self.raise_result_error(command, response)
        return False  # never reached

    def stop(self):
        """
        Hovers in the air. Supposedly.
        """
        self.send_control_command("stop")

    def cam(self, angle: str):
        """
        Switches to the specified camera
        """
        if angle == self.camera_position:
            print("Error, camera is already facing that direction.")
        if angle == "fwd":
            self.send_command_with_return("downvision 0")
            self.camera_position = True
        elif angle == "down":
            self.send_command_with_return("downvision 1")
            self.camera_position = False
        else:
            print("Camera angle not recognized")

    def pipeDown(self):
        """
        Shorter and sweeter version of end()
        """
        if self.is_flying:
            self.land()
        if self.stream_on:
            self.streamoff()

    def set_wifi_credentials(self, myssid, mypassword):
        """
        Set the Wi-Fi SSID and password. The Tello will reboot afterwords.
        Only run this command after all configuration is finished and you've reached the point that you would start running movement commands.
        This should be the last command you run.
        In short, Connect, Setup & Start Video Feed >> This command >> Nothing
        """
        cmd = 'wifi {} {}'.format(myssid, mypassword)
        self.send_command_without_return(cmd)

    def takeoff(self):
        """Automatic takeoff.
        """
        # Something it takes a looooot of time to take off and return a succesful takeoff.
        # So we better wait. Otherwise, it would give us an error on the following calls.
        self.send_control_command("takeoff", timeout=Tello.TAKEOFF_TIMEOUT)
        self.is_flying = True

    def send_rc_control(self, left_right_velocity: int, forward_backward_velocity: int, up_down_velocity: int,
                        yaw_velocity: int):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:
            left_right_velocity: -100~100 (left/right)
            forward_backward_velocity: -100~100 (forward/backward)
            up_down_velocity: -100~100 (up/down)
            yaw_velocity: -100~100 (yaw)
        """
        def clamp100(x: int) -> int:
            return max(-100, min(100, x))

        if time.time() - self.last_rc_control_timestamp > self.TIME_BTW_RC_CONTROL_COMMANDS:
            self.last_rc_control_timestamp = time.time()
            cmd = 'rc {} {} {} {}'.format(
                clamp100(left_right_velocity),
                clamp100(forward_backward_velocity),
                clamp100(up_down_velocity),
                clamp100(yaw_velocity)
            )
            self.send_command_without_return(cmd)
