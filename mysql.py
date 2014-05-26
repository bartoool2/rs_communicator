import pymysql
from sqlobject import *
from intRsCommands import *
import json


class MySQL:

    DB_HOST = 's6.jupe.pl'
    DB_USER = 'bstokro'
    DB_PASS = 'KyuG73QK'
    DB_NAME = 'bstokro_intrs'

    MAX_ZONES_STEP = 15
    MAX_USERS_STEP = 25

    QUERY_TYPE_SELECT = 0
    QUERY_TYPE_INSERT = 1

    UNICODE_TRANSLATIONS = {
        185: 0x61,
        230: 0x63,
        234: 0x65,
        179: 0x6c,
        241: 0x6e,
        243: 0x6f,
        156: 0x73,
        159: 0x7a,
        191: 0x7a,
        165: 0x41,
        198: 0x43,
        202: 0x45,
        163: 0x4c,
        209: 0x4e,
        211: 0x4f,
        140: 0x53,
        143: 0x5a,
        175: 0x5a
    }

    def __init__(self):
        connection = connectionForURI('mysql://' + MySQL.DB_USER + ':' + MySQL.DB_PASS + '@' + MySQL.DB_HOST + '/' + MySQL.DB_NAME)
        sqlhub.processConnection = connection

    def save_value(self, command, value):
        conn = pymysql.connect(host=MySQL.DB_HOST, port=3306, user=MySQL.DB_USER, passwd=MySQL.DB_PASS, db=MySQL.DB_NAME)

        cur = conn.cursor()

        query = self.update_builder(command, value)

        print query
        cur.execute(query)
        conn.commit()

        cur.close()
        conn.close()

    def select_builder(self, table, where_clause):
        return "SELECT * FROM " + table + " WHERE " + where_clause

    def insert_builder(self, table, args):
        query = "INSERT INTO " + table + " ("
        values_string = ""

        iteration = 0
        for key in args:
            if iteration > 0:
                query += ", "
                values_string += ", "
            query += key
            if args[key]["type"] != str:
                values_string += args[key]["value"]
            else:
                values_string += "'" + args[key]["value"] + "'"
            iteration += 1

        query += ") VALUES (" + values_string + ")"
        return query

    def update_builder(self, command, value):
        return "UPDATE intrs_state SET value='" + value + "' WHERE command='" + command + "'"

    def get_request(self):
        result = None

        try:
            result = RequestStackItem.select(RequestStackItem.q.status==RequestStackItem.STATUS_UNDONE).orderBy("priority DESC, time").limit(1).getOne()
        except:
            pass

        return result

    def process_next_request(self):
        request = self.get_request()
        if request != None:
            if request.request_code == RequestStackItem.CODE_DISARM:
                print 'disarm zones request received'
                try:
                    Zone.disarm_zones(request.pass_code, json.loads(request.additional_data))
                except Exception:
                    pass
            elif request.request_code == RequestStackItem.CODE_ARM:
                print 'arm zones request received'
                try:
                    Zone.arm_zones(request.pass_code, json.loads(request.additional_data))
                except Exception:
                    pass
            elif request.request_code == RequestStackItem.CODE_READ_USERS_LIST:
                print 'read users list request received'
                try:
                    IntegraUser.save_users_list(request.pass_code, json.loads(request.additional_data))
                except Exception:
                    pass
            elif request.request_code == RequestStackItem.CODE_CREATE_USER:
                print 'create user request received'
                try:
                    IntegraUser.create_user(request.pass_code, request.additional_data)
                except Exception:
                    pass
            elif request.request_code == RequestStackItem.CODE_UPDATE_USER:
                print 'update user request received'
                try:
                    IntegraUser.update_user(request.pass_code, request.additional_data)
                except Exception:
                    pass
            request.status = RequestStackItem.STATUS_DONE
            print 'request done'
            return True
        else:
            print 'no event returned'
            return False

    @staticmethod
    def decode_string(byte_list):
        temp_name = ''

        for byte in byte_list:
            if byte in MySQL.UNICODE_TRANSLATIONS:
                temp_name += chr(MySQL.UNICODE_TRANSLATIONS[byte]).decode('windows-1250')
            else:
                temp_name += chr(byte).decode('windows-1250')

        return temp_name.strip()

    def start_app_process(self):
        print 'process started'
        update_zones_step = 0
        update_users_step = 0

        while True:
            update_zones_step += 1
            update_users_step += 1

            request_received = self.process_next_request()
            time.sleep(5)

            if update_zones_step == MySQL.MAX_ZONES_STEP and request_received is False:
                print 'updating zones info'
                zones_to_check = [1, 2, 3, 4]
                update_zones_step = 0

                for state_code in Communicator.updateZonesState:
                    command = Communicator.updateZonesState[state_code]
                    zones_affected = Zone.get_affected_zones(command)

                    if len(zones_affected) > 0:
                        for zone_no in zones_affected:
                            if zone_no in zones_to_check:
                                zones_to_check.remove(zone_no)
                            try:
                                found_zone = ZoneItem.select(ZoneItem.q.number==zone_no).limit(1).getOne()
                                found_zone.status = state_code
                            except:
                                pass

                for checked_zone_no in zones_to_check:
                    try:
                        zone = ZoneItem.select(ZoneItem.q.number==checked_zone_no).limit(1).getOne()
                        zone.status = ZoneItem.STATE_DISARMED
                    except:
                        pass
                print 'zones info updated'

            if update_users_step == MySQL.MAX_USERS_STEP and request_received is False:
                print 'updating users info'
                update_users_step = 0
                if update_zones_step == 0:
                    time.sleep(5)

                # try:
                    users = IntegraUser.save_users_list("5272", str(255))

                    for user in users:
                        IntegraUser.save_user("5272", user)
                # except:
                #     pass

                print 'users info updated'

