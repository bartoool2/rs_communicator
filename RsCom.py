import serial
from mysql import MySQL
import time
from intRsCommands import IntRsCommands
from httpHandler import HTTPServer, HTTPHandler


class RsCom:
    def __init__(self):
        pass

    selected_port = 0
    rsCom = IntRsCommands()

    def init(self):
        available_ports = {}
        # self.send_command()
        # handler = HTTPHandler()
        server = HTTPServer(('localhost', 8000), HTTPHandler)
        print('Started http server')
        server.serve_forever()

    def send_command(self):
        # mysql = MySQL()
        # mysql.save_value(command, command)

        serial_port = serial.Serial(port=self.selected_port, baudrate=19200, timeout=5, writeTimeout=5)
        command = self.rsCom.get_command_frame([self.rsCom.zonesViolation])
        serial_port.write(data=command)
        time.sleep(1)
        response = self.rsCom.parse_response(serial_port.read(serial_port.inWaiting()))

        for item in response:
            print hex(item)

        serial_port.close()


