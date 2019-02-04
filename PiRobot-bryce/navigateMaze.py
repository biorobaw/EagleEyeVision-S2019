import time
import RPi.GPIO as GPIO
import signal
import maze
import servos
import sys

#objects for servos, encoders, sensors, and camera
serv = servos.Servos()


def ctrlC(signum, frame):
    print("Exiting")
    serv.stopServos()
    # sens.stopRanging()
    GPIO.cleanup()
    exit()
signal.signal(signal.SIGINT, ctrlC)

if len(sys.argv) != 4:
    sys.exit('Error: navigateMaze.py requires 3 arguments: x position, y position, and heading')
try:
    pos = [int(sys.argv[1]), int(sys.argv[2])]
except ValueError:
    sys.exit('Error: arguments must be integers: x position, y position')
heading = str(sys.argv[3].lower())
if heading != 'n' and heading != 's' and heading != 'e' and heading != 'w':
    sys.exit('Error: heading must be N, E, S, or W')
if pos[0] > 3 or pos[0] < 0 or pos[1] > 3 or pos[1] < 0:
    sys.exit('Error: positions must be 0, 1, 2, or 3')
mz = maze.Maze(pos, heading)

# mz.goForward()
# mz.goForward()
# mz.turn('right')
# mz.goForward()
# mz.turn('right')
# mz.goForward()
# mz.turn('left')
# mz.goForward()
# mz.goForward()
# mz.turn('right')
# mz.goForward()
# mz.turn('right')
# mz.goForward()
# mz.goForward()
# mz.goForward()
# mz.turn('right')
mz.analyzeCell(True)
while mz.goToNextCell():
    pass
print('DONE!')