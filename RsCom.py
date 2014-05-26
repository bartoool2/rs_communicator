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
        mysql.start_app_process()

        # print User.read_user(6, '5272')
        # test = json.loads(data)
        # data = '{"zones":"[1,2]","type":0,"rights_1":4,"rights_2":2,"rights_3":1,"name":"Test"}'

        # User.create_user('5272', data)
        # for value in data['zones']:
        #     print value


        # users = IntegraUser.save_users_list('5272', '1')
        # for user in users:
        #     IntegraUser.save_user("5272", str(user))

        # byte_code = []

        # for i in name:
            # byte_code.append()
            # print chr(i).decode('windows-1250')
            # chr(txt[i]).decode('windows-1250')

        # IntegraEvent.read_later_events(100)
        # string_append = ' append '
        # print string_append + chr(179).decode('windows-1250')
        # User.parse_user_data()

        # for i in range(9, 24):
        #     print i
        #     print Communicator.send_request([i])

        # request = mysql.get_request()
        # print request.additional_data

        # current_event = Event.get_event_by_index([6, 32, 229])
        # print json.dumps(current_event, default=lambda o: o.__dict__)




