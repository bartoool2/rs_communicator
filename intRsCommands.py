import time
from datetime import date
import serial
import json
import codecs
import unicodedata as ud


class Communicator:
    selected_port = 0

    readEvent = 0x8C
    readEventTxt = 0x8F

    zonesTamper = 0x01
    zonesTamperAlarm = 0x03
    zonesAlarmMemory = 0x04
    zonesTamperAlarmMemory = 0x05
    zonesBypass = 0x06
    zonesNoViolationTrouble = 0x07
    zonesLongViolationTrouble = 0x08
    armedPartitionsSuppressed = 0x09
    armedPartitionsReally = 0x0A
    partitionsArmedInMode = 0x0B
    partitionsArmedInMode = 0x0C
    partitionsWithFirstCodeEntered = 0x0D
    partitionsEntryTime = 0x0E
    partitionsExitTime = 0x0F
    partitionsExitTime = 0x10
    partitionsTemporaryBlocked = 0x11
    partitionsBlockedForGuardRound = 0x12
    partitionsAlarm = 0x13
    partitionsFireAlarm = 0x14
    partitionsAlarmMemory = 0x15
    partitionsFireAlarmMemory = 0x16
    outputsState = 0x17
    doorsOpened = 0x18
    doorsOpenedLong = 0x19
    RTCAndBasicStatusBits = 0x9A

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
        time.sleep(0.5)
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

    def __init__(self):
        pass

    @staticmethod
    def get_event_by_index(index = [255, 255, 255]):
        request_frame = [Communicator.readEvent] + index
        event_frame = Communicator.send_request(request_frame)
        event = Event()

        if len(event_frame) == 15:
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
            event_class = binary_byte_2[0:3]
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
            event_code = binary_byte_5[6:8]

            event_code += '{0:08b}'.format(event_frame[6])
            event_code = int(event_code, 2)
            event._code_high, event._code_low = divmod(event_code, 0x100)

            source_no = '{0:08b}'.format(event_frame[7])

            binary_byte_8 = '{0:08b}'.format(event_frame[8])
            object_no = binary_byte_8[0:3]
            user_control_no = binary_byte_8[3:8]

            event._index = [event_frame[9], event_frame[10], event_frame[11]]
            event._call_index = [event_frame[12], event_frame[13], event_frame[14]]

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

            return event
        else:
            print "Failed to read frame, retrying..."

        return None

    @staticmethod
    def decode_event_txt(txt):
        result_txt = ''

        if len(txt) >= 22:
            for i in range(6, len(txt)):
                try:
                    result_txt += str(unichr(txt[i]))
                except UnicodeEncodeError:
                    continue

        return result_txt

    @staticmethod
    def read_event_list(events_num = 1):
        current_event = Event.get_event_by_index()
        print json.dumps(current_event, default=lambda o: o.__dict__)

        for i in range(1, events_num):
            if current_event != None:
                current_event = Event.get_event_by_index(current_event._index)
                print json.dumps(current_event, default=lambda o: o.__dict__)
            else:
                break


class Zone(Communicator):

    def __init__(self):
        pass

    @staticmethod
    def get_affected_zones(cmd):
        read_zones = Communicator.send_request([cmd])
        # zones = [0x06, 0x20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x80]
        zones = read_zones[1:len(read_zones)]
        affected_zones = []
        iter = 0

        for byte in zones:
            bits = [int(x) for x in list('{0:08b}'.format(byte))]
            for i in range(0, 8):
                if bits[i] == 1:
                    affected_zones.append(8 - i + iter)
            iter += 8

        return sorted(affected_zones)
