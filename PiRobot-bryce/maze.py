import sensors
import servos
import encoders
import time
import navigate
import camera

class Maze(object):
    def __init__(self, startPos, startDirection):
        self.cam = camera.Camera()
        self.sens = sensors.Sensors()
        self.enc = encoders.Encoders()
        self.serv = servos.Servos()
        self.centeredInSquareLength = 7.5
        self.sideDistance = 7.05
        self.distanceBetweenSquares = 18
        self.speed = 7
        self.detectWallDistance = 15
        self.nav = navigate.Navigate(startPos, startDirection)
        self.useColor = False
        self.colorList = []
        self.foundColorList = []
        self.foundColorNorth = False
        self.foundColorEast = False
        self.foundColorSouth = False
        self.foundColorWest = False

    # def __del__(self):
    #     del self.nav
    def enableColor(self, colorList):
        self.useColor = True
        self.foundColorList = []
        self.foundColorNorth = False
        self.foundColorEast = False
        self.foundColorSouth = False
        self.foundColorWest = False
        self.colorList = colorList

    def isWallAhead(self):
        return self.sens.getProxForwardInches() < self.detectWallDistance

    def isWallRight(self):
        return self.sens.getProxRightInches() < self.detectWallDistance

    def isWallLeft(self):
        return self.sens.getProxLeftInches() < self.detectWallDistance

    def isListAscending(self, x, offset):
        return [(x[k+1]-x[k]-offset)>0 for k in range(len(x)-1)].count(True) == len(x)-1

    def isListDescending(self, x, offset):
        return [(x[k+1]-x[k]+offset)<0 for k in range(len(x)-1)].count(True) == len(x)-1

    def isListTrendingUp(self, x, offset):
        # print(sum([(x[k+1]-x[k]) for k in range(len(x)-1)]) / len(x))
        return sum([(x[k+1]-x[k]) for k in range(len(x)-1)]) / len(x) > 0 + offset

    def hardTurn(self, direction):
        omega = 2
        if direction == 'right':
            omega = -omega
        countID = self.enc.newCount(0)
        self.serv.setSpeedsVW(0.00001, omega)
        while (self.enc.getCounts(countID)[0] + self.enc.getCounts(countID)[1]) < 29:
            pass
        self.serv.stopServos()
        self.centerOneDimension()
        self.enc.deleteCount(countID)
        self.nav.updateHeadingInMap(direction)

    def turn(self, direction):
        # if direction == 'left':
        #     print('turning left')
        # else:
        #     print('turning right')
        sensorValues = [0, 0, 0, 0]
        countID = self.enc.newCount(0)
        #scan walls around, decide sensor to monitor
        leftWall = self.isWallLeft()
        rightWall = self.isWallRight()
        frontWall = self.isWallAhead()
        if frontWall and direction == 'left':
            activeSensor = 'right'
        elif frontWall and direction == 'right':
            activeSensor = 'left'
        elif leftWall and direction == 'left':
            activeSensor = 'front'
        elif rightWall and direction == 'right':
            activeSensor = 'front'
        elif rightWall or leftWall: #corresponds to rightWall and left turn, or leftWall and right turn. Basically no sensor.
            activeSensor = 'none'
        elif direction == 'left': #detects no walls
            activeSensor = 'left'
        elif direction == 'right': #detects no walls
            activeSensor = 'right'
        #start first part of turn, hard coded for first part
        omega1 = 2.5
        omega2 = 2.5
        omega3 = 0.6
        if direction == 'right':
            omega1 = -omega1
            omega2 = -omega2
            omega3 = -omega3
        if activeSensor != 'none':
            # print('Initiating first stage of turning: fixed')
            self.serv.setSpeedsVW(0.00001, omega1)
            while self.enc.getCounts(countID)[0] < 10: #used to be 6
                distance = self.sens.getProxInches(activeSensor)
                if distance < 10:
                    sensorValues.append(distance)
            # print('Initiating second stage of turning: look for descending values')
            self.serv.setSpeedsVW(0.00001, omega2)
            while self.isListTrendingUp(sensorValues[-5:], -0.075) and self.enc.getCounts(countID)[0] < 16: #used to be -0.1
                distance = self.sens.getProxInches(activeSensor)
                if distance < 10:
                    sensorValues.append(distance)
            # print('Initiating third stage of turning: look for ascending values')
            self.serv.setSpeedsVW(0.00001, omega3)
            while not self.isListTrendingUp(sensorValues[-5:], 0.035):
                distance = self.sens.getProxInches(activeSensor)
                if distance < 10:
                    sensorValues.append(distance)
            # print('Found ' + str(sensorValues[-6:]))
        else:
            # print('Oh, no, the hard turning case!')
            self.serv.setSpeedsVW(0.00001, omega3 * 1.8)
            while (self.enc.getCounts(countID)[0] + self.enc.getCounts(countID)[1]) < 29:
                pass
        self.serv.stopServos()
        self.centerOneDimension()
        self.enc.deleteCount(countID)
        self.nav.updateHeadingInMap(direction)
    
    def faceDirection(self, newHeading, turnType):
        # print('turning ' + newHeading)
        if turnType == 'sensor':
            if self.nav.heading == 'n' and newHeading == 's'or self.nav.heading == 's' and newHeading == 'n' or self.nav.heading == 'e' and newHeading == 'w' or self.nav.heading == 'w' and newHeading == 'e':
                if self.isWallLeft():
                    self.turn('left')
                    self.turn('left')
                else:
                    self.turn('right')
                    self.turn('right')
            elif self.nav.heading == 'n' and newHeading == 'e' or self.nav.heading == 'e' and newHeading == 's' or self.nav.heading == 's' and newHeading == 'w' or self.nav.heading == 'w' and newHeading == 'n':
                self.turn('right')
            elif self.nav.heading == 'n' and newHeading == 'w' or self.nav.heading == 'e' and newHeading == 'n' or self.nav.heading == 's' and newHeading == 'e' or self.nav.heading == 'w' and newHeading == 's':
                self.turn('left')
        else:
            if self.nav.heading == 'n' and newHeading == 's'or self.nav.heading == 's' and newHeading == 'n' or self.nav.heading == 'e' and newHeading == 'w' or self.nav.heading == 'w' and newHeading == 'e':
                if self.isWallLeft():
                    self.hardTurn('left')
                    self.hardTurn('left')
                else:
                    self.hardTurn('right')
                    self.hardTurn('right')
            elif self.nav.heading == 'n' and newHeading == 'e' or self.nav.heading == 'e' and newHeading == 's' or self.nav.heading == 's' and newHeading == 'w' or self.nav.heading == 'w' and newHeading == 'n':
                self.hardTurn('right')
            elif self.nav.heading == 'n' and newHeading == 'w' or self.nav.heading == 'e' and newHeading == 'n' or self.nav.heading == 's' and newHeading == 'e' or self.nav.heading == 'w' and newHeading == 's':
                self.hardTurn('left')



    def centerOneDimension(self):
        if self.isWallAhead():
            constantKp = 2
            difference = 1
            while (abs(difference) > 0.5):
                difference = self.centeredInSquareLength - self.sens.getProxForwardInches()
                newOutput =  -constantKp * difference #* difference
                self.serv.setSpeedsIPS(newOutput, newOutput)
                time.sleep(0.0025)
            self.serv.stopServos()
        return
    
    def goForward(self):
        # self.enc.resetMainCounts()
        countID = self.enc.newCount(0)
        # print('going straight #' + str(countID))
        countIDstraighten = self.enc.newCount(50) #this one is to keep path straight
        while sum(self.enc.getCountsInInches(countID)) / 2 < self.distanceBetweenSquares: 
            left = self.sens.getProxLeftInches()
            right = self.sens.getProxRightInches()
            # self.centerSideWays(left, right)
            # print(sum(self.enc.getMainCountsInInches()) / 2)
            # if left < 10 and right < 10:
            #     pass #stay eqidistant
            # if left < 16 and right < 16:
            #     self.keepEquidistant(left, right)
            #     self.enc.resetCounts(countIDstraighten)
            if left < 16 and left < right:
                # print('following left')
                self.wallFollowStraight('left')
                self.enc.resetCounts(countIDstraighten)
            elif right < 16 and right < left:
                # print('following right')
                self.wallFollowStraight('right')
                self.enc.resetCounts(countIDstraighten)
            else:
                # print('straightening')
                self.straightenPath(self.speed, self.speed, countIDstraighten)
        self.serv.stopServos()
        self.centerOneDimension()
        self.enc.deleteCount(countID)
        self.enc.deleteCount(countIDstraighten)
        self.nav.moveForwardInMap()
        self.analyzeCell(False)
        if self.useColor:
            self.checkColor()
        self.nav.printMap()
        return
    def keepEquidistant(self, left, right):
        Kp = 0.75
        difference = min(left, right) - self.sideDistance
        omega = difference * Kp
        if omega > 0.5:
            omega = 0.5
        if left < right:
            self.serv.setSpeedsVW(self.speed, omega)
        elif right < left:
            omega = -omega
            difference = right - self.sideDistance
            self.serv.setSpeedsVW(self.speed, omega)
        else:
            self.serv.setSpeedsVW(self.speed, 0)


    def wallFollowStraight(self, side):
        constantKp = 4
        if side == 'left':
            tempKp = -constantKp
            distance = self.sens.getProxLeftInches()
        else:
            tempKp = constantKp
            distance = self.sens.getProxRightInches()
        difference = self.sideDistance - distance
        omega =  tempKp * difference
        if omega > 2 and distance > self.sideDistance:
            omega = 0.15
        elif omega > 1:
            omega = 1
        if omega < -2 and distance > self.sideDistance:
            omega = -0.15
        elif omega < -1:
            omega = -1
        self.serv.setSpeedsVW(self.speed, omega)
        return

    def straightenPath(self, desiredSpeedLeft, desiredSpeedRight, countID):
        ratio = desiredSpeedLeft / desiredSpeedRight
        ticks = self.enc.getCounts(countID)
        if (ticks[1] != 0):
            actualRatio = ticks[0] / ticks[1]
        else:
            actualRatio = 1
        percentError = (actualRatio / ratio - 1) * 100
        if percentError > 1.5:
            # print("Slowing left wheel")
            differential = desiredSpeedRight * 0.5
            self.serv.setSpeedsIPS(desiredSpeedLeft - differential, desiredSpeedRight + differential)
        elif percentError < -1.5:
            # print("Slowing right wheel")
            differential = desiredSpeedLeft * 0.5
            self.serv.setSpeedsIPS(desiredSpeedLeft + differential, desiredSpeedRight - differential)
        else:
            self.serv.setSpeedsIPS(desiredSpeedLeft, desiredSpeedRight)
            if (ticks[0] > 100 or ticks[1] > 100):
                self.enc.subtractCounts(countID, 25)

    def centerTwoDimensions(self):
        self.centerOneDimension()
        if self.isWallLeft():
            self.turn('left')
            self.centerOneDimension()
            self.turn('right')
        elif self.isWallRight():
            self.turn('right')
            self.centerOneDimension()
            self.turn('left')
        # else:
            # print('no wall to the side')

    def centerSideWays(self, left, right):
        if left < 4.5:
            self.turn('left')
            self.centerOneDimension()
            self.turn('right')
        elif right < 4.5:
            self.turn('right')
            self.centerOneDimension()
            self.turn('left')
        # else:
            # print('already in center of lane')
        return
    # def printMap(self):
    #     # self.nav.discoverCell(self.nav.map[1][1])
    #     self.nav.printMap()

    # def face(self, directin): #MAKE THIS

    def analyzeCell(self, first): #must be called after going forward or at start
        if not first:
            self.nav.addCellToMap(not self.isWallAhead(), not self.isWallRight(), True, not self.isWallLeft()) #front, right, behind, left
        else:
            wallAhead = self.isWallAhead()
            wallRight = self.isWallRight()
            wallLeft = self.isWallLeft()
            if self.isWallRight(): #tries to avoid blind turn
                self.turn('right')
                back = not self.isWallRight()
                self.turn('left')
            else:
                self.turn('left')
                back = not self.isWallLeft()
                self.turn('right')
            self.nav.addCellToMap(not wallAhead, not wallRight, back, not wallLeft)
            self.checkColor() #CAN DO THIS WAY BETTER, NO NEED FOR EXTRA TURNS todo
            self.nav.printMap()

    def checkColor(self):
        if len(self.nav.map[self.nav.pos[1]][self.nav.pos[0]].colors) == 0 and len(self.foundColorList) != len(self.colorList) and 'none' not in self.nav.map[self.nav.pos[1]][self.nav.pos[0]].colors:
            if self.nav.pos[1] == 3 and not self.foundColorNorth:
                # print('FACING NORTH')
                self.faceDirection('n', 'hard')
                self.checkAgainstColorList('north')
            if self.nav.pos[1] == 0 and not self.foundColorSouth:
                # print('FACING SOUTH')
                self.faceDirection('s', 'hard')
                self.checkAgainstColorList('south')
            if self.nav.pos[0] == 0 and not self.foundColorWest:
                # print('FACING WEST')
                self.faceDirection('w', 'hard')
                self.checkAgainstColorList('west')
            if self.nav.pos[0] == 3 and not self.foundColorEast:
                # print('FACING EAST')
                self.faceDirection('e', 'hard')
                self.checkAgainstColorList('east')

    def checkAgainstColorList(self, wall): #called in the above function
        addNoColorFlag = True
        for color in self.colorList:
                stats = self.cam.getBlobStatsColored(color)
                if stats['totalArea'] > 50000:
                    self.nav.map[self.nav.pos[1]][self.nav.pos[0]].colors.append(color['name'])
                    self.foundColorList.append(color)
                    self.nav.addColorToCell(color['name'])
                    addNoColorFlag = False
                    if wall == 'north':
                        self.foundColorNorth = True
                    elif wall == 'south':
                        self.foundColorSouth = True
                    elif wall == 'east':
                        self.foundColorEast = True
                    elif wall == 'west':
                        self.foundColorWest = True
                    #HERE, should mark whole row as no color todo
        if addNoColorFlag:
            self.nav.map[self.nav.pos[1]][self.nav.pos[0]].colors.append('none')


        

    def goToNextCell(self):
        discovered = self.nav.getDiscoveredCells()
        if len(discovered) > 0:
            self.faceDirection(self.nav.getCellDirection(discovered[-1]), 'sensor')
            self.nav.pushCurrentCellToStack()
            self.goForward()
            return True
        elif len(discovered) == 0 and len(self.nav.cellStack) > 0:
            nextCell = self.nav.expressPop()
            if self.nav.hasUnexploredNeighbors(nextCell): #get rid of this if/else statement to make it go back to starting cell
                self.goToCell(nextCell)
            else:
                self.nav.mapComplete = True
                return False
            return True
        else:
            self.nav.mapComplete = True
            return False

    def waveNumberCells(self, goalCell, number): #start with 0
        if self.nav.map[goalCell.y][goalCell.x].waveNumber > number:
            self.nav.map[goalCell.y][goalCell.x].waveNumber = number
            if self.nav.map[goalCell.y][goalCell.x].north != None:
                self.waveNumberCells(self.nav.map[goalCell.y][goalCell.x].north, number + 1)
            if self.nav.map[goalCell.y][goalCell.x].east != None:
                self.waveNumberCells(self.nav.map[goalCell.y][goalCell.x].east, number + 1)
            if self.nav.map[goalCell.y][goalCell.x].south != None:
                self.waveNumberCells(self.nav.map[goalCell.y][goalCell.x].south, number + 1)
            if self.nav.map[goalCell.y][goalCell.x].west != None:
                self.waveNumberCells(self.nav.map[goalCell.y][goalCell.x].west, number + 1)

    def clearWaveNumbers(self):
        for x in range(4):
            for y in range(4):
                self.nav.map[y][x].waveNumber = 16

    def FollowWaveNumbers(self):
        targetWaveNumber = 16
        while self.nav.map[self.nav.pos[1]][self.nav.pos[0]].waveNumber != 0:
            if self.nav.map[self.nav.pos[1]][self.nav.pos[0]].north:
                targetCell = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].north
                targetWaveNumber = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].north.waveNumber
            if self.nav.map[self.nav.pos[1]][self.nav.pos[0]].east and self.nav.map[self.nav.pos[1]][self.nav.pos[0]].east.waveNumber < targetWaveNumber:
                targetCell = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].east
                targetWaveNumber = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].east.waveNumber
            if self.nav.map[self.nav.pos[1]][self.nav.pos[0]].south and self.nav.map[self.nav.pos[1]][self.nav.pos[0]].south.waveNumber < targetWaveNumber:
                targetCell = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].south
                targetWaveNumber = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].south.waveNumber
            if self.nav.map[self.nav.pos[1]][self.nav.pos[0]].west and self.nav.map[self.nav.pos[1]][self.nav.pos[0]].west.waveNumber < targetWaveNumber:
                targetCell = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].west
                targetWaveNumber = self.nav.map[self.nav.pos[1]][self.nav.pos[0]].west.waveNumber
            self.faceDirection(self.nav.getCellDirection(targetCell), 'sensor')
            self.goForward()

    def goToCell(self, goal):
        self.waveNumberCells(goal, 0)
        self.FollowWaveNumbers()
        self.clearWaveNumbers()

    def getPosition(self):
        return {
            'pos': self.nav.pos,
            'heading': self.nav.heading
        }

