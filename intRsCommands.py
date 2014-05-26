import json
import time
from datetime import date
import serial


class Communicator:
    selected_port = 0

    readEvent = 0x8C
    readEventTxt = 0x8F

    arm = 0x80
    disarm = 0x84
    clear_alarm = 0x85
    create_user = 0xE6
    update_user = 0xE7

    armedPartitions = 0x0A
    partitionsEntryTime = 0x0E
    partitionsExitTimeOver10Sec = 0x0F
    partitionsExitTimeUnder10Sec = 0x10
    partitionsAlarm = 0x13
    partitionsFireAlarm = 0x14
    partitionsAlarmMemory = 0x15
    partitionsFireAlarmMemory = 0x16

    stateArmed = 2
    stateTimeToEnter = 3
    stateTimeToExit = 4
    stateAlarm = 7
    stateFire = 8
    stateAlarmMemory = 9
    stateFireMemory = 10

    updateZonesState = {
        stateArmed: armedPartitions,
        stateTimeToEnter: partitionsEntryTime,
        stateTimeToExit: partitionsExitTimeOver10Sec,
        stateAlarm: partitionsAlarm,
        stateFire: partitionsFireAlarm,
        stateAlarmMemory: partitionsAlarmMemory,
        stateFireMemory: partitionsFireAlarmMemory
    }

    readUsersList = 0xE2
    readUser = 0xE1

    def __init__(self):
        pass

    def init(self):
        pass

    @staticmethod
    def get_command_frame(cmd):
        crc = Communicator.calculate_crc(cmd)
        result = [0xfe, 0xfe]
        for b in cmd:
            result.append(b)

        result.append(int(crc['crcHigh']))
        result.append(int(crc['crcLow']))
        result.append(0xfe)
        result.append(0x0d)

        return ''.join(chr(b) for b in result)

    @staticmethod
    def calculate_crc(data):
        crc = 0x147A

        for b in data:
            crc = Communicator.ROL(crc, 1)
            crc = crc ^ 0xFFFF
            high, low = divmod(int(crc), 0x100)
            crc = crc + high + b;

        crcHigh, crcLow = divmod(int(crc), 0x100)
        return {'crcHigh': crcHigh, 'crcLow': crcLow}

    @staticmethod
    def parse_response(response):
        frame = [ord(b) for b in response]
        return frame[2: len(frame)-4]

    @staticmethod
    def ROR(x, n):
        mask = (2L**n) - 1
        mask_bits = x & mask
        return (x >> n) | (mask_bits << (16 - n))

    @staticmethod
    def ROL(x, n):
        return Communicator.ROR(x, 16 - n)

    @staticmethod
    def send_request(frame):
        serial_port = serial.Serial(port=Communicator.selected_port, baudrate=19200, timeout=5, writeTimeout=5)
        # print "Serial port opened successfully"

        cmd = Communicator.get_command_frame(frame)

        # print "Sending request..."
        serial_port.write(data=cmd)
        time.sleep(2)
        result = Communicator.parse_response(serial_port.read(serial_port.inWaiting()))
        # print "Response received"

        serial_port.close()
        return result

    @staticmethod
    def system_arm():
        Communicator.send_request()

    # def get_event_txt(self, cmd):


class Event:

    _date = None
    _time = None
    _code_high = None
    _code_low = None
    _index = None
    _call_index = None
    _txt = None
    _class = None

    def __init__(self):
        pass

    @staticmethod
    def get_event_by_index(index = [255, 255, 255]):
        request_frame = [Communicator.readEvent] + index
        event_frame = Communicator.send_request(request_frame)
        event = Event()

        if event_frame[0] == Communicator.readEvent:
            binary_byte_1 = '{0:08b}'.format(event_frame[1])
            year_marker = binary_byte_1[0:2]
            z = binary_byte_1[2]
            e = binary_byte_1[3]
            status2 = binary_byte_1[4:6]
            status1 = binary_byte_1[6:8]
            event_year = date.today().year
            year_diff = int(year_marker, 2) - (event_year%4)
            event_year = event_year + year_diff

            binary_byte_2 = '{0:08b}'.format(event_frame[2])
            event._class = int(binary_byte_2[0:3], 2)
            day = binary_byte_2[3:8]

            binary_byte_3 = '{0:08b}'.format(event_frame[3])
            month = binary_byte_3[0:4]
            time_minutes = binary_byte_3[4:8]
            event._date = str(event_year)+"-"+str(int(month, 2))+"-"+str(int(day, 2))

            time_minutes += '{0:08b}'.format(event_frame[4])
            time_minutes = int(time_minutes, 2)
            event._time = str(time_minutes/60)+":"+str(time_minutes%60)

            binary_byte_5 = '{0:08b}'.format(event_frame[5])
            partition_no = binary_byte_5[0:5]
            restore = binary_byte_5[5]
            event_code = binary_byte_5[5:8]

            event_code += '{0:08b}'.format(event_frame[6])
            event_code = int(event_code, 2)
            event._code_high, event._code_low = divmod(event_code, 0x100)

            source_no = '{0:08b}'.format(event_frame[7])

            binary_byte_8 = '{0:08b}'.format(event_frame[8])
            object_no = binary_byte_8[0:3]
            user_control_no = binary_byte_8[3:8]

            if index[0] == event_frame[-3] and index[1] == event_frame[-2] and index[2] == event_frame[-1]:
                event._index = [event_frame[-6], event_frame[-5], event_frame[-4]]
                event._call_index = [event_frame[-3], event_frame[-2], event_frame[-1]]

                code_high_bitlist = [int(x) for x in list('{0:08b}'.format(event._code_high))]
                code_low_bitlist = [int(x) for x in list('{0:08b}'.format(event._code_low))]
                code_high_bitlist[0] = 1

                event._code_high = 0
                event._code_low = 0

                for bit in code_high_bitlist:
                    event._code_high = (event._code_high << 1) | bit

                for bit in code_low_bitlist:
                    event._code_low = (event._code_low << 1) | bit

                event._txt = Event.decode_event_txt(Communicator.send_request([Communicator.readEventTxt, event._code_high, event._code_low]))
            else:
                print "Failed to read frame index. Frame given:"
                print event_frame
                return None

            return event
        else:
            print "Failed to read frame, retrying..."
            print event_frame

        return None

    @staticmethod
    def decode_event_txt(txt):
        if len(txt) >= 22:
            try:
                return txt[6:len(txt)]
            except UnicodeEncodeError:
                pass

        return []


