#!/usr/bin/python
# 

# command to run:  python3 /home/pi/quadrabot/switch_test.py

import RPi.GPIO as GPIO # Import the GPIO Library
import time # Import the Time library

# Set the GPIO modes
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set variables slide switches connected to the GPIO pins
onoff = 9
auto = 10
web = 11

# Set the on/off slide switch as an input
GPIO.setup(onoff, GPIO.IN)

# Set auto slide switch as an input
GPIO.setup(auto, GPIO.IN)

# Set web slide switch as an input
GPIO.setup(web, GPIO.IN)



# set some parameters so that the program only prints out something if it has changed from last time
state_onoff = 2
state_auto = 2
state_web = 2

try:
    #repeat the next indented block forever
    while True:
        # if the on/off switch is low (=0), it's off
        if GPIO.input(onoff)==0 and state_onoff!=0:
            print('The on/off switch is OFF')
            state_onoff = 0

        # If not (else), print the following
        elif GPIO.input(onoff)==1 and state_onoff!=1:
            print('The on/off switch is ON')
            state_onoff = 1

        # if the auto switch is low (=0), it's in demo mode
        if GPIO.input(auto)==0 and state_auto!=0:
            print('demo mode')
            state_auto = 0

        # If not (else), print the following
        elif GPIO.input(auto)==1 and state_auto!=1:
            print('auto mode')
            state_auto = 1

        # if the web switch is low (=0), it's in web control off mode
        if GPIO.input(web)==0 and state_web!=0:
            print('Web control OFF')
            state_web = 0

        # If not (else), print the following
        elif GPIO.input(web)==1 and state_web!=1:
            print('Web control ON')
            state_web = 1


        # Wait, then do the same again
        time.sleep(0.2)

# If you press CTRL+C, cleanup and stop
except KeyboardInterrupt:
    GPIO.cleanup()
    print('  ')
    print('program end - GPIO pins cleaned up')
    print('  ')
