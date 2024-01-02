from typing import Union
import json, os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def ignorecase_equals(a: str, b: str) -> bool:
    return a.casefold() == b.casefold()

def error_loop(msg: str) -> bool:
    while True:
        clear()
        print(msg)
        i = input("Press enter to try again or type 'exit' to exit: ")
        if i.lower() == "exit":
            return False
        if i == "":
            return True

def get_delay() -> int:
    while True:
        delay = input("Enter delay in seconds (default 10): ")
        if not delay.isdigit():
            if not error_loop("Invalid input."):
                exit()
            continue
        delay = int(delay)
        if delay < 1:
            if not error_loop("Invalid input."):
                exit()
            continue
        return delay

class Pager:
    PAGE_SIZE = 8

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

    def add_server(self) -> Union[dict, None]:
        try:
            while True:
                clear()
                name = input("Enter name: ")
                ip = input("Enter IP: ")
                port = input("Enter Query Port: ")
                if not name or not ip or not port:
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

    def display_servers(self):
        for i, server in enumerate(self.servers[self.page * self.PAGE_SIZE : (self.page + 1) * self.PAGE_SIZE]):
            print(f"{i + 1}. {server['name']}")

    def display_pagination(self):
        print()
        if self.page > 0:
            print("-. Previous Page")
        print("0. Add Server")
        if self.page < (len(self.servers)-1) // self.PAGE_SIZE:
            print("+. Next Page")
        print()
        print("x. Exit")
        print(f"Page {self.page + 1}/{len(self.servers) // self.PAGE_SIZE + 1}")
        print()

    def gui(self):
        clear()
        print()
        print("{:=^50}".format(" Rust Ping Monitor "))
        print()
        self.display_servers()
        self.display_pagination()

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
                if 1 <= selector <= self.PAGE_SIZE:
                    return self.servers[selector - 1 + (self.page * self.PAGE_SIZE)]
                raise IndexError()
            except IndexError:
                if not error_loop("Invalid Selection."):
                    exit()
                return None
        if not error_loop("Invalid Selection."):
            exit()
        return None

    def gui_loop(self):
        try:
            chosen = None
            while chosen is None:
                if not self.servers:
                    chosen = self.add_server()
                    if chosen is None:
                        exit()
                self.gui()
                chosen = self.gui_selector()
            return chosen
        except KeyboardInterrupt:
            print()
            print("Exiting...")
            exit()