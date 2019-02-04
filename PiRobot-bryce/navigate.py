

class Node:
    def __init__(self, north, east, south, west, x, y):
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.x = x
        self.y = y
        self.explored = False
        self.discovered = False
        self.miniMap = [['x', 'x', 'x', 'x'], ['x', ' ', ' ', ' '], ['x', ' ', '?', ' '], ['x', ' ', ' ', ' ']]
        self.waveNumber = 16 #highest number is 15, 16 is not mapped
        self.colors = []
        
class Navigate(object):
    def __init__(self, startPos, startDirection):
        self.cellStack = []
        self.heading = startDirection
        # base = {'explored': False}
        self.map = [[None, None, None, None], [None, None, None, None], [None, None, None, None], [None, None, None, None]]
        for y in range(0, 4):
            for x in range (0, 4):
                self.map[y][x] = Node(None, None, None, None, x, y)
        self.pos = startPos # is a list with length 2, [0, 0]
        self.mapComplete = False
    def updateHeadingInMap(self, direction):
        #Change stored direction
        if direction == 'right' and self.heading == 'n':
            self.heading = 'e'
        elif direction == 'right' and self.heading == 'e':
            self.heading = 's'
        elif direction == 'right' and self.heading == 's':
            self.heading = 'w'
        elif direction == 'right' and self.heading == 'w':
            self.heading = 'n'
        elif direction == 'left' and self.heading == 'n':
            self.heading = 'w'
        elif direction == 'left' and self.heading == 'e':
            self.heading = 'n'
        elif direction == 'left' and self.heading == 's':
            self.heading = 'e'
        elif direction == 'left' and self.heading == 'w':
            self.heading = 's'

    def orientSensorReadings(self, walls):
        if self.heading == 'n':
            rotations = 0
        elif self.heading == 'e':
            rotations = 3
        elif self.heading == 's':
            rotations = 2
        elif self.heading == 'w':
            rotations = 1
        return walls[rotations:] + walls[:rotations]
        
    def howManyTurnsToFace(self, currentDirection):
        if self.heading == 'n' and currentDirection == 's':
            rotations = 2
        elif self.heading == 's' and currentDirection == 'n':
            rotations = 2
        elif self.heading == 'e' and currentDirection == 'w':
            rotations = 2
        elif self.heading == 'w' and currentDirection == 'e':
            rotations = 2
        else:
            rotations = 1
        return rotations

    def moveForwardInMap(self):
        if self.heading == 'n':
            self.pos[1] += 1
        elif self.heading == 'e':
            self.pos[0] += 1
        elif self.heading == 's':
            self.pos[1] -= 1
        elif self.heading == 'w':
            self.pos[0] -= 1    

    def printMap(self):
        for y in range(3, -1, -1):
            for x in range (0, 4):
                print(self.map[y][x].miniMap[0][0], end="")
                print(self.map[y][x].miniMap[0][1], end="")
                print(self.map[y][x].miniMap[0][2], end="")
                print(self.map[y][x].miniMap[0][3], end="")
            print('x')
            for x in range (0, 4):
                print(self.map[y][x].miniMap[1][0], end="")
                print(self.map[y][x].miniMap[1][1], end="")
                print(self.map[y][x].miniMap[1][2], end="")
                print(self.map[y][x].miniMap[1][3], end="")
            print('x')
            for x in range (0, 4):
                print(self.map[y][x].miniMap[2][0], end="")
                print(self.map[y][x].miniMap[2][1], end="")
                print(self.map[y][x].miniMap[2][2], end="")
                if self.map[y][x].miniMap[2][2] == 'R':
                    self.map[y][x].miniMap[2][2] = ' '
                print(self.map[y][x].miniMap[2][3], end="")
            print('x')
            for x in range (0, 4):
                print(self.map[y][x].miniMap[3][0], end="")
                print(self.map[y][x].miniMap[3][1], end="")
                print(self.map[y][x].miniMap[3][2], end="")
                print(self.map[y][x].miniMap[3][3], end="")
            print('x')
        for i in range(0, 4 * 4):
            print('x', end='')
        print('x')
        print('Heading: ' + self.heading.upper())
        print(self.pos)

    def addCellToMap(self, front, right, back, left):
        # print([front, right, back, left])
        wallArray = self.orientSensorReadings([front, right, back, left])
        # print(wallArray)
        # self.map[self.pos[1]][self.pos[0]].north = wallArray[0]
        # self.map[self.pos[1]][self.pos[0]].east = wallArray[1]
        # self.map[self.pos[1]][self.pos[0]].south = wallArray[2]
        # self.map[self.pos[1]][self.pos[0]].west = wallArray[3]
        self.map[self.pos[1]][self.pos[0]].miniMap[2][2] = 'R' #this is reverted back after printing it
        self.map[self.pos[1]][self.pos[0]].explored = True
        if wallArray[0] and self.pos[1] < 3:
            self.map[self.pos[1]][self.pos[0]].north = self.map[self.pos[1] + 1][self.pos[0]]
            self.map[self.pos[1]][self.pos[0]].miniMap[0][1] = ' '
            self.map[self.pos[1]][self.pos[0]].miniMap[0][2] = ' '
            self.map[self.pos[1]][self.pos[0]].miniMap[0][3] = ' '
            self.discoverCell(self.map[self.pos[1] + 1][self.pos[0]])
        if wallArray[2] and self.pos[1] > 0:
            self.map[self.pos[1]][self.pos[0]].south = self.map[self.pos[1] - 1][self.pos[0]]
            self.discoverCell(self.map[self.pos[1] - 1][self.pos[0]])
            self.map[self.pos[1] - 1][self.pos[0]].miniMap[0][1] = ' '
            self.map[self.pos[1] - 1][self.pos[0]].miniMap[0][2] = ' '
            self.map[self.pos[1] - 1][self.pos[0]].miniMap[0][3] = ' '
        if wallArray[1] and self.pos[0] < 3:
            self.map[self.pos[1]][self.pos[0]].east = self.map[self.pos[1]][self.pos[0] + 1]
            self.discoverCell(self.map[self.pos[1]][self.pos[0] + 1])
            self.map[self.pos[1]][self.pos[0] + 1].miniMap[1][0] = ' '
            self.map[self.pos[1]][self.pos[0] + 1].miniMap[2][0] = ' '
            self.map[self.pos[1]][self.pos[0] + 1].miniMap[3][0] = ' '
        if wallArray[3] and self.pos[0] > 0:
            self.map[self.pos[1]][self.pos[0]].miniMap[1][0] = ' '
            self.map[self.pos[1]][self.pos[0]].miniMap[2][0] = ' '
            self.map[self.pos[1]][self.pos[0]].miniMap[3][0] = ' '
            self.map[self.pos[1]][self.pos[0]].west = self.map[self.pos[1]][self.pos[0] - 1]
            self.discoverCell(self.map[self.pos[1]][self.pos[0] - 1])

    def discoverCell(self, cell):
        if not cell.explored:
            cell.discovered = True
            cell.miniMap[2][2] = '!'

    def getDiscoveredCells(self):
        discoveredList = []

        #if not facing that direction
        if not self.heading == 'n' and self.map[self.pos[1]][self.pos[0]].north and self.map[self.pos[1]][self.pos[0]].north.discovered and not self.map[self.pos[1]][self.pos[0]].north.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].north)
        if not self.heading == 'e' and self.map[self.pos[1]][self.pos[0]].east and self.map[self.pos[1]][self.pos[0]].east.discovered and not self.map[self.pos[1]][self.pos[0]].east.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].east)
        if not self.heading == 's' and self.map[self.pos[1]][self.pos[0]].south and self.map[self.pos[1]][self.pos[0]].south.discovered and not self.map[self.pos[1]][self.pos[0]].south.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].south)
        if not self.heading == 'w' and self.map[self.pos[1]][self.pos[0]].west and self.map[self.pos[1]][self.pos[0]].west.discovered and not self.map[self.pos[1]][self.pos[0]].west.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].west)

        #if facing that direction, should be added last because stack top is in back
        if self.heading == 'n' and self.map[self.pos[1]][self.pos[0]].north and self.map[self.pos[1]][self.pos[0]].north.discovered and not self.map[self.pos[1]][self.pos[0]].north.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].north)
        if self.heading == 'e' and self.map[self.pos[1]][self.pos[0]].east and self.map[self.pos[1]][self.pos[0]].east.discovered and not self.map[self.pos[1]][self.pos[0]].east.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].east)
        if self.heading == 's' and self.map[self.pos[1]][self.pos[0]].south and self.map[self.pos[1]][self.pos[0]].south.discovered and not self.map[self.pos[1]][self.pos[0]].south.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].south)
        if self.heading == 'w' and self.map[self.pos[1]][self.pos[0]].west and self.map[self.pos[1]][self.pos[0]].west.discovered and not self.map[self.pos[1]][self.pos[0]].west.explored:
            discoveredList.append(self.map[self.pos[1]][self.pos[0]].west)
            
        return discoveredList


    def getNeighbors(self):
        neighborList = []

        #if not facing that direction
        if not self.heading == 'n' and self.map[self.pos[1]][self.pos[0]].north:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].north)
        if not self.heading == 'e' and self.map[self.pos[1]][self.pos[0]].east:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].east)
        if not self.heading == 's' and self.map[self.pos[1]][self.pos[0]].south:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].south)
        if not self.heading == 'w' and self.map[self.pos[1]][self.pos[0]].west:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].west)

        #if facing that direction, should be added last because stack top is in back
        if self.heading == 'n' and self.map[self.pos[1]][self.pos[0]].north:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].north)
        if self.heading == 'e' and self.map[self.pos[1]][self.pos[0]].east:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].east)
        if self.heading == 's' and self.map[self.pos[1]][self.pos[0]].south:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].south)
        if self.heading == 'w' and self.map[self.pos[1]][self.pos[0]].west:
            neighborList.append(self.map[self.pos[1]][self.pos[0]].west)
            
        return neighborList


    def hasUnexploredNeighbors(self, cell):
        unexplored = False
        if (cell.north and cell.north.explored == False):
            unexplored = True
        elif (cell.east and cell.east.explored == False):
            unexplored = True
        elif (cell.south and cell.south.explored == False):
            unexplored = True
        elif (cell.west and cell.west.explored == False):
            unexplored = True
        return unexplored

    def getCellDirection(self, cell):
        if cell == self.map[self.pos[1]][self.pos[0]].north:
            return 'n'
        if cell == self.map[self.pos[1]][self.pos[0]].east:
            return 'e'
        if cell == self.map[self.pos[1]][self.pos[0]].south:
            return 's'
        if cell == self.map[self.pos[1]][self.pos[0]].west:
            return 'w'
        else:
            print('whoops, guess these objects can\'t be compared by reference. Or maybe that cell is not adjacent.')
            exit()

    def pushCurrentCellToStack(self):
        self.cellStack.append(self.map[self.pos[1]][self.pos[0]])

    def expressPop(self):
        cell = self.cellStack.pop()
        while len(self.cellStack) > 0 and (not cell.north or cell.north.explored) and (not cell.south or cell.south.explored) and (not cell.east or cell.east.explored) and (not cell.west or cell.west.explored):
            cell = self.cellStack.pop()
        return cell
        
    def clearMap(self):
        self.map = [[None, None, None, None], [None, None, None, None], [None, None, None, None], [None, None, None, None]]
        for y in range(0, 4):
            for x in range (0, 4):
                self.map[y][x] = Node(None, None, None, None, x, y)
        # self.pos = pos
        # self.heading = heading

    def findColor(self, color): #temporary
        for y in range(0, 4):
            for x in range (0, 4):
                if color in self.map[y][x].colors:
                    return self.map[y][x]

    def addColorToCell(self, color):
        # print(self.map[self.pos[1]][self.pos[0]].colors)
        if len(self.map[self.pos[1]][self.pos[0]].colors) == 1:
            # print('(1)ADDING ' + color)
            self.map[self.pos[1]][self.pos[0]].miniMap[3][3] = color[0]
            self.map[self.pos[1]][self.pos[0]].miniMap[1][1] = color[0]
            self.map[self.pos[1]][self.pos[0]].miniMap[1][3] = color[0]
            self.map[self.pos[1]][self.pos[0]].miniMap[3][1] = color[0]
        else:
            # print('(2)ADDING ' + color)
            self.map[self.pos[1]][self.pos[0]].miniMap[2][1] = color[0]
            self.map[self.pos[1]][self.pos[0]].miniMap[2][3] = color[0]
            self.map[self.pos[1]][self.pos[0]].miniMap[1][2] = color[0]
            self.map[self.pos[1]][self.pos[0]].miniMap[3][2] = color[0]

    def setPosition(self, pos, heading):
        self.pos = pos
        self.heading = heading