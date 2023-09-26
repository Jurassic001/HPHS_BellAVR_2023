import djitellopy as tello


class CustomTello(tello):
    def __init__(self):
        super().__init__()

    def stop(self):
        """Hovers in the air.
        """
        self.send_control_command("stop")

    def cam(self, angle: str):
        """Switches to the camera that you tell it to.
        """
        if angle == "fwd":
            self.send_command_with_return("downvision 0")
        if angle == "down":
            self.send_command_with_return("downvision 1")

    def pipeDown(self):
        """Shorter and sweeter version of end()
        """
        if self.is_flying:
            self.land()
        if self.stream_on:
            self.streamoff()
            exit()
