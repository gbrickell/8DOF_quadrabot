#!/usr/bin/python

# quadrabot I2C_servo_test.py - servo control test routine using a PCA9685 I2C controller
# moves a SG90 servo on channel N from min to max position after an input
#
# command:  python3 /home/pi/quadrabot/I2C_servo_test.py

# CLI command to check I2C address:  i2cdetect -y -r 1
#

########################################################
####            various python functions            ####
########################################################

##################################################################################
###   function to reset the legs to the 75% DOWN and midway position          ####
##################################################################################
def reset_legs(fd):
    #  reset all the leg servos to the 75% DOWN and midway position
    stand_all_75down(fd)
    set_midway(fd)
    time.sleep(0.2)
##################

##################################################################################
###      function to set all legs to 75% down using the C library             ####
##################################################################################
def stand_all_75down(fd):
    #  set all the leg servos to the 75% DOWN position
    quadrabot_servo.setServo(fd, FRONT_RIGHT_LEG, FRONT_RIGHT_LEG_down75, 0)
    quadrabot_servo.setServo(fd, FRONT_LEFT_LEG, FRONT_LEFT_LEG_down75, 0)
    quadrabot_servo.setServo(fd, BACK_RIGHT_LEG, BACK_RIGHT_LEG_down75, 0)
    quadrabot_servo.setServo(fd, BACK_LEFT_LEG, BACK_LEFT_LEG_down75, 0)
    return()
##################

##################################################################################
###   function to set all hips to mid way position using the C library        ####
##################################################################################
def set_midway(fd):
    #  set all the hip servos to mid position
    quadrabot_servo.setServo(fd, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd50, 0)
    quadrabot_servo.setServo(fd, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd50, 0)
    quadrabot_servo.setServo(fd, BACK_RIGHT_HIP, BACK_RIGHT_HIP_back50, 0)
    quadrabot_servo.setServo(fd, BACK_LEFT_HIP, BACK_LEFT_HIP_back50, 0)
    return()
##################

########################################################
####                   main code                    ####
########################################################
import time               # this imports the module to allow various time functions to be used
import RPi.GPIO as GPIO   # this imports the module to allow the GPIO pins to be easily utilised
from ctypes import *

# --------------------------------------------------------------------------------
# set up the use of a set of compiled C functions that do various servo functions
# compiled C is used because it is faster than interpreted python coding and some 
# of these functions need to run as fast as possible
quadrabot_servo = CDLL("/home/pi/quadrabot/libquadrabot_servo.so")
#call the servo connect C function to check connection to the compiled 'C' library
quadrabot_servo.connect_servo() 

# Initialise the PCA9685 servo PWM control board assuming it has its 
#  default address i.e. hex 40 (0x40) and is the only PCA9685 device on the I2C bus
#  this can be checked by running "i2cdetect -y 1"
#  for all recent RPi models the port# is 1 in the above 'detect' command - but for pre-Oct'12 models it is 0
address = "0x40" 
frequency = 50  # recommended PWM frequency for servo use
print (" setting up PWM module")
print ("  ")
filedesc = quadrabot_servo.PWMsetup(0x40, 50)  # sets up the board and retrieves the I2C file descriptor for later use
print ("I2C file descriptor is: " + str(filedesc))
print ("  ")
print("PCA9685 initialised")

servo_chan = 99  # set an initial non-valid servo channel#
# set the min and max servo pulse lengths
# min: 1ms pulse length ie should be 205 steps out of 4096 but should be fine tuned for the specific servo
servo_min = 160 

# max: 1.5ms pulse length ie should be 308 steps out of 4096 but should be fine tuned for the specific servo
servo_mid = 350 

# mid: 2ms pulse length ie should be 410 steps out of 4096 but should be fine tuned for the specific servo
servo_max = 560 

# below are the channel# to quadrabot leg associations
FRONT_RIGHT_LEG = 10
FRONT_RIGHT_HIP = 8
BACK_RIGHT_LEG = 6
BACK_RIGHT_HIP = 4
FRONT_LEFT_LEG = 11
FRONT_LEFT_HIP = 9
BACK_LEFT_LEG = 7
BACK_LEFT_HIP = 5

