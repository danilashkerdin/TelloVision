from udp_client import UDPClient
from udp_capturing_server import UDPCapturingServer
from time import time, sleep


class Tello:
    """Constants"""
    ATTEMPT_NUMBERS = 3
    TIMEOUT = 0.1
    FLYING_TIMEOUT = 20
    TIME_BTW_RC_CONTROL_COMMANDS = 0.1

    def __init__(self):
        self.server = UDPCapturingServer()
        self.pilot = UDPClient()

        self.cap = self.server.get_video_capture()
        self.stream_on = False

        self.last_command_time = time()

    """Main"""

    def try_to_send_command(self, command):
        """This function is used to trying sending commands with getting bool response and message to user"""
        self.last_command_time = time()
        for _ in range(self.ATTEMPT_NUMBERS):
            try:
                resp = self.pilot.send_message_with_response(command)
                if resp == 'ok':
                    return True
                sleep(self.TIMEOUT)
            except Exception as e:
                return False, e

    def connect(self):
        """Starts command mode"""
        resp = self.try_to_send_command("command")
        return resp

    def set_wifi(self, ssid, password):
        """Set Wi-Fi with SSID password.
        Returns: bool: True for successful, False for unsuccessful"""
        resp = self.try_to_send_command(f"wifi {ssid} {password}")
        return resp

    def set_speed(self, x):
        """Set speed to x cm/s. Arguments:  x: 10-100"""
        resp = self.try_to_send_command("speed " + str(x))
        return resp

    def end(self):
        """Call this method when you want to end the tello object"""
        if self.stream_on:
            self.streamoff()
        if self.cap is not None:
            self.cap.release()

    """Video streaming"""

    def streamon(self):
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response("streamon")
        return resp == "ok"

    def streamoff(self):
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response("streamoff")
        return resp == "ok"

    """Move"""

    def takeoff(self):
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response("takeoff")
        return resp == "ok"

    def land(self):
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response("land")
        return resp == "ok"

    def stop(self):
        self.last_command_time = time()
        resp = self.move_with_velocities_without_waiting(0, 0, 0, 0)
        return resp == "ok"

    def move(self, direction, x):
        """Tello fly up, down, left, right, forward or back with distance x cm.
        Arguments: direction: up, down, left, right, forward or back, x: 20-500
        Returns: bool: True for successful, False for unsuccessful"""
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response(direction + ' ' + str(x))
        return resp == "ok"

    def up(self, x):
        """Tello fly up with distance x cm.
        Arguments: x: 20-500.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.move("up", x)

    def down(self, x):
        """Tello fly down with distance x cm.
        Arguments: x: 20-500.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.move("down", x)

    def left(self, x):
        """Tello fly left with distance x cm.
        Arguments: x: 20-500.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.move("left", x)

    def right(self, x):
        """Tello fly right with distance x cm.
        Arguments: x: 20-500.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.move("right", x)

    def forward(self, x):
        """Tello fly forward with distance x cm.
        Arguments: x: 20-500.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.move("forward", x)

    def back(self, x):
        """Tello fly backward with distance x cm.
        Arguments: x: 20-500.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.move("back", x)

    def rotate_cw(self, x):
        """Tello rotate x degree clockwise.
        Arguments: x: 1-360
        Returns: bool: True for successful, False for unsuccessful"""
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response("cw " + str(x))
        return resp == "ok"

    def rotate_ccw(self, x):
        """Tello rotate x degree counter-clockwise.
        Arguments: x: 1-360
        Returns: bool: True for successful, False for unsuccessful"""
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response("ccw " + str(x))
        return resp == "ok"

    def flip(self, direction):
        """Tello fly flip.
        Arguments: direction: l (left), r (right), f (forward) or b (back)
        Returns: bool: True for successful, False for unsuccessful"""
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response("flip " + direction)
        return resp == "ok"

    def flip_left(self):
        """Tello fly flip left.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.flip("l")

    def flip_right(self):
        """Tello fly flip left.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.flip("r")

    def flip_forward(self):
        """Tello fly flip left.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.flip("f")

    def flip_back(self):
        """Tello fly flip left.
        Returns: bool: True for successful, False for unsuccessful"""
        return self.flip("b")

    def go(self, x, y, z, speed):
        """Tello fly to x y z in speed (cm/s)
        Arguments: x: 20-500, y: 20-500, z: 20-500, speed: 10-100
        Returns: bool: True for successful, False for unsuccessful"""
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response(f'go {x} {y} {z} {speed}')
        return resp == "ok"

    def curve(self, x1, y1, z1, x2, y2, z2, speed):
        """Tello fly a curve defined by the current and two given coordinates with speed (cm/s).
            - If the arc radius is not within the range of 0.5-10 meters, it responses false.
            - x/y/z can’t be between -20 – 20 at the same time.
        Arguments: x1: 20-500; x2: 20-500; y1: 20-500; y2: 20-500; z1: 20-500; z2: 20-500; speed: 10-60
        Returns: bool: True for successful, False for unsuccessful"""
        self.last_command_time = time()
        resp = self.pilot.send_message_with_response(f'curve {x1} {y1} {z1} {x2} {y2} {z2} {speed}')
        return resp == "ok"

    def move_with_velocities(self, left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:  left_right_velocity: -100~100 (left/right), forward_backward_velocity: -100~100 (forward/backward),
        up_down_velocity: -100~100 (up/down), yaw_velocity: -100~100 (yaw)
        Returns: bool: True for successful, False for unsuccessful"""
        if time() - self.last_command_time < self.TIME_BTW_RC_CONTROL_COMMANDS:
            pass
        else:
            self.last_command_time = time()
            resp = self.pilot.send_message(
                f'rc {left_right_velocity} {forward_backward_velocity} {up_down_velocity} {yaw_velocity}')
            return resp == "ok"

    def move_with_velocities_without_waiting(self, left_right_velocity, forward_backward_velocity, up_down_velocity, yaw_velocity):
        """Send RC control via four channels. Command is sent every self.TIME_BTW_RC_CONTROL_COMMANDS seconds.
        Arguments:  left_right_velocity: -100~100 (left/right), forward_backward_velocity: -100~100 (forward/backward),
        up_down_velocity: -100~100 (up/down), yaw_velocity: -100~100 (yaw)
        Returns: bool: True for successful, False for unsuccessful"""
        self.last_command_time = time()
        resp = self.pilot.send_message(
            f'rc {left_right_velocity} {forward_backward_velocity} {up_down_velocity} {yaw_velocity}')
        return resp == "ok"

    """Info"""

    def get_speed(self):
        """Get current speed (cm/s). Returns: False: Unsuccessful; int: 1-100"""
        self.last_command_time = time()
        return self.pilot.send_message_with_response('speed?')

    def get_battery(self):
        """Get current battery percentage. Returns: False: Unsuccessful; int: -100"""
        self.last_command_time = time()
        return self.pilot.send_message_with_response('battery?')

    def get_flight_time(self):
        """Get current fly time (s). Returns: False: Unsuccessful; int: Seconds elapsed during flight."""
        self.last_command_time = time()
        return self.pilot.send_message_with_response('time?')

    def get_wifi(self):
        """Get wifi snr (%). Returns: False: Unsuccessful; int: 0 - 100 wifi signal quality."""
        self.last_command_time = time()
        return self.pilot.send_message_with_response('wifi?')

    def get_baro(self):
        """Get current barometer value (m). Returns: False: Unsuccessful; float number."""
        self.last_command_time = time()
        return self.pilot.send_message_with_response('baro?')

    def get_attitude(self):
        """Get IMU attitude data
        Returns: False: Unsuccessful; int: pitch roll yaw"""
        self.last_command_time = time()
        return self.pilot.send_message_with_response('attitude?')

    def get_height(self):
        """Get height (cm)
        Returns: False: Unsuccessful; int: 0-3000"""
        self.last_command_time = time()
        return self.pilot.send_message_with_response('height?')


def main():
    import cv2
    t = Tello()
    print(t.cap)
    r = t.connect()
    print(r)
    r = t.streamon()
    res = False
    frame = None
    while True:
        try:
            cap = t.server.get_video_capture()
            res, frame = cap.read()
        except ValueError:
            pass
        if res and frame is not None:
            cv2.imshow("drone", frame)
            print(f"Frame is: {frame}")
            print(f"Shape is: {frame.shape}")
        key = cv2.waitKey(5) & 0xff
        if key == ord('q'):
            break
        else:
            continue


if __name__ == "__main__":
    main()
