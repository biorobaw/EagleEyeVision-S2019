import time
import sys
sys.path.append('/home/pi/VL53L0X_rasp_python/python')
import VL53L0X
import RPi.GPIO as GPIO
class Sensors(object):
    def __init__(self):
        # Pins that the sensors are connected to
        LSHDN = 27
        FSHDN = 22
        RSHDN = 23

        DEFAULTADDR = 0x29 # All sensors use this address by default, don't change this
        LADDR = 0x2a
        RADDR = 0x2b

        # Set the pin numbering scheme to the numbering shown on the robot itself.
        GPIO.setmode(GPIO.BCM)

        # Setup pins
        GPIO.setup(LSHDN, GPIO.OUT)
        GPIO.setup(FSHDN, GPIO.OUT)
        GPIO.setup(RSHDN, GPIO.OUT)

        # Shutdown all sensors
        GPIO.output(LSHDN, GPIO.LOW)
        GPIO.output(FSHDN, GPIO.LOW)
        GPIO.output(RSHDN, GPIO.LOW)

        time.sleep(0.01)

        # Initialize all sensors
        self.lSensor = VL53L0X.VL53L0X(address=LADDR)
        self.fSensor = VL53L0X.VL53L0X(address=DEFAULTADDR)
        self.rSensor = VL53L0X.VL53L0X(address=RADDR)

        # Connect the left sensor and start measurement
        GPIO.output(LSHDN, GPIO.HIGH)
        time.sleep(0.01)
        self.lSensor.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)

        # Connect the right sensor and start measurement
        GPIO.output(RSHDN, GPIO.HIGH)
        time.sleep(0.01)
        self.rSensor.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)

        # Connect the front sensor and start measurement
        GPIO.output(FSHDN, GPIO.HIGH)
        time.sleep(0.01)
        self.fSensor.start_ranging(VL53L0X.VL53L0X_GOOD_ACCURACY_MODE)

    def getProxForward(self):
        return self.fSensor.get_distance()
    def getProxRight(self):
        return self.rSensor.get_distance()
    def getProxLeft(self):
        return self.lSensor.get_distance()

    def getProxForwardInches(self):
        return self.getProxForward() * 0.393701 / 10
    def getProxRightInches(self):
        return self.getProxRight() * 0.393701 / 10
    def getProxLeftInches(self):
        return self.getProxLeft() * 0.393701 / 10

    def getProxInches(self, side):
        if side == 'right':
            return self.getProxRightInches()
        if side == 'left':
            return self.getProxLeftInches()
        if side == 'front':
            return self.getProxForwardInches()

    def stopRanging(self):
        self.lSensor.stop_ranging()
        self.fSensor.stop_ranging()
        self.rSensor.stop_ranging()
