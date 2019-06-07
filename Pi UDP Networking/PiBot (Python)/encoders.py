import time
#import Adafruit_PCA9685
import pca9685
import signal
import math
import pprint
import servos
import json
import xlsxwriter
import RPi.GPIO as GPIO
import sensors


class Encoders(object):

    def __init__(self):
        self.velArrayRight = []
        self.velArrayLeft = []
        self.counters = []
        self.counterCount = 0 #number of count instances made so far
        self.startTime = time.time()
        self.speedRecord = 2 #number of values to record in record of speed. Min val is 2. Bigger values are less instantaneous but more reliable.
        self.notMovingTimeout = 1 # time in s before declared as not moving if no encoders ticked. The smaller the value, the less accurate but the higher the response time.
        #for calibration
        self.calibrating = False
        self.wheelTicksLeft = 0
        self.wheelTicksRight = 0
        self.calibrationArrayRight = [] #these two arrays hold values for speed that will be averages for each speed increment and put into the json
        self.calibrationArrayLeft = []
        self.accuracy = 10 #will record speed this number of time and average result
        self.wheelsDiameter = 2.61

        self.graphing = False #set this to true when writing to excel, otherwise should be false. Will not calibrate when true.

        # Set the pin numbering scheme to the numbering shown on the robot itself.
        LENCODER = 17
        RENCODER = 18
        GPIO.setmode(GPIO.BCM)

        # Set encoder pins as input
        # Also enable pull-up resistors on the encoder pins
        # This ensures a clean 0V and 3.3V is always outputted from the encoders.
        GPIO.setup(LENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(RENCODER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Attach a rising edge interrupt to the encoder pins
        GPIO.add_event_detect(LENCODER, GPIO.RISING, self.onLeftEncode)
        GPIO.add_event_detect(RENCODER, GPIO.RISING, self.onRightEncode)
        

        #LEGACY DATA - these are just kept so that old code will run. Avoid using them in the future.
        self.rightTicks = 0
        self.leftTicks = 0
    # This function is called when the left encoder detects a rising edge signal.
    def onLeftEncode(self, pin):
        #print("Left encoder ticked!")
        self.leftTicks += 1
        self.incrementAllCounts('left')
        self.velArrayLeft.append((time.time(), self.leftTicks))
        if (len(self.velArrayLeft) > self.speedRecord):
            self.velArrayLeft = self.velArrayLeft[1:(self.speedRecord + 1)]
        if (self.calibrating):
            self.wheelTicksLeft += 1
            self.calibrationArrayLeft.append(self.getSpeeds()[0]) #append current left speed to array

    # This function is called when the right encoder detects a rising edge signal.
    def onRightEncode(self, pin):
        #print("Right encoder ticked!")
        self.rightTicks += 1
        self.incrementAllCounts('right')
        self.velArrayRight.append((time.time(), self.rightTicks))
        if (len(self.velArrayRight) > self.speedRecord):
            self.velArrayRight = self.velArrayRight[1:(self.speedRecord + 1)]
        if (self.calibrating):
            self.wheelTicksRight += 1
            self.calibrationArrayRight.append(self.getSpeeds()[1]) #append current right speed to array

    def incrementAllCounts(self, side):
        for count in self.counters:
            count[side] += 1

    def newCount(self, base):
        number = self.counterCount
        self.counterCount += 1
        self.counters.append({'number': number, 'left': base, 'right': base, 'base': base})
        return number

    def resetCounts(self, number):
        for count in self.counters:
            if count['number'] == number:
                count['left'] = count['base']
                count['right'] = count['base']
                break

    def subtractCounts(self, number, sub):
        for count in self.counters:
            if count['number'] == number:
                count['left'] -= sub
                count['right'] -= sub
                break
        
    def resetTime(self):
        self.startTime = time.time()

    def getCounts(self, number):
        for count in self.counters:
            if count['number'] == number:
                return (count['left'], count['right'])

    def deleteCount(self, number):
        self.counters = [x for x in self.counters if x['number'] != number]
    
    def getCountsInInches(self, number):
        for count in self.counters:
            if count['number'] == number:
                return (count['left'] / 32 * self.wheelsDiameter * math.pi, count['right'] / 32 * self.wheelsDiameter * math.pi)

    def getSpeeds(self):
        totalTime = self.getElapsedTime()
        moving = self.isSpeedZero()
        leftLength = len(self.velArrayLeft)
        rightLength = len(self.velArrayRight)
        if rightLength > 0 and leftLength > 0 and totalTime > 0:
            if ((self.velArrayLeft[leftLength - 1][0] - self.velArrayLeft[0][0]) > 0 and (self.velArrayRight[rightLength - 1][0] - self.velArrayRight[0][0]) > 0):
                speedLeft = (self.velArrayLeft[leftLength - 1][1] - self.velArrayLeft[0][1]) / (self.velArrayLeft[leftLength - 1][0] - self.velArrayLeft[0][0])
                speedRight = (self.velArrayRight[rightLength - 1][1] - self.velArrayRight[0][1]) / (self.velArrayRight[rightLength - 1][0] - self.velArrayRight[0][0])
            else:
                return (0, 0)
            return (speedLeft / 32 * moving[0], speedRight / 32 * moving[1])
        elif leftLength > 1 and totalTime > 0: # or not moving[1]:
            return ((self.velArrayLeft[leftLength - 1][1] - self.velArrayLeft[0][1]) / (self.velArrayLeft[leftLength - 1][0] - self.velArrayLeft[0][0]) / 32, 0)
        elif rightLength > 1 and totalTime > 0: #  not moving[0]:
            return (0, (self.velArrayRight[rightLength - 1][1] - self.velArrayRight[0][1]) / (self.velArrayRight[rightLength - 1][0] - self.velArrayRight[0][0]) / 32)
        else:
            return (0, 0)

    def getElapsedTime(self):
        return time.time() - self.startTime
    def isSpeedZero(self): #returns 0 for stopped, 1 for moving as a tuple (left, right)
        rightMoving = 1
        leftMoving = 1
        if (len(self.velArrayLeft) > 0):
            timeSinceLeft = time.time() - self.velArrayLeft[len(self.velArrayLeft) - 1][0]
        else:
            timeSinceLeft = 0
        if (len(self.velArrayRight) > 0):
            timeSinceRight = time.time() - self.velArrayRight[len(self.velArrayRight) - 1][0]
        else:
            timeSinceRight = 0
        if timeSinceRight > self.notMovingTimeout:
            rightMoving = 0
        if timeSinceLeft > self.notMovingTimeout:
            leftMoving = 0
        return (leftMoving, rightMoving)


    def calibrateSpeeds(self):
        calServ = servos.Servos()
        self.wheelTicksLeft = 0
        self.wheelTicksRight = 0
        self.calibrating = True
        print('Starting calibration...')
        if(self.graphing):
            excelDataRight = [] #data to plot in excel
            excelDataLeft = []
        else:
            calibrationData = {} #dictionary containing calibration data
            calibrationData['left'] = {}
            calibrationData['right'] = {}
        rightStage = 1.2 #PWM freq for right
        leftStage = 1.8 #PWM freq for left
        print('CCW stage beginning...')
        while (rightStage < 1.5 and leftStage > 1.5):
            print('Collecting data for (' + str(leftStage) + ', ' + str(rightStage) + ')...')
            calServ.setSpeeds(leftStage, rightStage)
            print('Waiting for ticks...')
            while(self.wheelTicksLeft < self.accuracy + 1 and self.wheelTicksRight < self.accuracy + 1): #while loop is just to wait for more ticks
                pass
            print('Got the ticks!')
            averageSpeedLeft = sum(self.calibrationArrayLeft[-self.accuracy:]) / self.accuracy #averages last x elements of left array, left out first because it may not be accurate
            averageSpeedRight = sum(self.calibrationArrayRight[-self.accuracy:]) / self.accuracy #averages last x elements of right array
            if(self.graphing):
                excelDataRight.append((rightStage, -averageSpeedRight))
                excelDataLeft.append((leftStage, averageSpeedLeft))
            else:
                calibrationData['left'][averageSpeedLeft] = leftStage
                calibrationData['right'][-averageSpeedRight] = rightStage
            print('Average speed left: ' + str(averageSpeedLeft))
            print('Average speed right: ' + str(averageSpeedRight))
            #empty everything and reset for next stage
            self.calibrationArrayLeft = []
            self.calibrationArrayRight = []
            self.wheelTicksLeft = 0
            self.wheelTicksRight = 0
            if leftStage > 1.6 and rightStage < 1.4:
                rightStage += 0.0025
                leftStage -= 0.0025
            elif(leftStage > 1.505 and rightStage < 1.495): #would be miserable going slower than this, and this is the easy direction to spin so the requirements are closer to 1.5 than next stage
                rightStage += 0.001
                leftStage -= 0.001
            else:
                rightStage = 1.5
                leftStage = 1.5
        #reset for another run in the opposite direction
        print('CW stage beginning...')
        rightStage = 1.8 #PWM freq for right
        leftStage = 1.2 #PWM freq for left
        while (rightStage > 1.5 and leftStage < 1.5):
            print('Collecting data for (' + str(leftStage) + ', ' + str(rightStage) + ')...')
            calServ.setSpeeds(leftStage, rightStage)
            print('Waiting for ticks...')
            while(self.wheelTicksLeft < self.accuracy + 1 and self.wheelTicksRight < self.accuracy + 1): #while loop is just to wait for more ticks
                pass
            print('Got the ticks!')
            averageSpeedLeft = sum(self.calibrationArrayLeft[-self.accuracy:]) / self.accuracy #averages last x elements of left array, left out first because it may not be accurate
            averageSpeedRight = sum(self.calibrationArrayRight[-self.accuracy:]) / self.accuracy #averages last x elements of right array
            if(self.graphing):
                excelDataRight.append((rightStage, averageSpeedRight))
                excelDataLeft.append((leftStage, -averageSpeedLeft))
            else:
                calibrationData['left'][-averageSpeedLeft] = leftStage
                calibrationData['right'][averageSpeedRight] = rightStage
            print('Average speed left: ' + str(averageSpeedLeft))
            print('Average speed right: ' + str(averageSpeedRight))
            #empty everything and reset for next stage
            self.calibrationArrayLeft = []
            self.calibrationArrayRight = []
            self.wheelTicksLeft = 0
            self.wheelTicksRight = 0
            if leftStage < 1.4 and rightStage > 1.6:
                rightStage -= 0.0025
                leftStage += 0.0025
            elif(leftStage < 1.493 and rightStage > 1.507): #would be miserable going slower than this
                rightStage -= 0.001
                leftStage += 0.001
            else:
                rightStage = 1.5
                leftStage = 1.5
        print('Turning off servos.')
        calServ.stopServos()
        #write to file
        if (self.graphing):
            workbook = xlsxwriter.Workbook('calibrationData.xlsx')
            worksheet = workbook.add_worksheet()
            col = 0
            row = 0
            for item in excelDataLeft:
                worksheet.write(row, col, item[0])
                worksheet.write(row, col + 1, item[1])
                row += 1
            col = 4
            row = 0
            for item in excelDataRight:
                worksheet.write(row, col, item[0])
                worksheet.write(row, col + 1, item[1])
                row += 1
            workbook.close()
        else:
            with open('calibration.json', 'w') as writeFile:
                json.dump(calibrationData, writeFile, indent=4, separators=(',',': '), sort_keys=True)
        self.calibrating = False
        self.wheelTicksLeft = 0
        self.wheelTicksRight = 0

    #LEGACY FUNCTIONS - these are just kept so that old code will run. Avoid using them in the future.
    def resetMainCounts(self):
        self.rightTicks = 0
        self.leftTicks = 0

    def subtractMainCounts(self, sub): # will increase accuracy
        self.rightTicks -= sub
        self.leftTicks -= sub

    def getMainCounts(self):
        return (self.leftTicks, self.rightTicks)

    def getMainCountsInInches(self):
        return (self.leftTicks / 32 * self.wheelsDiameter * math.pi, self.rightTicks / 32 * self.wheelsDiameter * math.pi)

    def getDistanceTraveledRPS(self):
        return (self.leftTicks / 32, self.rightTicks / 32)
    