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
        mysql = MySQL()
        mysql.start_app_process()

        # for i in range(9, 24):
        #     print i
        #     print Communicator.send_request([i])

        # request = mysql.get_request()
        # print request.additional_data

        # current_event = Event.get_event_by_index([6, 32, 229])
        # print json.dumps(current_event, default=lambda o: o.__dict__)




