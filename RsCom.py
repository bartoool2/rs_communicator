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
        # print User.read_users_list("248", "5272")
        username = [85,191,121,116,107,111,119,110,105,107,32,32,32,49,32,32,0]
        temp_name = ''
        for i in username:
            try:
                # user._name += str(unichr(data[i]))
                temp_name += (chr(i).decode('windows-1250'))
            except:
                continue
        print temp_name

        integra_user = IntegraUser.select(IntegraUser.q.number==1).limit(1).getOne()
        integra_user.name = temp_name.encode('utf8')
        # for user in users:
        #     IntegraUser.save_user("5272", str(user))
        # IntegraUser.save_user("5272", "1")
        # name = [179, 179, 180, 82, 54]

        # byte_code = []

        # for i in name:
            # byte_code.append()
            # print chr(i).decode('windows-1250')
            # chr(txt[i]).decode('windows-1250')

        # Event.read_event_list()
        # string_append = ' append '
        # print string_append + chr(179).decode('windows-1250')
        # mysql.start_app_process()
        # User.parse_user_data()

        # for i in range(9, 24):
        #     print i
        #     print Communicator.send_request([i])

        # request = mysql.get_request()
        # print request.additional_data

        # current_event = Event.get_event_by_index([6, 32, 229])
        # print json.dumps(current_event, default=lambda o: o.__dict__)




