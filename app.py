from datetime import datetime
from time import sleep
from pager import Pager, clear, get_delay
from socketclient import SocketClient
import sys

class ServerMonitor:
    def __init__(self):
        self.pager = Pager()
        self.delay = 0
        self.socket_client = None
        self.last_server_info = None
        self.last_time = datetime.now()
        self.points = 0

    def display_server_info(self, server_info, action):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {action} server:")
        if action != "Updated":
            print(f"   Name: {server_info.name}")
            print(f"   Map Generator: {server_info.map_generator}")
            print(f"   Map Age: {server_info.get_formatted_age()}")
        print(f"   Players: {server_info.current_players}/{server_info.max_players}")
        print()

    def run(self):
        try:
            selected_server = self.pager.gui_loop()
            self.delay = get_delay()
            self.socket_client = SocketClient(selected_server["ip"], selected_server["port"])
            clear()

            while True:
                if (datetime.now() - self.last_time).seconds > self.delay:
                    self.last_time = datetime.now()
                    server_info = self.socket_client.request_data()

                    if self.last_server_info is None:
                        self.last_server_info = server_info
                        self.display_server_info(server_info, "Added")
                    elif server_info != self.last_server_info:
                        self.last_server_info = server_info
                        self.display_server_info(server_info, "Updated")

                self.points = (self.points + 1) % 6
                print("Loading" + "." * self.points + "      ", end="\r")
                sleep(1)

        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()
        except Exception as e:
            print(f"An error has occurred: {e}")
            print("Exiting...")
            sys.exit()

if __name__ == "__main__":
    server_monitor = ServerMonitor()
    server_monitor.run()