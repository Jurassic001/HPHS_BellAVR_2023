from djitellopy import Tello
import time


class CustomTello(Tello):
    def __init__(self):
        super().__init__()

    def send_control_command(self, command: str, timeout: int = 7) -> bool:
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
        if angle == "fwd":
            self.send_command_with_return("downvision 0")
        if angle == "down":
            self.send_command_with_return("downvision 1")

    def pipeDown(self):
        """
        Shorter and sweeter version of end()
        Also if self.land() fails then we deactivate all motors
        """
        if self.is_flying:
            self.land()
        if self.stream_on:
            self.streamoff()
        print("You should press Ctrl+F2 NOW!!")
