import serial
from mysql import *
from intRsCommands import *
from httpHandler import HTTPServer, HTTPHandler
import json


class RsCom:
    def __init__(self):
        pass

    # rsCom = Communicator()

    def init(self):
        # mysql = MySQL()
        # request = mysql.get_request()
        # print request.id
        self.send_command()
        # handler = HTTPHandler()
        # server = HTTPServer(('192.168.1.101', 8000), HTTPHandler)
        # print('Started http server')
        # server.serve_forever()

    def send_command(self):
        # mysql = MySQL()
        # mysql.save_value(command, command)

        # print 0x7f
        # print Communicator.send_request([0x7f])

        for i in range(0, 32):
            print Zone.get_affected_zones(i)
            # print Communicator.send_request([i])
        # Event.read_event_list(20)
        # Event.get_event_by_index()

        # event = self.rsCom.decode_event([0x8c,
        #     0xbf,
        #     0xcf,
        #     0x42,
        #     0x65,
        #     0x84,
        #     0x13,
        #     0x0,
        #     0x0,
        #     0x6,
        #     0x60,
        #     0xa9,
        #     0xff,
        #     0xff,
        #     0xff])

        # print json.dumps(event, default=lambda o: o.__dict__)




