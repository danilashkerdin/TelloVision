import socket


class UDPClient:
    def __init__(self, server=("192.168.10.1", 8889), buffer_size=1024):
        self.server = server
        self.buffer_size = buffer_size
        self.udp_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def receive_message(self):
        response = self.udp_client_socket.recvfrom(self.buffer_size)
        try:
            decoded_response = response[0].decode('utf-8').rstrip("\r\n")
            return decoded_response
        except UnicodeDecodeError:
            print(UnicodeDecodeError, "не удалось расшифровать ответ сервера")

    def send_message(self, message):
        encoded_message = str.encode(message)
        self.udp_client_socket.sendto(encoded_message, self.server)

    def send_message_with_response(self, message):
        encoded_message = str.encode(message)
        self.udp_client_socket.sendto(encoded_message, self.server)
        return self.receive_message()


def main():
    import time
    server_adr = ("192.168.10.1", 8889)
    user = UDPClient(server_adr)
    inp = "command"
    while inp != "q":
        resp = user.send_message_with_response(inp)
        print(resp)
        inp = str(input("Waiting for command: "))


if __name__ == "__main__":
    main()