class Zone:

    def __init__(self):
        pass

    @staticmethod
    def get_affected_zones(cmd):
        read_zones = Communicator.send_request([cmd])
        # zones = [0x06, 0x20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x80]
        zones = read_zones[1:len(read_zones)]
        return Zone.zones_bytes_to_list(zones)

    @staticmethod
    def zones_bytes_to_list(zones):
        affected_zones = []
        iter = 0

        for byte in zones:
            bits = [int(x) for x in list('{0:08b}'.format(byte))]
            for i in range(0, 8):
                if bits[i] == 1:
                    affected_zones.append(8 - i + iter)
            iter += 8

        return sorted(affected_zones)

    @staticmethod
    def disarm_zones(pass_code, zones_list = [1, 2, 3, 4]):
        Zone.manipulate_zones(Communicator.disarm, pass_code, zones_list)

    @staticmethod
    def arm_zones(pass_code, zones_list = [1, 2, 3, 4]):
        Zone.manipulate_zones(Communicator.arm, pass_code, zones_list)

    @staticmethod
    def manipulate_zones(operation, pass_code, zones_list):
        manipulate_frame = [0, 0, 0, 0, 0, 0, 0, 0]
        for zone in zones_list:
            manipulate_frame[8 - zone] = 1

        zones_code = 0
        for bit in manipulate_frame:
                zones_code = (zones_code << 1) | bit

        pass_code_first_part = int('0x' + pass_code[0:2], 16)
        pass_code_second_part = int('0x' + pass_code[2:4], 16)

        Communicator.send_request([operation, pass_code_first_part, pass_code_second_part, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, zones_code, 0x00, 0x00, 0x00])


class User:

    _number = None
    _zones = None
    _type = None
    _rights_1 = None
    _rights_2 = None
    _rights_3 = None
    _name = None

    def __init__(self):
        pass

    @staticmethod
    def read_user(user_number, pass_code):
        pass_code_first_part = int('0x' + pass_code[0:2], 16)
        pass_code_second_part = int('0x' + pass_code[2:4], 16)

        data = Communicator.send_request([Communicator.readUser, pass_code_first_part, pass_code_second_part, 0xFF, 0xFF, int(user_number)])
        user = User()

        user._number = data[1]
        user._zones = Zone.zones_bytes_to_list([data[2], data[3], data[4], data[5]])
        user._type = int(('{0:08b}'.format(data[6]))[4:8], 2)

        user._rights_1 = data[9]
        user._rights_2 = data[10]
        user._rights_3 = data[11]

        user._name = data[12:29]

        return user

    @staticmethod
    def read_users_list(user_number, pass_code):
        pass_code_first_part = int('0x' + pass_code[0:2], 16)
        pass_code_second_part = int('0x' + pass_code[2:4], 16)

        users = Communicator.send_request([Communicator.readUsersList, pass_code_first_part, pass_code_second_part, 0xFF, 0xFF, int(user_number)])

        return Zone.zones_bytes_to_list(users[2:32])

    @staticmethod
    def create_user(pass_code, data):
        pass_code_first_part = int('0x' + pass_code[0:2], 16)
        pass_code_second_part = int('0x' + pass_code[2:4], 16)

        request_frame = [Communicator.create_user, pass_code_first_part, pass_code_second_part, 0, 0,  255, 0x12, 0x34, 0, 0, 0xFF, 0xFF]
        request_frame = User.get_write_frame(request_frame, data)
        request_frame.append(0)

        print request_frame
        Communicator.send_request(request_frame)

    @staticmethod
    def update_user(pass_code, data):
        pass_code_first_part = int('0x' + pass_code[0:2], 16)
        pass_code_second_part = int('0x' + pass_code[2:4], 16)

        request_frame = [Communicator.update_user, pass_code_first_part, pass_code_second_part, 0, 0, 6, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        request_frame = User.get_write_frame(request_frame, data)

        print request_frame
        Communicator.send_request(request_frame)

    @staticmethod
    def get_write_frame(frame, data):
        test = json.loads(data)
        # data = '{"zones":"[1,2]","type":0,"rights_1":4,"rights_2":2,"rights_3":1,"name":"Test"}'
        # test = json.loads(data)

        zones_sum = 0
        for s in test['zones']:
            try:
                zones_sum += int(s)
            except:
                pass

        frame += [zones_sum, 0, 0, 0]
        frame.append(test['type'])
        frame.append(0)
        frame.append(0)
        frame += [test['rights_1'], test['rights_2'], test['rights_3']]

        text = test['name']

        text_bytes = []
        for elem in text:
            text_bytes.append(int(elem.encode('hex'), 16))

        for i in range(0, (16 - len(text))):
            text_bytes.append(32)

        frame += text_bytes

        return frame

