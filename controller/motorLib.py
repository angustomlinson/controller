from roboclaw import Roboclaw
import re
import enum
import time

DEFAULT_TIME_TO_DELAY_MOTOR = 0.02 # delay for 20 milliseconds
MAX_MOTOR_SPEED = 100 # max speed from client
MAX_MOTOR_POWER = 10000 # max power to motor controllers

class subMessagePrefix(enum.Enum):
    LEFT_MOTOR = 'l'
    RIGHT_MOTOR = 'r'
    ACTUATOR = 'a'
    BUCKET = 'b'
    SERVO = 's'

motorMessageRegex = re.compile('([\w])([-]*[\d]+)\|')

class MotorConnection():
    def __init__(self, communicationPort = '/dev/roboclaw', baudRate = 115200,
                 driveAddress = 0x80, bucketAddress = 0x81):
        print 'MotorConnnection initialized.'
        self.controller = Roboclaw(communicationPort, baudRate)
        self.controller.Open()
        self.driveAddress = driveAddress

        self.bucketAddress = bucketAddress

        self.leftMotorSpeed = 0
        self.rightMotorSpeed = 0
        self.actuatorMotorSpeed = 0
        self.bucketMotorSpeed = 0

    def directionOfSpeed(self, speed):
        if speed >= 0:
            return 1
        else:
            return -1

    def areSpeedDirectionsEqual(self, speed1, speed2):
        if self.directionOfSpeed(speed1) is self.directionOfSpeed(speed2):
            return True
        else:
            return False

    def convertSpeedToPower(self, speed):
        if abs(speed) > MAX_MOTOR_SPEED:
            return 0
        else:
            powerPercentage = float(speed) / float(MAX_MOTOR_SPEED)
            power = int(powerPercentage * float(MAX_MOTOR_POWER))
            return power

    def leftDrive(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.leftMotorSpeed):
            print 'Left motor speed changed direction.'
            self.controller.SpeedM1(self.driveAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Left motor at speed:', speed
        self.leftMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Left motor at power:', power
        self.controller.SpeedM1(self.driveAddress, power)

    def rightDrive(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.rightMotorSpeed):
            print 'Right motor speed changed direction.'
            self.controller.SpeedM2(self.driveAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Right motor at speed:', speed
        self.rightMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Right motor at power:', power
        self.controller.SpeedM2(self.driveAddress, power)

    def bucketActuate(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.actuatorMotorSpeed):
            print 'Actuator motor speed changed direction.'
            self.controller.SpeedM1(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Actuator motor at speed:', speed
        self.actuatorMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Actuator motor at power:', power
        self.controller.SpeedM1(self.bucketAddress, power)

    def bucketRotate(self, speed):
        if not self.areSpeedDirectionsEqual(speed, self.bucketMotorSpeed):
            print 'Bucket motor speed changed direction.'
            self.controller.SpeedM2(self.bucketAddress, 0)
            time.sleep(DEFAULT_TIME_TO_DELAY_MOTOR)

        print 'Bucket motor at speed:', speed
        self.bucketMotorSpeed = speed
        power = self.convertSpeedToPower(speed)
        print 'Bucket motor at power:', power
        self.controller.SpeedM2(self.bucketAddress, power)

    def parseMessage(self, message):
        subMessages = motorMessageRegex.findall(message)

        for subMessage in subMessages:
            motorPrefix = subMessage[0]
            speed = int(subMessage[1])

            if motorPrefix == subMessagePrefix.LEFT_MOTOR:
                self.leftDrive(speed)
            elif motorPrefix == subMessagePrefix.RIGHT_MOTOR:
                self.rightDrive(speed)
            elif motorPrefix == subMessagePrefix.ACTUATOR:
                self.bucketActuate(speed)
            elif motorPrefix == subMessagePrefix.BUCKET:
                self.bucketRotate(speed)
            else:
                print 'MotorPrefix "', motorPrefix, '" unrecognized.'