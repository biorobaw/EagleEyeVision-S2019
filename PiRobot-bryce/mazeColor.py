import time
import RPi.GPIO as GPIO
import signal
import maze
import servos
import sys


#colors
colorList = []
# testRed = {'minH': 169, 'maxH': 180, 'minS': 124, 'maxS': 180, 'minV': 32, 'maxV': 103, 'name': 'pink'}
# colorList.append(testRed)
pink = {'minH': 152, 'minS': 120, 'minV': 85, 'maxH': 180, 'maxS': 255, 'maxV': 255, 'name': 'pink'}
colorList.append(pink)

yellow = {'minH': 17, 'minS': 235, 'minV': 129, 'maxH': 35, 'maxS': 255, 'maxV': 207, 'name': 'yellow'}
colorList.append(yellow)

green = {'minH': 29, 'minS': 209, 'minV': 79, 'maxH': 51, 'maxS': 255, 'maxV': 208, 'name': 'green'}
colorList.append(green)

# blue = {'minH': 0, 'minS': 0, 'minV': 52, 'maxH': 111, 'maxS': 58, 'maxV': 207, 'name': 'blue'}
blue = {'minH': 57, 'minS': 44, 'minV': 77, 'maxH': 109, 'maxS': 160, 'maxV': 171, 'name': 'blue'}
colorList.append(blue)
#objects for servos, encoders, sensors, and camera
serv = servos.Servos()


def ctrlC(signum, frame):
    print("Exiting")
    serv.stopServos()
    # sens.stopRanging()
    GPIO.cleanup()
    exit()
signal.signal(signal.SIGINT, ctrlC)

def mainMenu(options):
    selection = input('(P) Change Robot Position. Enter as <P x y heading>.\n(M) Create new map. Enter as <M>.\n(C) Choose to find pink, yellow, green, or blue. Enter as <C color>.\n(E) Exit. Enter as <E>\nEnter selection: ')
    selection = selection.split(' ')
    if selection[0].lower() == 'p':
        try:
            pos = [int(selection[1]), int(selection[2])]
        except ValueError:
            print('Error: x and y must be integers')
            return options
        if pos[0] > 3 or pos[0] < 0 or pos[1] > 3 or pos[1] < 0:
            print('Error: positions must be 0, 1, 2, or 3')
            return options
        heading = selection[3].lower()
        if heading != 'n' and heading != 's' and heading != 'e' and heading != 'w':
            print('Error: heading must be N, E, S, or W')
            return options
        options['pos'] = pos
        options['heading'] = heading
        print('Position set!')
    elif selection[0].lower() == 'm':
        if (options['heading'] == 'unknown' or options['pos'] == (-1, -1)):
            print('Error: must set position first')
        else:
            options['readyToMap'] = True
            print('Mapping...')
    elif selection[0].lower() == 'c':
        if options['mapped']:
            if selection[1].lower() == 'pink':
                options['color'] = 'pink'
                print('Color set!')     
            elif selection[1].lower() == 'yellow':
                options['color'] = 'yellow'
                print('Color set!')
            elif selection[1].lower() == 'green':
                options['color'] = 'green'
                print('Color set!')
            elif selection[1].lower() == 'blue':
                options['color'] = 'blue'
                print('Color set, plotting...')
            else:
                print('Error: color must be pink, yellow, green, or blue')
        else:
            print('Error: must construct map first')
    elif selection[0].lower() == 'e':
        exit()
    else:
        print('Error: must select P, M, C, or E')
    return options



# if len(sys.argv) != 4:
#     sys.exit('Error: navigateMaze.py requires 3 arguments: x position, y position, and heading')
# try:
#     pos = [int(sys.argv[1]), int(sys.argv[2])]
# except ValueError:
#     sys.exit('Error: arguments must be integers: x position, y position')
# heading = str(sys.argv[3].lower())
# if heading != 'n' and heading != 's' and heading != 'e' and heading != 'w':
#     sys.exit('Error: heading must be N, E, S, or W')
# if pos[0] > 3 or pos[0] < 0 or pos[1] > 3 or pos[1] < 0:
#     sys.exit('Error: positions must be 0, 1, 2, or 3')

#Todo:
#Make robot stop going forward and return to cell if detects wall in front of it and less than ~2 inches moved
#Make robot navigate randomly; will need to pass in data telling maze not to print map

options = {'color': 'unknown', 'readyToMap': False, 'pos': (-1, -1), 'heading': 'unknown', 'mapped': False}

while options['pos'] == (-1, -1) or options['heading'] == 'unknown': #make sure has position
    options = mainMenu(options)

mz = maze.Maze(options['pos'], options['heading'])
mz.enableColor(colorList)

while True: #now can choose any option
    if options['readyToMap'] == True:
        if mz.nav.mapComplete == True: #clear map
            mz.enableColor(colorList) #clears found color list
            mz.nav.clearMap()
        mz.analyzeCell(True)
        while mz.goToNextCell():
            pass
        print('DONE!')
        options['readyToMap'] = False
        options['mapped'] = True

    if options['color'] != 'unknown':
        try:
            mz.goToCell(mz.nav.findColor(options['color']))
        except:
            print('Error: color not found!')
        options['color'] = 'unknown'

    tempPosition = mz.getPosition() #updates position for next run in case no new pos is input. Will be overwritten by main menu if new position is input
    options['heading'] = tempPosition['heading']
    options['pos'] = tempPosition['pos']
    options = mainMenu(options)
    # print(options)
    mz.nav.setPosition(options['pos'], options['heading'])
    # print('SETTING POSITION TO ' + str(options['pos']) + ' ' + options['heading'])