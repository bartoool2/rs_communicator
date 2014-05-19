import pymysql
from sqlobject import *
from intRsCommands import *
import json


class MySQL:

    DB_HOST = 's6.jupe.pl'
    DB_USER = 'bstokro'
    DB_PASS = 'KyuG73QK'
    DB_NAME = 'bstokro_intrs'

    QUERY_TYPE_SELECT = 0
    QUERY_TYPE_INSERT = 1

    def __init__(self):
        connection = connectionForURI('mysql://' + MySQL.DB_USER + ':' + MySQL.DB_PASS + '@' + MySQL.DB_HOST + '/' + MySQL.DB_NAME)
        sqlhub.processConnection = connection
        # pass

    # def execute_query(self, query, type):
    #     conn = pymysql.connect(host=MySQL.DB_HOST, port=3306, user=MySQL.DB_USER, passwd=MySQL.DB_PASS, db=MySQL.DB_NAME)
    #
    #     cur = conn.cursor()

        # query = self.insert_builder("intrs_state", {
        #     "command": {"value": command, "type": str},
        #     "value": {"value": value, "type": str},
        # })

        # query = self.update_builder(command, value)
        #
        # print query
        # cur.execute(query)
        # conn.commit()
        #
        # cur.close()
        # conn.close()

    def save_value(self, command, value):
        conn = pymysql.connect(host=MySQL.DB_HOST, port=3306, user=MySQL.DB_USER, passwd=MySQL.DB_PASS, db=MySQL.DB_NAME)

        cur = conn.cursor()

        # query = self.insert_builder("intrs_state", {
        #     "command": {"value": command, "type": str},
        #     "value": {"value": value, "type": str},
        # })

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
            request.status = RequestStackItem.STATUS_DONE
            print 'request done'
        else:
            print 'no event returned'

        zones_to_check = [1, 2, 3, 4]
        for state_code in Communicator.updateZonesState:
            command = Communicator.updateZonesState[state_code]
            zones_affected = Zone.get_affected_zones(command)

            if len(zones_affected) > 0:
                for zone_no in zones_affected:
                    zones_to_check.remove(zone_no)
                    print 'zone_no: ' + str(zone_no)
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

    def start_app_process(self):
        print 'process started'
        while True:
            self.process_next_request()
            time.sleep(5)


class RequestStackItem(SQLObject):

    STATUS_DONE = 1
    STATUS_UNDONE = 0

    CODE_DISARM = 1
    CODE_ARM = 2
    CODE_CLEAR_ALARM = 3

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

