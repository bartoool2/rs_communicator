import pymysql


class MySQL:
    def __init__(self):
        pass


    def save_value(self, command, value):
        conn = pymysql.connect(host='s6.jupe.pl', port=3306, user='bstokro_bstokro', passwd='intrs123', db='bstokro_intrs')

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