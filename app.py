import socket, re, random, os, json
from datetime import datetime
from time import sleep

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def error_loop(msg: str) -> bool:
    while True:
        clear()
        print(msg)
        i = input("Press enter to try again or type 'exit' to exit: ")
        if i.lower() == "exit":
            return False
        if i == "":
            return True

def get_random_port() -> int:
    return random.randint(64000, 65000)

def ignorecase_equals(a: str, b: str) -> bool:
    return a.lower() == b.lower()

class Server:
    def __init__(self, data: str):
        split_data = re.split(",|\x01|\x00", data)
        for i in range(0, len(split_data)):
            d = split_data[i]
            if i == 0:
                self.name = d
            elif i == 1:
                self.map_generator = d
            elif d.startswith("mp"):
                self.max_players = int(d[2:])
            elif d.startswith("cp"):
                self.current_players = int(d[2:])
            elif d.startswith("born"):
                self.map_age = int(d[4:])

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Server):
            return self.name == __value.name and self.map_generator == __value.map_generator and self.max_players == __value.max_players and self.current_players == __value.current_players and self.map_age == __value.map_age
        return False

    def get_formatted_age(self) -> str:
        return FormatDelta(datetime.fromtimestamp(self.map_age)).format()

class SocketClient:
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1)
        self.socket.bind(("0.0.0.0", get_random_port()))
        self.ip = ip
        self.port = port
    
    def send_packet(self, packet: str) -> bytes:
        self.socket.sendto(bytes.fromhex(packet), (self.ip, self.port))
        data, addr = self.socket.recvfrom(1024)
        return data

    def request_data(self) -> Server:
        payload = "ffffffff54536f7572636520456e67696e6520517565727900"
        payload += self.send_packet(payload).hex()[10:]
        return Server(self.send_packet(payload)[6:-9].decode("utf-8", errors="ignore"))

class FormatDelta:    
    def __init__(self, dt: datetime):
        now = datetime.now()
        delta = now - dt
        self.day = delta.days
        self.second = delta.seconds
        self.year, self.day = self.qnr(self.day, 365)
        self.month, self.day = self.qnr(self.day, 30)
        self.hour, self.second = self.qnr(self.second, 3600)
        self.minute, self.second = self.qnr(self.second, 60)

    def formatn(self, n: int, s: str) -> str:
        if n == 1:
            return "1 %s" % s
        else:
            return "%d %ss" % (n, s)
        
    def qnr(self, a: int, b: int) -> tuple:
        return a / b, a % b

    def format(self) -> str:
        for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
            n = getattr(self, period)
            if n > 1:
                return '{0} ago'.format(self.formatn(n, period))
        return "just now"

class Pager:
    def __init__(self):
        self.servers = []
        self.load()
        self.page = 0

    def save(self):
        with open("servers.json", "w") as f:
            json.dump(self.servers, f)

    def load(self):
        if os.path.exists("servers.json"):
            with open("servers.json", "r") as f:
                self.servers = json.load(f)
        else:
            self.save()

    def add(self, name: str, ip: str, port: int) -> dict:
        data = {"name": name, "ip": ip, "port": port}
        self.servers.append(data)
        self.save()
        return data

    def add_server(self):
        try:
            while True:
                clear()
                name = input("Enter name: ")
                ip = input("Enter IP: ")
                port = input("Enter Query Port: ")
                if name == "" or ip == "" or port == "":
                    if not error_loop("You must enter all fields!"):
                        return None
                    continue
                if not port.isdigit():
                    if not error_loop("Port must be a number!"):
                        return None
                    continue
                port = int(port)
                return self.add(name, ip, port)
        except KeyboardInterrupt:
            return None

    def gui(self):
        clear()
        print()
        print("{:=^50}".format(" Server Pager "))
        print()
        for i in range(0, 8):
            try:
                print("{0}. {1}".format(i + 1, self.servers[i + (self.page * 8)]["name"]))
            except IndexError:
                break
        print()
        if self.page > 0:
            print("-. Previous Page")
        print("0. Add Server")
        if self.page < len(self.servers) // 8:
            print("+. Next Page")
        print()
        print("x. Exit")
        print("Page {0}/{1}".format(self.page + 1, len(self.servers) // 8 + 1))
        print()

    def gui_selector(self):
        selector = input("Select: ")
        if selector == "0":
            return self.add_server()
        if selector == "-":
            self.page -= 1
            return None
        if selector == "+":
            self.page += 1
            return None
        if ignorecase_equals(selector, "x"):
            exit()
        if selector.isdigit():
            try:
                selector = int(selector)
                if selector < 1 or selector > 8:
                    raise IndexError()
                return self.servers[int(selector) - 1 + (self.page * 8)]
            except IndexError:
                if not error_loop("Invalid Selection."):
                    exit()
                return None
        if not error_loop("Invalid Selection."):
            exit()
        return None

    def gui_loop(self):
        chosen = None
        while chosen is None:
            if len(self.servers) == 0:
                chosen = self.add_server()
                if chosen is None:
                    exit()
            self.gui()
            chosen = self.gui_selector()
        return chosen

    def get_delay(self):
        while True:
            delay = input("Enter delay in seconds (default 10): ")
            if delay == "":
                return 10
            elif not delay.isdigit():
                if not error_loop("Invalid input."):
                    exit()
                continue
            elif int(delay) < 1:
                if not error_loop("Invalid input."):
                    exit()
                continue
            return int(delay)

def main():
    pager = Pager()
    selected_server = pager.gui_loop()
    delay = pager.get_delay()
    socket_client = SocketClient(selected_server["ip"], selected_server["port"])
    last_server_info = None
    last_time = datetime.now()
    points = 0
    clear()
    try:        
        while True:
            if (datetime.now() - last_time).seconds > delay:
                last_time = datetime.now()
                server_info = socket_client.request_data()
                if last_server_info is None:
                    last_server_info = server_info
                    ts = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"[{ts}] Added server:")
                    print(f"   Name: {server_info.name}")
                    print(f"   Map Generator: {server_info.map_generator}")
                    print(f"   Map Age: {server_info.get_formatted_age()}")
                    print(f"   Players: {server_info.current_players}/{server_info.max_players}")
                    print()
                elif server_info != last_server_info:
                    last_server_info = server_info
                    ts = datetime.now().strftime("%H:%M:%S")
                    print(f"[{ts}] Server updated:")
                    print(f"   Players: {server_info.current_players}/{server_info.max_players}")
                    print()
            sleep(1)
            points = (points + 1) % 5
            print("Loading" + "." * points + "      ", end="\r")
    except KeyboardInterrupt:
        print("Exiting...                ")
        exit()

if __name__ == "__main__":
    main()