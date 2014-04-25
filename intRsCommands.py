import time
from datetime import date
import json

class IntRsCommands:
    readEvent = 0x8C


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

    def get_command_frame(self, cmd):
        crc = self.calculate_crc(cmd)
        result = [0xfe, 0xfe]
        for b in cmd:
            result.append(b)

        result.append(int(crc['crcHigh']))
        result.append(int(crc['crcLow']))
        result.append(0xfe)
        result.append(0x0d)

        return ''.join(chr(b) for b in result)

    def calculate_crc(self, data):
        crc = 0x147A

        for b in data:
            crc = self.ROL(crc, 1)
            crc = crc ^ 0xFFFF
            high, low = divmod(int(crc), 0x100)
            crc = crc + high + b;

        crcHigh, crcLow = divmod(int(crc), 0x100)
        return {'crcHigh': crcHigh, 'crcLow': crcLow}

    def parse_response(self, response):
        frame = [ord(b) for b in response]
        return frame[2: len(frame)-4]

    def ROR(self, x, n):
        mask = (2L**n) - 1
        mask_bits = x & mask
        return (x >> n) | (mask_bits << (16 - n))

    def ROL(self, x, n):
        return self.ROR(x, 16 - n)

    def read_event_list(self, serial_port):
        cmd = self.get_command_frame([self.readEvent, 0xFF, 0xFF, 0xFF])
        serial_port.write(data=cmd)
        time.sleep(1)
        result = self.parse_response(serial_port.read(serial_port.inWaiting()))
        serial_port.close()

        return result

    def decode_event(self, event_frame):
        class Event(): pass

        event = Event()

        if(len(event_frame) == 15):

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
            event.date = str(event_year)+"-"+str(int(month, 2))+"-"+str(int(day, 2))

            time_minutes += '{0:08b}'.format(event_frame[4])
            time_minutes = int(time_minutes, 2)
            event.time = str(time_minutes/60)+":"+str(time_minutes%60)

            binary_byte_5 = '{0:08b}'.format(event_frame[5])
            partition_no = binary_byte_5[0:5]
            restore = binary_byte_5[5]
            event_code = binary_byte_5[6:8]

            event_code += '{0:08b}'.format(event_frame[6])

            source_no = '{0:08b}'.format(event_frame[7])

            binary_byte_8 = '{0:08b}'.format(event_frame[8])
            object_no = binary_byte_8[0:3]
            user_control_no = binary_byte_8[3:8]

            event.index = [hex(event_frame[9]), hex(event_frame[10]), hex(event_frame[11])]
            event.call_index = [hex(event_frame[12]), hex(event_frame[13]), hex(event_frame[14])]

            print json.dumps(event, default=lambda o: o.__dict__)
        else:
            print "Frame does not contain enough elements"