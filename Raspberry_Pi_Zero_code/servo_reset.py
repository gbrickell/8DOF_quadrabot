#!/usr/bin/python
# 
# routine to simply put all the quadrabot's servos into their stand up reset positions
#  - this then allows the servo horns to be taken off of the servo splined drive shafts 
#    and the leg assemblies put into their correct orientations for the quadrabot to 
#    be in the 'stand up' position. 
#  - the servo horns can then be pressed back onto the splined shafts and the small 
#    self tap screws used to secure the horns in their correct positions

# command to run:  python3 /home/pi/quadrabot/servo_reset.py

#*********************************************************************************
#**********************  robot movement functions  *******************************
#*********************************************************************************

##################################################################################
###   function to reset the legs to the 75% DOWN and midway position          ####
##################################################################################
def reset_legs(fd):
    #  reset all the leg servos to the 75% DOWN and midway position
    stand_all_75down(fd)
    set_midway(fd)
    time.sleep(0.2)

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

##################################################################################
###                    main code                                              ####
##################################################################################

import time   # this imports the module to allow various time functions to be used

####################################
# servo set up
####################################
# allow C libraries to be used - but just for servo control
from ctypes import *
# for servo function the custom C library is used
quadrabot_servo = CDLL("/home/pi/quadrabot/libquadrabot_servo.so") 
#call C function to check connection to servo C library
quadrabot_servo.connect_servo() 

# variables (servo descriptions) for the PCA9685 channels
FRONT_RIGHT_LEG = 10
FRONT_RIGHT_HIP = 8
BACK_RIGHT_LEG = 6
BACK_RIGHT_HIP = 4
FRONT_LEFT_LEG = 11
FRONT_LEFT_HIP = 9
BACK_LEFT_LEG = 7
BACK_LEFT_HIP = 5

# array for servo/channel numbers in the order FRL, FRH, BRL, BRH, FLL, FLH, BLL, BLH
SERVO_numbers =[ 10, 8, 6, 4, 11, 9, 7, 5 ]

# initialise the PCA9685 and get the I2C 'file descriptor' to be passed to further functions
print (" setting up PWM module")
print ("  ")
filedesc = quadrabot_servo.PWMsetup(0x40, 50)  # assumes the i2caddress is the default for the PCA9685
print ("I2C file descriptor is: " + str(filedesc))
print ("  ")
# ********************************************************
# set the servo pulse lengths for various movement amounts
# ********************************************************

# individual servo calibrations for 'set' movement amounts
# min: 1ms pulse length ie should be 205 steps out of 4096 but fine tuned for the specific servo
# mid: 1.5ms pulse length ie should be 308 steps out of 4096 but fine tuned for the specific servo
# max: 2ms pulse length ie should be 410 steps out of 4096 but fine tuned for the specific servo

#[ 520, 405, 300, 210, 110 ],    # FRL 10
FRONT_RIGHT_LEG_up100   = 110
FRONT_RIGHT_LEG_up75    = 210
FRONT_RIGHT_LEG_down50  = 300
FRONT_RIGHT_LEG_down75  = 405
FRONT_RIGHT_LEG_down100 = 520

#[ 150, 239, 310, 450, 480 ],    # FRH 8
FRONT_RIGHT_HIP_back100 = 150
FRONT_RIGHT_HIP_back75  = 239
FRONT_RIGHT_HIP_fwd50   = 310
FRONT_RIGHT_HIP_fwd75   = 450
FRONT_RIGHT_HIP_fwd100  = 480

#[ 160, 240, 330, 440, 540 ],    # BRL 6
BACK_RIGHT_LEG_up100   = 540
BACK_RIGHT_LEG_up75    = 440
BACK_RIGHT_LEG_down50  = 330
BACK_RIGHT_LEG_down75  = 240
BACK_RIGHT_LEG_down100 = 160

#[ 205, 250, 350, 450, 520 ],    # BRH 4
BACK_RIGHT_HIP_back100 = 205
BACK_RIGHT_HIP_back75  = 250
BACK_RIGHT_HIP_back50  = 350
BACK_RIGHT_HIP_fwd75   = 450
BACK_RIGHT_HIP_fwd100  = 520

#[ 170, 240, 350, 440, 540 ],    # FLL 11
FRONT_LEFT_LEG_up100   = 540
FRONT_LEFT_LEG_up75    = 440
FRONT_LEFT_LEG_down50  = 350
FRONT_LEFT_LEG_down75  = 240
FRONT_LEFT_LEG_down100 = 170

#[ 560, 450, 350, 240, 195 ],    # FLH 9
FRONT_LEFT_HIP_back100 = 560
FRONT_LEFT_HIP_back75  = 450
FRONT_LEFT_HIP_fwd50   = 350
FRONT_LEFT_HIP_fwd75   = 240
FRONT_LEFT_HIP_fwd100  = 195

#[ 490, 415, 320, 200, 110 ],    # BLL 7
BACK_LEFT_LEG_up100   = 110
BACK_LEFT_LEG_up75    = 200
BACK_LEFT_LEG_down50  = 320
BACK_LEFT_LEG_down75  = 415
BACK_LEFT_LEG_down100 = 490

#[ 520, 460, 350, 270, 205 ] ]   # BLH 5
BACK_LEFT_HIP_back100 = 520
BACK_LEFT_HIP_back75  = 460
BACK_LEFT_HIP_back50  = 350
BACK_LEFT_HIP_fwd75   = 270
BACK_LEFT_HIP_fwd100  = 205

# calibration array where columns are the positions 0%, 25%, 50%,75% and 100% (hips forward and legs up)
# and where the rows are the servos in the order FRL, FRH, BRL, BRH, FLL, FLH, BLL, BLH
S_cal = [
[ 520, 405, 300, 210, 110 ],    # FRL 10
[ 150, 239, 310, 450, 480 ],    # FRH 8
[ 160, 240, 330, 440, 540 ],    # BRL 6
[ 205, 250, 350, 450, 520 ],    # BRH 4
[ 170, 240, 350, 440, 540 ],    # FLL 11
[ 560, 450, 350, 240, 195 ],    # FLH 9
[ 490, 415, 320, 200, 110 ],    # BLL 7
[ 520, 460, 350, 270, 205 ] ]   # BLH 5


# set the stand-up mode to show that the robot has fully started up and is ready

time.sleep(0.5)
reset_legs(filedesc)

print (" ")
print ("****************************************************")
print ("*******      robot in stand up position      *******") 
print ("*** now remove a battery to 'release' the servos ***")
print ("* and reset the legs and servo horns appropriately *")
print ("*****************************************************")
print (" ")
print (" ")

