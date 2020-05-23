from tello import Tello
from face_vector import FaceVector
from time import sleep
from cv2 import imshow, waitKey, namedWindow, imread


class FaceTracker:
    """Constants"""
    FB_S = 15  # FWD/BWD Speed of the drone
    LR_S = 25  # LFT/RGHT Speed of the drone
    UD_S = 25
    CW_S = 25  # CW/CCW Speed of the drone
    FPS = 20  # Frames per second of the pygame window display

    def __init__(self, height, width):
        """Start loading"""
        namedWindow("drone")
        self.paper = imread("./resources/Tello.png")
        self.height = height
        self.width = width
        self.fv = FaceVector(height, width)
        self.tello = Tello()
        # Drone velocities between -100~100
        self.for_back_velocity = 20
        self.left_right_velocity = 20
        self.up_down_velocity = 20
        self.yaw_velocity = 20
        self.speed = 20
        self.send_rc_control = False
        self.should_stop = False
        self.mode = "keyboard"

    def run(self, show=False, debug=False):
        """Connecting block"""
        if not self.tello.connect():
            return
        print("Connected")
        if not self.tello.set_speed(self.speed):
            return
        print("Speeds set")

        """Stream start block"""
        if not self.tello.streamoff():
            return
        if not self.tello.streamon():
            return
        cap = self.tello.server.get_video_capture()
        print("Stream started")

        """Main loop"""
        while not self.should_stop:
            vec = None
            """Frame reading block"""
            if self.mode == "tracking" or show or debug:
                try:
                    r, frame = cap.read()
                except ValueError:
                    continue
                if r:
                    """Creating target directions vector"""
                    if self.mode == "tracking" or debug:
                        vec, frame = self.fv.direction_vector_3d_with_returning_image(frame)
                    """Frame plotting(requires from argument: bool:SHOW)"""
                    if show or debug:
                        frame = self.fv.text_addition(frame, vec)
                        imshow("drone", frame)
            if (not show) and (not debug):
                imshow("drone", self.paper)
            key = waitKey(5) & 0xff

            """Keyboard commands getting"""
            self.check_key(key)

            if self.mode == "tracking":
                """Driving block"""
                if vec is None:
                    vec = [0, 0, 0]
                print(vec)

                """Setting velocities depending from directions vector VEC"""
                if vec[0] != 0 or vec[1] != 0:
                    """Moving in 2D space at first"""
                    # set left/right velocity
                    self.left_right_velocity = -self.LR_S * vec[0]
                    # set up/down velocity
                    self.up_down_velocity = self.UD_S * vec[1]
                    # set forward/backward velocity
                else:
                    """Then moving forward/backward"""
                    self.for_back_velocity = self.FB_S * vec[2]
                    # set yaw clockwise velocity
                    self.yaw_velocity = self.CW_S * 0
                """Send move commands"""
                self.update()

            sleep(1 / self.FPS)
        self.tello.end()

    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.send_rc_control:
            self.tello.move_with_velocities(self.left_right_velocity, self.for_back_velocity,
                                            self.up_down_velocity, self.yaw_velocity)

    def check_key(self, key):
        """
        Moves Tello through the keyboard keys.
            - T / G : Takeoff / Land(Ground).
            - W / S : Up / Down.
            - A / D : CW / CCW.
            - I / K : Forward / Backward.
            - J / L : Left / Right.
            - SPACE : Start / Stop face tracking.
            - Q : Quit.
        """

        if key == ord('q'):  # stop
            self.should_stop = True
        elif key == ord('t'):  # takeoff
            print("Flying")
            self.tello.takeoff()
            self.send_rc_control = True
        elif key == ord('g'):  # land
            print("Landing")
            self.tello.land()
            self.send_rc_control = False
        elif key == ord('i'):  # forward
            self.tello.forward(50)
        elif key == ord('k'):  # backward
            self.tello.back(50)
        elif key == ord('j'):  # left
            self.tello.left(50)
        elif key == ord('l'):  # right
            self.tello.right(50)
        elif key == ord('w'):  # up
            self.tello.up(50)
        elif key == ord('s'):  # down
            self.tello.down(50)
        elif key == ord('a'):  # cw
            self.tello.rotate_cw(30)
        elif key == ord('d'):  # ccw
            self.tello.rotate_ccw(30)
        elif key == ord(' '):  # change mode
            self.change_mode()

    """Realise mode changing event"""
    def change_mode(self):
        if self.mode == "tracking":
            self.mode = "keyboard"
            self.tello.stop()
        elif self.mode == "keyboard":
            self.mode = "tracking"


def main():
    tracker = FaceTracker(480, 640)
    tracker.run()  # todo: try to run without showing


if __name__ == '__main__':
    main()
