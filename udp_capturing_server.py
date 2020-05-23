import cv2


class UDPCapturingServer:
    def __init__(self, address=('0.0.0.0', 11111)):

        self.clients = []
        self.add_client("192.168.10.1")

        self.host = address[0]
        self.port = address[1]
        self.address = address

        self.cap = None
        self.frame = None
        self.message = None
        self.received_flag = False
        self.background_frame_read = None

    def get_text_message(self):
        if self.received_flag:
            self.received_flag = False
            return self.message.decode('utf-8').rstrip("\r\n")
        else:
            return None

    def get_message(self):
        if self.received_flag:
            self.received_flag = False
            return self.message
        else:
            return None

    def add_client(self, client):
        self.clients.append(client)

    def get_udp_video_address(self):
        return 'udp://@' + self.host + ':' + str(self.port)  # + '?overrun_nonfatal=1&fifo_size=5000'

    def get_video_capture(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.get_udp_video_address())

        if not self.cap.isOpened():
            self.cap.open(self.get_udp_video_address())

        return self.cap


def main():
    from udp_client import UDPClient
    client = UDPClient()
    print(client.send_message_with_response("command"))
    print(client.send_message_with_response("streamon"))
    server = UDPCapturingServer()
    res = False
    frame = None
    cv2.namedWindow("drone")
    while True:
        try:
            cap = server.get_video_capture()
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

if __name__ == '__main__':
    main()
