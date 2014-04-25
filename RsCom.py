import serial
from mysql import MySQL
from intRsCommands import IntRsCommands
from httpHandler import HTTPServer, HTTPHandler


class RsCom:
    def __init__(self):
        pass

    selected_port = 0
    rsCom = IntRsCommands()

    def init(self):
        available_ports = {}
        self.send_command()
        # handler = HTTPHandler()
        # server = HTTPServer(('localhost', 8000), HTTPHandler)
        # print('Started http server')
        # server.serve_forever()

    def send_command(self):
        # mysql = MySQL()
        # mysql.save_value(command, command)

        # serial_port = serial.Serial(port=self.selected_port, baudrate=19200, timeout=5, writeTimeout=5)
        # response = self.rsCom.read_event_list(serial_port)
        response = self.rsCom.decode_event([0x8c,
            0xbf,
            0xcf,
            0x42,
            0x65,
            0x84,
            0x13,
            0x0,
            0x0,
            0x6,
            0x60,
            0xa9,
            0xff,
            0xff,
            0xff])

        # response = self.rsCom.parse_response(serial_port.read(serial_port.inWaiting()))

        # for item in response:
        #     print hex(item)




