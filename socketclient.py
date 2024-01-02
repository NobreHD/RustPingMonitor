from server import Server
import socket

class SocketClient:
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1)
        self.socket.bind(("0.0.0.0", 0))
        self.ip = ip
        self.port = port
        self._default_payload = "ffffffff54536f7572636520456e67696e6520517565727900"

    def get_bind_port(self) -> int:
        return self.socket.getsockname()[1]

    def _send_receive_packet(self, packet: str) -> bytes:
        self.socket.sendto(bytes.fromhex(packet), (self.ip, self.port))
        data, addr = self.socket.recvfrom(1024)
        return data

    def send_packet(self, packet: str) -> bytes:
        return self._send_receive_packet(packet)

    def request_data(self) -> Server:
        try:
            payload = self._default_payload
            payload += self.send_packet(payload).hex()[10:]
            response = self.send_packet(payload)
            server_data = response[6:-9].decode("utf-8", errors="ignore")
            return Server(server_data)
        except socket.timeout:
            raise ConnectionError("Server not found or unresponsive. Please check your IP and port.")