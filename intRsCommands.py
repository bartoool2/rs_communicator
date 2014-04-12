class IntRsCommands:
    zonesViolation = 0x00
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

