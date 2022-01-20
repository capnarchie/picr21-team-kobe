import asyncio
from ast import literal_eval
from configparser import ConfigParser
import websockets
import json


parser = ConfigParser()


class Server:
    def __init__(self):
        parser.read('config.ini')
        self.host = literal_eval(parser.get('websocket', 'host'))
        self.port = literal_eval(parser.get('websocket', 'port'))
        self.robot = literal_eval(parser.get('robot', 'robot_id'))

    async def send(self, ws, path):
        while True:
            instructions = "Enter a command: 1, 2, 3 or 4 \n 1 - signal: start, targets: ['Io', " + self.robot + \
                           "], baskets: ['magenta', 'blue']\n 2 - signal: start, targets: ['Io', " + self.robot + \
                           "'], baskets: ['blue', 'magenta'] \n 3 - signal: stop, targets: ['Io', " + self.robot + \
                           "] \n 4 - Change ID"

            try:
                cmd = int(await asyncio.get_event_loop().run_in_executor(None, input, instructions))
            except ValueError:
                print("Invalid command")
                continue

            if cmd == 1:
                msg = {
                    "signal": "start",
                    "targets": ["Io", self.robot],
                    "baskets": ["magenta", "blue"]
                }
            elif cmd == 2:
                msg = {
                    "signal": "start",
                    "targets": ["Io", self.robot],
                    "baskets": ["blue", "magenta"]
                }
            elif cmd == 3:
                msg = {
                    "signal": "stop",
                    "targets": ["Io", self.robot]
                }
            elif cmd == 4:
                robot_old = self.robot
                self.robot = ""
                while self.robot == "":
                    try:
                        self.robot = str(await asyncio.get_event_loop().run_in_executor(None, input, "Enter an ID..."))
                        parser.set('robot', 'robot_id', repr(self.robot))
                        with open('config.ini', "w") as f:
                            parser.write(f)
                    except (ValueError, UnicodeError):
                        self.robot = robot_old
                        parser.set('robot', 'robot_id', repr(self.robot))
                        with open('config.ini', "w") as f:
                            parser.write(f)
                        print("Invalid robot id")
                if self.robot == robot_old:
                    continue
                msg = {
                    "signal": "changeID",
                    "targets": [robot_old],
                    "new_robot_id": self.robot
                }
            else:
                print("Invalid command")
                continue

            await ws.send(json.dumps(msg))

    def start(self):
        loop = asyncio.new_event_loop()
        server = websockets.serve(self.send, self.host, self.port, loop=loop, ping_interval=None, ping_timeout=None)
        loop.run_until_complete(server)
        loop.run_forever()


Server().start()
