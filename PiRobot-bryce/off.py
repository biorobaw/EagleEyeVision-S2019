# This program demonstrates usage of the digital encoders.
# After executing the program, manually spin the wheels and observe the output.
# See https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/ for more details.
import encoders
import servos
import sensors
import time
import RPi.GPIO as GPIO
import signal
# import pandas as pd

#objects for servos, encoders, sensors, and camera
enc = encoders.Encoders()
serv = servos.Servos()
sens = sensors.Sensors()

def ctrlC():
    print("Exiting")
    serv.stopServos()
    sens.stopRanging()
    GPIO.cleanup()
    exit()

# Attach the Ctrl+C signal interrupt
signal.signal(signal.SIGINT, ctrlC)

ctrlC()
  
