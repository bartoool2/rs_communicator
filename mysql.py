import pymysql
from sqlobject import *


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
        return RequestStackItem.select(RequestStackItem.q.status==RequestStackItem.STATUS_UNDONE).orderBy("priority DESC, time").limit(1).getOne()

class RequestStackItem(SQLObject):

    class sqlmeta:
         table = "im_request_stack"

    STATUS_DONE = 1
    STATUS_UNDONE = 0

    request_code = StringCol(length=45)
    pass_code = StringCol(length=4)
    status = IntCol(length=1, default=0)
    time = DateTimeCol()
    priority = IntCol(length=3, default=1)


class Zone(SQLObject):

    class sqlmeta:
         table = "im_zone"

