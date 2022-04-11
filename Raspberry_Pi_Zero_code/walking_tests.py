#!/usr/bin/python
# 
# test routine to show the quadrabot's individual leg movements in 'slow motion'
#  for the various movement ioptions i.e. fwd, back etc

# command to run:  python3 /home/pi/quadrabot/walking_tests.py

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
###        function to make a left or right turn using the C library          ####
##################################################################################
def slow_make_turn(delay1, delay2, fd, dir, cycles, dirFRL, dirFRH, dirBRL, dirBRH, dirFLL, dirFLH, dirBLL, dirBLH):
    # delay1 in seconds between each servo/leg movement
    # delay2 in seconds between each time slice
    # not using the dir(ection) parameter - but left in just in case
    #loop through the time slices for n cycles
    for n in range(0,int(cycles)):
        # loop through each servo for 16 time slices
        for i in range(0,16):
            print ("*** time slice: " + str(i) + " ***")
            print ("front right leg " + str(i))
            quadrabot_servo.setServo(fd, FRONT_RIGHT_LEG, dirFRL[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("front right hip " + str(i))
            quadrabot_servo.setServo(fd, FRONT_RIGHT_HIP, dirFRH[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("back right leg " + str(i))
            quadrabot_servo.setServo(fd, BACK_RIGHT_LEG, dirBRL[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("back right hip " + str(i))
            quadrabot_servo.setServo(fd, BACK_RIGHT_HIP, dirBRH[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("front left leg " + str(i))
            quadrabot_servo.setServo(fd, FRONT_LEFT_LEG, dirFLL[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("front left hip " + str(i))
            quadrabot_servo.setServo(fd, FRONT_LEFT_HIP, dirFLH[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("back left leg " + str(i))
            quadrabot_servo.setServo(fd, BACK_LEFT_LEG, dirBLL[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("back left hip " + str(i))
            quadrabot_servo.setServo(fd, BACK_LEFT_HIP, dirBLH[i], 0)
            time.sleep(delay2) # wait between time slices
    #  reset all the leg servos to the 75% DOWN and midway position
    reset_legs(fd)

    return()
##################

##################################################################################
###        function to walk forwards or backwards using the C library         ####
##################################################################################
def slow_walking(delay1, delay2, fd, dir, cycles, dirFRL, dirFRH, dirBRL, dirBRH, dirFLL, dirFLH, dirBLL, dirBLH):
    # delay1 in seconds between each servo/leg movement
    # delay2 in seconds between each time slice
    # not using the dir(ection) parameter - but left in just in case
    #loop through the time slices for n cycles
    for n in range(0,int(cycles)):
        # loop through each servo for 16 time slices
        for i in range(0,16):
            print ("*** time slice: " + str(i) + " ***")
            print ("front right leg " + str(i) + " " + str(dirFRL[i]))
            quadrabot_servo.setServo(fd, FRONT_RIGHT_LEG, dirFRL[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("front right hip " + str(i) + " " + str(dirFRH[i]))
            quadrabot_servo.setServo(fd, FRONT_RIGHT_HIP, dirFRH[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("back right leg " + str(i) + " " + str(dirBRL[i]))
            quadrabot_servo.setServo(fd, BACK_RIGHT_LEG, dirBRL[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("back right hip " + str(i) + " " + str(dirBRH[i]))
            quadrabot_servo.setServo(fd, BACK_RIGHT_HIP, dirBRH[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("front left leg " + str(i) + " " + str(dirFLL[i]))
            quadrabot_servo.setServo(fd, FRONT_LEFT_LEG, dirFLL[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("front left hip " + str(i) + " " + str(dirFLH[i]))
            quadrabot_servo.setServo(fd, FRONT_LEFT_HIP, dirFLH[i], 0)
            time.sleep(delay1) # wait between servo movements
            print ("back left leg " + str(i) + " " + str(dirBLL[i]))
            quadrabot_servo.setServo(fd, BACK_LEFT_LEG, int(dirBLL[i]), 50)
            time.sleep(delay1) # wait between servo movements
            print ("back left hip " + str(i) + " " + str(dirBLH[i]))
            quadrabot_servo.setServo(fd, BACK_LEFT_HIP, dirBLH[i], 50)
            time.sleep(delay2) # wait between time slices
    #  reset all the leg servos to the 75% DOWN and midway position
    reset_legs(fd)

    return()
##################

##################################################################################
###           function to make a leg 'wave' using the C library               ####
##################################################################################
def wave_leg(fd, hip_servo, hip_min, hip_max, leg_servo, leg_up, leg_down, waves):
    print ("waving hip-leg servos: " + str(hip_servo) + " - " + str(leg_servo) )

    # raise the leg_servo to the leg_up position 
    #   and move the hip back and forth 'waves' times
    quadrabot_servo.setServo(fd, leg_servo, leg_up, 0)
    for i in range(0,waves):
        quadrabot_servo.setServo(fd, hip_servo, hip_min, 0 )
        time.sleep(0.5)
        quadrabot_servo.setServo(fd, hip_servo, hip_max, 0 )
        time.sleep(0.5)
    quadrabot_servo.setServo(fd, leg_servo, leg_down, 0)
    time.sleep(0.5)  # small delay whilst the waving foot is being set down
    return()
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

##################################################################################
###   function to set all hips and legs to produce the 'squat' position       ####
##################################################################################
def set_squat(fd):
    #  set all the hip servos to mid position
    quadrabot_servo.setServo(fd, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd50, 0)
    quadrabot_servo.setServo(fd, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd50, 0)
    quadrabot_servo.setServo(fd, BACK_RIGHT_HIP, BACK_RIGHT_HIP_back50, 0)
    quadrabot_servo.setServo(fd, BACK_LEFT_HIP, BACK_LEFT_HIP_back50, 0)
    #  set all the leg servos to the fully down position
    quadrabot_servo.setServo(fd, FRONT_RIGHT_LEG, FRONT_RIGHT_LEG_down100, 0)
    quadrabot_servo.setServo(fd, FRONT_LEFT_LEG, FRONT_LEFT_LEG_down100, 0)
    quadrabot_servo.setServo(fd, BACK_RIGHT_LEG, BACK_RIGHT_LEG_down100, 0)
    quadrabot_servo.setServo(fd, BACK_LEFT_LEG, BACK_LEFT_LEG_down100, 0)
    return()
##################

##################################################################################
###   function to set all hips and legs to produce the 'bowing' position       ####
##################################################################################
def set_bow(fd):
    #  set all the hip servos to the 75% fwd and back positions
    quadrabot_servo.setServo(fd, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd75, 0)
    quadrabot_servo.setServo(fd, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd75, 0)
    quadrabot_servo.setServo(fd, BACK_RIGHT_HIP, BACK_RIGHT_HIP_back75, 0)
    quadrabot_servo.setServo(fd, BACK_LEFT_HIP, BACK_LEFT_HIP_back75, 0)
    #  set all the rear legs to 75% down and the front to 100% up
    quadrabot_servo.setServo(fd, FRONT_RIGHT_LEG, FRONT_RIGHT_LEG_up100, 0)
    quadrabot_servo.setServo(fd, FRONT_LEFT_LEG, FRONT_LEFT_LEG_up100, 0)
    quadrabot_servo.setServo(fd, BACK_RIGHT_LEG, BACK_RIGHT_LEG_down75, 0)
    quadrabot_servo.setServo(fd, BACK_LEFT_LEG, BACK_LEFT_LEG_down75, 0)
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


##################################################
## set the forward walking array servo settings ##
##        0-15 time slices                      ##
##        8 servos : 10,8,6,4,11,9,7,5          ##
##################################################

fwdFRL = [ 405, 405, 405, 405, 405, 300, 300, 405, 405, 405, 405, 405, 405, 405, 405, 405 ] # 100%: 110 - 50%: 300
fwdFRH = [ 240, 210, 180, 150, 150, 300, 450, 450, 450, 450, 420, 390, 360, 330, 300, 270 ]

fwdBRL = [ 240, 330, 330, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240 ] # 100%: 540 - 50%: 350
fwdBRH = [ 250, 385, 520, 520, 520, 520, 493, 466, 439, 412, 385, 358, 331, 304, 277, 250 ]

fwdFLL = [ 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 350, 350, 240 ] # 100%: 540 - 50%: 350
fwdFLH = [ 230, 230, 263, 296, 329, 362, 395, 428, 461, 494, 527, 560, 560, 395, 230, 230 ]

fwdBLL = [ 415, 415, 415, 415, 415, 415, 415, 415, 415, 320, 320, 415, 415, 415, 415, 415 ] # 100%: 110 - 50%: 300
fwdBLH = [ 283, 309, 335, 361, 387, 413, 439, 460, 460, 332, 205, 205, 205, 205, 231, 257 ]


###################################################
## set the backward walking array servo settings ##
##        0-15 time slices                       ##
##        8 servos : 10,8,6,4,11,9,7,5           ##
###################################################

backFRL = [ 405, 405, 405, 405, 405, 300, 300, 405, 405, 405, 405, 405, 405, 405, 405, 405 ] # 100%: 110 - 50%: 300
backFRH = [ 360, 390, 420, 450, 450, 310, 150, 150, 150, 150, 180, 210, 240, 270, 300, 330 ]
															
backBRL = [ 240, 350, 350, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240 ] # 100%: 540 - 50%: 350
backBRH = [ 520, 450, 250, 250, 250, 250, 277, 304, 331, 358, 385, 412, 439, 466, 493, 520 ]

backFLL = [ 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 350, 350, 240 ] # 100%: 540 - 50%: 350														
backFLH = [ 560, 560, 527, 494, 461, 428, 395, 362, 329, 296, 263, 230, 230, 350, 560, 560 ]
															
backBLL = [ 415, 415, 415, 415, 415, 415, 415, 415, 415, 300, 300, 415, 415, 415, 415, 415 ] # 100%: 110 - 50%: 300
backBLH = [ 385, 360, 335, 310, 285, 260, 235, 205, 205, 270, 460, 460, 460, 460, 435, 410 ]


##################################################
## set the turn right array servo settings      ##
##        0-15 time slices                      ##
##        8 servos : 10,8,6,4,11,9,7,5          ##
##################################################

rightFRL = [ 405, 405, 405, 405, 405, 300, 300, 405, 405, 405, 405, 405, 405, 405, 405, 405 ] # 100%: 110 - 50%: 300
rightFRH = [ 388, 422, 456, 490, 490, 310, 150, 150, 150, 150, 184, 218, 252, 286, 320, 354 ]
															
rightBRL = [ 240, 330, 330, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240 ] # 100%: 540 - 50%: 330
rightBRH = [ 520, 350, 205, 205, 205, 205, 237, 269, 301, 333, 365, 397, 429, 461, 493, 520 ]
															
rightFLL = [ 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 350, 350, 240 ] # 100%: 540 - 50%: 350
rightFLH = [ 180, 180, 218, 256, 294, 332, 370, 408, 446, 484, 522, 560, 560, 350, 180, 180 ]
															
rightBLL = [ 415, 415, 415, 415, 415, 415, 415, 415, 415, 300, 300, 415, 415, 415, 415, 415 ] # 100%: 110 - 50%: 300
rightBLH = [ 301, 333, 365, 397, 429, 461, 493, 520, 520, 350, 205, 205, 205, 205, 237, 269 ]


##################################################
## set the turn left array servo settings       ##
##        0-15 time slices                      ##
##        8 servos : 10,8,6,4,11,9,7,5          ##
##################################################

leftFRL = [ 405, 405, 405, 405, 405, 300, 300, 405, 405, 405, 405, 405, 405, 405, 405, 405 ] # 100%: 110 - 50%: 300
leftFRH = [ 252, 218, 184, 150, 150, 310, 490, 490, 490, 490, 456, 422, 388, 354, 320, 286 ]
															
leftBRL = [ 240, 330, 330, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240 ] # 100%: 540 - 50%: 330
leftBRH = [ 205, 350, 520, 520, 520, 520, 489, 458, 427, 396, 365, 334, 303, 272, 241, 205 ]
															
leftFLL = [ 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 350, 350, 240 ] # 100%: 540 - 50%: 350
leftFLH = [ 560, 560, 522, 484, 446, 408, 370, 332, 294, 256, 218, 180, 180, 350, 560, 560 ]
															
leftBLL = [ 415, 415, 415, 415, 415, 415, 415, 415, 415, 300, 300, 415, 415, 415, 415, 415 ] # 100%: 110 - 50%: 300
leftBLH = [ 427, 396, 365, 334, 303, 272, 241, 205, 205, 350, 520, 520, 520, 520, 489, 458 ]

# set the squat and then the stand-up mode to show that the robot has fully started up and is ready
set_squat(filedesc)
time.sleep(0.5)
reset_legs(filedesc)

sdelay = 0.3    # delay in seconds between servo movements
tdelay = 0.5    # delay in seconds between time slices

########################################################
# code to control the walking robot goes below this line
########################################################

try:        # using try ahead of the 'while' loop allows CTRL-C to be used to cleanly end the cycle

    # 
    ######################
    #  start of main loop
    ######################
    repeat = "first_time"  # first time thru
    wtype = "" 
    while True:
        time.sleep(0.5)  # pause for 0.5 seconds to provide a processing gap for other activity
        # input the walking type to be tested
        while wtype != "l" and wtype != "r" and wtype != "f" and wtype != "b":
            wtype = input(" Enter a walking test type i.e. l, r, f or b: ")

        if repeat == 'yes' or repeat == "first_time":
            if repeat == "yes":
                print ("repeating slow walk type: " + wtype)
            if wtype == "l":
                print ("slow turning left")
                slow_make_turn(sdelay, tdelay, filedesc, "left",   1, leftFRL,  leftFRH,  leftBRL,  leftBRH,  leftFLL,  leftFLH,  leftBLL, leftBLH)
            elif wtype == "r":
                print ("slow turning right")
                slow_make_turn(sdelay, tdelay, filedesc, "right",  1, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)
            elif wtype == "f":
                print ("slow walking forwards")
                slow_walking(sdelay, tdelay, filedesc, "forward",  1, fwdFRL,   fwdFRH,   fwdBRL,   fwdBRH,   fwdFLL,   fwdFLH,   fwdBLL, fwdBLH)
            elif wtype == "b":
                print ("slow walking backwards")
                slow_walking(sdelay, tdelay, filedesc, "backward", 1, backFRL,  backFRH,  backBRL,  backBRH,  backFLL,  backFLH,  backBLL, backBLH)

        # reset repeat
        repeat = ""

        # now check if the same wtype is to be repeated
        while repeat != "no" and repeat != "yes":
            repeat = input(" repeat the same walking test type yes or no: ")
        if repeat == "yes":
            pass
        elif repeat == "no":
            repeat = "first_time"   # reset the repeat parameter
            wtype = ""              # reset wtype so that it has to be input again

        # now go round the while loop again



finally:  
    print ("Cleaning up at the end of the program")

    #  reset all the leg servos to the 75% DOWN and midway position
    stand_all_75down(filedesc)
    set_midway(filedesc)
    time.sleep(0.5)

    print("  ")
    print("*******************************************************")
    print("robot put into stand-up stance")
    print("program end")
    print("*******************************************************")
    print("  ")