# individual servo calibrations for 'set' movement amounts
# min: 1ms pulse length ie should be 205 steps out of 4096 but fine tuned for the specific servo
# mid: 1.5ms pulse length ie should be 308 steps out of 4096 but fine tuned for the specific servo
# max: 2ms pulse length ie should be 410 steps out of 4096 but fine tuned for the specific servo

##just setting these so that the stand-up function works OK
FRONT_RIGHT_LEG_down75  = 405
FRONT_RIGHT_HIP_fwd50   = 310

BACK_RIGHT_LEG_down75  = 240
BACK_RIGHT_HIP_back50  = 350

FRONT_LEFT_LEG_down75  = 240
FRONT_LEFT_HIP_fwd50   = 350

BACK_LEFT_LEG_down75  = 415
BACK_LEFT_HIP_back50  = 350

# calibration array where columns are the positions 0%, 25%, 50%,75% and 100% (hips forward and legs up)
# and where the rows are the servos in the order FRL (10), FRH (8), BRL (6), BRH(4), FLL(11), FLH (9), BLL (7), BLH (5)
####
# fine tune the numbers in this array and then copy the finalised 
# calibrations to the main quadrabot Python code at about line 977
####
S_cal = [
[ 510, 370, 280, 200, 110 ],    # FRL 10
[ 150, 239, 310, 450, 480 ],    # FRH 8
[ 160, 240, 330, 440, 540 ],    # BRL 6
[ 205, 250, 350, 450, 520 ],    # BRH 4
[ 170, 240, 350, 440, 540 ],    # FLL 11
[ 560, 450, 350, 240, 195 ],    # FLH 9
[ 490, 415, 320, 200, 110 ],    # BLL 7
[ 520, 460, 350, 270, 205 ] ]   # BLH 5

reset_legs(filedesc)

print (" ***************************************************************************")
print (" An individual servo channel number needs to be entered ")
print (" An 8DOF quadrabot usually uses channels 4-11")
print (" ***************************************************************************")
print (" ")

print("Program running: once a channel# is entered that servo will move from min to max once - CTRL C to stop")
try:    # this loop is not strictly necessary but it does allow the script to be easily stopped with CTRL-C
    while True:  # this is the loop that checks if a button is pressed and moves each servo arm if it is

        while int(servo_chan) < 4 or int(servo_chan) > 11:
            servo_chan = input(" Enter a servo channel value from 4 to 11: ")
        # valid channel entered so move servo on servo_chan between extremes.
        # first decide which calbration row to use for the choseb channel#
        if int(servo_chan) == 4:
            calrow = 3
        elif int(servo_chan) == 5:
            calrow = 7
        elif int(servo_chan) == 6:
            calrow = 2
        elif int(servo_chan) == 7:
            calrow = 6
        elif int(servo_chan) == 8:
            calrow = 1
        elif int(servo_chan) == 9:
            calrow = 5
        elif int(servo_chan) == 10:
            calrow = 0
        elif int(servo_chan) == 11:
            calrow = 4

        print("  .... moving servo on channel " + str(servo_chan) )
        quadrabot_servo.setServo(filedesc, int(servo_chan), S_cal[calrow][0], 50)
        time.sleep(2)
        quadrabot_servo.setServo(filedesc, int(servo_chan), S_cal[calrow][1], 50)
        time.sleep(2)
        quadrabot_servo.setServo(filedesc, int(servo_chan), S_cal[calrow][2], 50)
        time.sleep(2)
        quadrabot_servo.setServo(filedesc, int(servo_chan), S_cal[calrow][3], 50)
        time.sleep(2)
        quadrabot_servo.setServo(filedesc, int(servo_chan), S_cal[calrow][4], 50)
        time.sleep(2)
        quadrabot_servo.setServo(filedesc, int(servo_chan), S_cal[calrow][2], 50)
        time.sleep(2)
        servo_chan = 99  # reset to a non-valid number so a new channel# can be entered
        reset_legs(filedesc)
        print("looping to get another channel or CTRL C to stop")

finally:  # this code is run when the try is interrupted with a CTRL-C
    print(" ")
    print("Cleaning up the GPIO pins before stopping")
    print(" ")
    print(" ")
    print(" ")
    GPIO.cleanup()
    print("*******************************************************")
    print("program end")
    print("*******************************************************")
    print("  ")


    
# The cleanup command sets all the pins back to inputs which protects the
# Pi from accidental shorts-circuits if something metal touches the GPIO pins.