class IntegraEvent(SQLObject):

    index_1 = IntCol(length=11)
    index_2 = IntCol(length=11)
    index_3 = IntCol(length=11)
    call_index_1 = IntCol(length=11)
    call_index_2 = IntCol(length=11)
    call_index_3 = IntCol(length=11)
    date = DateCol()
    time = TimeCol()
    description = StringCol(length=100)
    event_class = IntCol(length=11)

    class sqlmeta:
         table = "im_events"

    @staticmethod
    def read_event_list(events_num = 1):
        current_event = Event.get_event_by_index()
        IntegraEvent(index_1=current_event._index[0], index_2=current_event._index[1], index_3=current_event._index[2],
                     call_index_1=current_event._call_index[0], call_index_2=current_event._call_index[1], call_index_3=current_event._call_index[2],
                     date=current_event._date, time=current_event._time+":00", description=MySQL.decode_string(current_event._txt), event_class=current_event._class)

        for i in range(1, events_num):
            if current_event != None:
                current_event = Event.get_event_by_index(current_event._index)
                IntegraEvent(index_1=current_event._index[0], index_2=current_event._index[1], index_3=current_event._index[2],
                     call_index_1=current_event._call_index[0], call_index_2=current_event._call_index[1], call_index_3=current_event._call_index[2],
                     date=current_event._date, time=current_event._time+":00", description=MySQL.decode_string(current_event._txt), event_class=current_event._class)
            else:
                break

    @staticmethod
    def read_later_events(events_num=1):
        first_event = IntegraEvent.select().orderBy('id DESC').limit(1).getOne()

        list = []
        list.append(int(first_event.index_1))
        list.append(int(first_event.index_2))
        list.append(int(first_event.index_3))

        current_event = Event.get_event_by_index(list)
        IntegraEvent(index_1=current_event._index[0], index_2=current_event._index[1], index_3=current_event._index[2],
                     call_index_1=current_event._call_index[0], call_index_2=current_event._call_index[1], call_index_3=current_event._call_index[2],
                     date=current_event._date, time=current_event._time+":00", description=MySQL.decode_string(current_event._txt), event_class=current_event._class)

        for i in range(1, events_num):
            if current_event != None:
                current_event = Event.get_event_by_index(current_event._index)
                IntegraEvent(index_1=current_event._index[0], index_2=current_event._index[1], index_3=current_event._index[2],
                     call_index_1=current_event._call_index[0], call_index_2=current_event._call_index[1], call_index_3=current_event._call_index[2],
                     date=current_event._date, time=current_event._time+":00", description=MySQL.decode_string(current_event._txt), event_class=current_event._class)
            else:
                break


class RequestStackItem(SQLObject):

    STATUS_DONE = 1
    STATUS_UNDONE = 0

    CODE_DISARM = 1
    CODE_ARM = 2
    CODE_CLEAR_ALARM = 3
    CODE_READ_USERS_LIST = 4
    CODE_CREATE_USER = 5
    CODE_UPDATE_USER = 6

    request_code = IntCol(length=4)
    pass_code = StringCol(length=4)
    additional_data = StringCol(length=100)
    status = IntCol(length=1, default=0)
    time = DateTimeCol()
    priority = IntCol(length=3, default=1)

    class sqlmeta:
         table = "im_request_stack"


class ZoneItem(SQLObject):

    STATE_DISARMED = 1
    STATE_ARMED = 2
    STATE_TIME_TO_ENTER = 3
    STATE_TIME_TO_EXIT = 4
    STATE_ALARM = 7
    STATE_FIRE = 8
    STATE_ALARM_MEMORY = 9
    STATE_FIRE_MEMORY = 10

    number = IntCol(length=4)
    name = StringCol(length=45)
    status = IntCol(length=3)

    class sqlmeta:
         table = "im_zones"


class IntegraUser(SQLObject):

    number = IntCol(length=4)
    type = IntCol(length=3)
    name = UnicodeCol(length=20)
    rights_1 = IntCol(length=11)
    rights_2 = IntCol(length=11)
    rights_3 = IntCol(length=11)
    zones = StringCol(length=45)

    class sqlmeta:
        table = "im_integra_users"

    @staticmethod
    def save_users_list(pass_code, data):
        users = User.read_users_list(data, pass_code)

        for user in users:
            try:
                IntegraUser(number=user, type=None, name=None)
            except:
                pass

        return users

    @staticmethod
    def save_user(pass_code, data):
        user = User.read_user(data, pass_code)

        print user._name
        integra_user = IntegraUser.select(IntegraUser.q.number==user._number).limit(1).getOne()
        integra_user.type = user._type
        integra_user.name = MySQL.decode_string(user._name)
        integra_user.rights_1 = user._rights_1
        integra_user.rights_2 = user._rights_2
        integra_user.rights_3 = user._rights_3
        integra_user.zones = str(user._zones)

    @staticmethod
    def create_user(pass_code, data):
        User.create_user(pass_code, data)

    @staticmethod
    def update_user(pass_code, data):
        User.update_user(pass_code, data)

