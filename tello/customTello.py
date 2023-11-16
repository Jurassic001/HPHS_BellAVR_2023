# Code by Max Haberer
from djitellopy import Tello
import time


class CustomTello(Tello):
    def __init__(self):
        super().__init__()

    RESPONSE_TIMEOUT = 15
    camera_position = "fwd"
    camera_angle = 0

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

    def takeoff(self):
        """
        Automatic takeoff.
        Overridden so that the drone sleeps for one second after takeoff
        """
        self.send_control_command("takeoff", timeout=Tello.TAKEOFF_TIMEOUT)
        self.is_flying = True
        time.sleep(1)

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
            self.camera_position = "fwd"
            self.camera_angle -= 90
        elif angle == "down":
            self.send_command_with_return("downvision 1")
            self.camera_position = "down"
            self.camera_angle += 90
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
