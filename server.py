from datetime import datetime
import re

class Server:
    def __init__(self, data: str):
        server_properties = re.split(",|\x01|\x00", data)
        server_data = {}

        for prop in server_properties:
            if prop.startswith("mp"):
                server_data["max_players"] = int(prop[2:])
            elif prop.startswith("cp"):
                server_data["current_players"] = int(prop[2:])
            elif prop.startswith("born"):
                server_data["map_age"] = int(prop[4:])
            else:
                if "name" not in server_data:
                    server_data["name"] = prop
                elif "map_generator" not in server_data:
                    server_data["map_generator"] = prop

        self.__dict__.update(server_data)

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Server):
            return self.__dict__ == __value.__dict__
        return False

    def get_formatted_age(self) -> str:
        return FormatDelta(datetime.fromtimestamp(self.map_age)).format()
    
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
        return divmod(a, b)

    def format(self) -> str:
        for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
            n = getattr(self, period)
            if n > 1:
                return '{0} ago'.format(self.formatn(n, period))
        return "just now"