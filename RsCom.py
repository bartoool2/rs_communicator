import serial
from mysql import *
from intRsCommands import *
from httpHandler import HTTPServer, HTTPHandler
import json


class RsCom:
    def __init__(self):
        pass

    def init(self):
        self.send_command()

    def send_command(self):
        mysql = MySQL()
        IntegraUser.save_user("5272", "1")

        # mysql.start_app_process()
        # User.parse_user_data()

        # for i in range(9, 24):
        #     print i
        #     print Communicator.send_request([i])

        # request = mysql.get_request()
        # print request.additional_data

        # current_event = Event.get_event_by_index([6, 32, 229])
        # print json.dumps(current_event, default=lambda o: o.__dict__)




