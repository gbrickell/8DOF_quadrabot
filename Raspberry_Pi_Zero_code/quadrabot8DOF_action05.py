#!/usr/bin/python

# quadrabot8DOF_action05.py - quadrabot 8DOF walking robot motion control program using a PCA9685 I2C controller
# moves servos on a specified leg for 'creeping' gait walking
#  channels chosen to make the physical connections to the PCA9685 on the quadrabot build a bit easier
#
# slide switch logic also allows use of wireless controller which uses the "inputs" library
# if in web mode it expects to 'see' the commands coming from the separate web app
# from an interprocess communication file held in ram disc

# command:  python3 /home/pi/quadrabot/quadrabot8DOF_action05.py
# Enmore 220406

## cron ##
# start main python control code for the 8DOF quadrabot
#@reboot python3 /home/pi/quadrabot/quadrabot8DOF_action05.py
# start web interface code for the 8DOF quadrabot
#@reboot sudo python3 /home/pi/quadrabot/quadrabot8DOF_web02.py

###########################################################################################
# Dictionary of the 19 game controller buttons/joysticks on the PiHut wireless controller
# which is recognised by the 'inputs' module as a "MS X-Box 360 pad"
###########################################################################################
controller_input = {'BTN_THUMBL': 0, 'ABS_X': 0, 'ABS_Y': 0, 'BTN_THUMBR': 0,  'ABS_RX': 0, 'ABS_RY': 0, 
                    'BTN_START': 0, 'BTN_SELECT': 0, 'BTN_MODE': 0,  'ABS_HAT0X': 0, 'ABS_HAT0Y': 0, 
                    'BTN_WEST': 0, 'BTN_NORTH': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0,
                    'BTN_TL': 0, 'BTN_TR': 0, 'ABS_Z': 0, 'ABS_RZ': 0 }


## **************************************************************************************
## python routine to check slide switch state and change the opmode setting accordingly
##       opmode options:  simple integers as set out below
## switch state local variables:  state_onoff   state_auto_demo  state_web are all either 0 or 1
## debug set to 1 gives additional outputs - but the routine is otherwise 'silent'
## assumes Broadcom GPIO numbering, the switches are already set as INPUTs and the switch GPIO#'s are 'global'
## **************************************************************************************
def check_slide_switches(opmode_last, debug):
    ## check for each slide switch setting
    ## opmode_last is a simple passed parameter of the current/last opmode setting
    ## opmode = 0 means 'idle'
    ## opmode = 1 means 'demo'
    ## opmode = 2 means 'avoid'
    ## opmode = 3 means 'web'
    ## opmode = 4 means 'stop_web'
    ## opmode = 5 means 'wc_mode' ie wireless controller
    ## opmode = 9 means an undefined operational mode

    opmode=10;

    state_onoff=2;
    state_autod=2;
    state_web=2;

    ## *** ON/OFF slide switch ***
    ##     -------------------
    ## if the on/off switch is low (=0), it's OFF
    if GPIO.input(onoff) == 0:
        if (opmode_last!=0 and debug==1):
            print("The on/off switch is now OFF \n")
            print("check slide switch: switches set to IDLE mode \n")
            reset_legs(filedesc)
            clearOLED(width, height, image)
            line1 = "system idle/OFF"
            line2 = "* legs reset *" 
            line3 = " " 
            line4 = " " 
            OLED_4lines(line1, line2, line3, line4, top, font, image)

        opmode=0       ##  if the ON/OFF switch is OFF it is always in 'idle' mode 
        return opmode  ##  so immediately return

    ## if the on/off switch is high (=1), it's ON
    elif GPIO.input(onoff) == 1:
        state_onoff=1

    ## *** auto/demo slide switch ***
    ##     ----------------------
    ## if the auto/demo switch is low (=0), it may be in demo mode if web is also low (=0)
    if GPIO.input(auto_demo) == 0:
        state_autod=0  ## just set the state for now

    ## if the auto/demo switch is high (=1), it may be in avoid mode
    ##   unless web is also high (=1) which will mean wc mode
    elif GPIO.input(auto_demo) == 1:
        state_autod=1  ## just set the state for now

    ## *** web on/off slide switch ***
    ##     -----------------------
    ## if the web switch is low (=0), it is NOT in web control mode
    if GPIO.input(web) == 0:
        state_web=0    ## just set the state for now

    ## if the web switch is high (=1), it may be in web control mode 
    ##   unless auto/demo is also high (=1) which will mean wc mode
    elif GPIO.input(web) == 1:
        state_web=1    ## just set the state for now

    ## now set the appropriate opmode

    ## *** special stop web mode ***
    ##     ---------------------
    ## if we were in web mode (3) and now it is switched off set 'stop_web'
    if opmode_last == 3 and state_web == 0:  ## special stop web mode
        if debug == 1:
            print("The web on/off switch is now off \n")
            print("check slide switch: switches set to 'stop_web' mode \n")

        opmode=4       ##  set to 'stop_web' 
        return opmode  ##   and immediately return

    ## *** demo mode ***
    ##     ---------
    elif (state_onoff == 1 and state_web != 1 and state_autod == 0) :   ## set demo mode
        opmode=1
        ## but first check if this is a change of opmode before printing
        if (opmode_last != 1 and debug==1):
            print("check slide switch: switches set for DEMO mode \n")
        return opmode ##   and immediately return

    ## *** avoid mode ***
    ##     ----------
    elif (state_onoff == 1 and state_web != 1 and state_autod == 1):   ## set avoid mode
        opmode=2;
        ## but first check if this is a change of opmode before printing
        if (opmode_last != 2 and debug==1):
            print("check slide switch: switches set for AVOID mode \n")
        return opmode ##   and immediately return

    ## *** web mode ***
    ##     --------
    elif (state_onoff == 1 and state_web == 1 and state_autod == 0):   ## set web mode
        opmode=3
        ## but first check if this is a change of opmode before printing
        if (opmode_last != 3 and debug==1):
            print("check slide switch: switches set for WEB mode \n")
        return opmode ##   and immediately return

    ## *** wireless controller mode ***
    ##     ------------------------
    elif (state_onoff == 1 and state_web == 1 and state_autod == 1):   ## set wc mode
        opmode=5
        ## but first check if this is a change of opmode before printing
        if (opmode_last != 5 and debug==1):
            print("check slide switch: switches set for WC mode \n")
        return opmode ##   and immediately return

    ## end of slide switch checks - if here then in an undefined opmode state
    opmode=9
    if (opmode != opmode_last and debug==1):   ## only print out if this has just happened
        print("check slide switch: undefined opmode state \n")

    return opmode


##############################################
###   function to clear the OLED screen    ###
##############################################
def clearOLED(w, h, screenimage):

    # Draw a black filled box to clear the image and then display it.
    draw.rectangle((0,0,w,h), outline=0, fill=0)
    disp.image(screenimage)
    disp.display()

    return()

########################################################
###   function to display text on the OLED screen    ###
########################################################
def OLED_4lines(l1, l2, l3, l4, screentop, displayfont, screenimage):
    # l1 to l4 are text strings where the font is assumed to be Lato-Regular.ttf size 16

    # Write four lines of text onto the image: need to adjust the 'spacing' for the font size
    # if font size is 16 the maximum #lines is 4 for the 128 x 64 display
    draw.text((x, top),    l1,  font=font, fill=255)
    draw.text((x, top+16), l2,  font=font, fill=255)
    draw.text((x, top+32), l3,  font=font, fill=255)
    draw.text((x, top+48), l4,  font=font, fill=255)

    # Display the image.
    disp.image(screenimage)  # set the buffer to the values of the Python Imaging Library (PIL) image
                       # the image should be in 1 bit mode and a size equal to the display size.
    disp.display()     # write the display buffer to the physical display

    return()


##################################################
##        joystick axes mixer function          ##
##    for use with the PiHut controller         ##
##    and using the Python 'inputs' module      ##
##     not used with the quadrabot but          ##
##      included here for completeness          ##
##################################################
def mixer(yaw, throttle, max_power=100):   # max_power set to 100 for L298N use
    """
    Mix a pair of joystick axes, returning a pair of wheel power settings. This is where the mapping from
    joystick positions to wheel powers is defined, so any changes to how the robot drives should be made here
    
    :param yaw: 
        Yaw axis values normalised to the range from -1.0 to 1.0 before it gets here
    :param throttle: 
        Throttle axis value normalised to the range from -1.0 to 1.0 before it gets here
    :param max_power: 
        Maximum speed that should be returned from the mixer, defaults to 100
    :return: 
        A pair of power_left, power_right integer duty cycle values to send to the motor driver
    """
    left = throttle + yaw
    right = throttle - yaw
    scale = float(max_power) / max(1, abs(left), abs(right))
    return int(left * scale), int(right * scale)

################################################################
##   wireless controller general button/joystick functions    ##
##  all the buttons and functions set up here - just in case! ##
################################################################

#-----------------------------------------------------------

def gamepad_update():
    # Code execution stops at the following line until gamepad event occurs.
    events = get_gamepad()
    return_code = 'No Match'
    for event in events:
        event_test = controller_input.get(event.code, 'No Match')
        if event_test != 'No Match':
            controller_input[event.code] = event.state
            return_code = event.code
        else:
            return_code = 'No Match'

    return return_code

#-----------------------------------------------------------

def drive_controlxy_left():
    # function to drive robot motors using the left hand joystick
    # x-axis output
    print('x-axis output --> {}' .format(controller_input['ABS_X']) )
    # y-axis output
    print('y-axis output --> {}' .format(controller_input['ABS_Y']) )

#-----------------------------------------------------------
def drive_controlxy_right():
    # function to drive robot motors using the right hand joystick
    # x-axis output
    print('x-axis output --> {}' .format(controller_input['ABS_RX']) )
    # y-axis output
    print('y-axis output --> {}' .format(controller_input['ABS_RY']) )

#-----------------------------------------------------------

def abs_z():  # not used for the 8DOF quadrabot control so nothing 'special' done here
    # Function to do something when the rear/bottom (2) left-hand (ABS_Z) btn is held down for a period of time
    print('ABS_Z button movement --> {}' .format(controller_input['ABS_Z']) )

#-----------------------------------------------------------

def abs_rz():  # not used for the 8DOF quadrabot control so nothing 'special' done here
    # Function to do something when the rear/bottom (2) right-hand (ABS_RZ) btn is held down for a period of time
    print('ABS_RZ button movement --> {}' .format(controller_input['ABS_RZ']) )

#-----------------------------------------------------------

def abs_hat0x():  # used for turning the quadrabot left or right 
    # Function to do something when either of the x-axis pads (ABS_HAT0X) are pressed
    print('ABS_HAT0X pad pressed --> {}' .format(controller_input['ABS_HAT0X']) )
    if controller_input['ABS_HAT0X'] == -1:
        print (" .... turn left")
        return "left"
    elif controller_input['ABS_HAT0X'] == 1:
        print (" .... turn right")
        return "right"

#-----------------------------------------------------------

def abs_hat0y():  # used for 'walking' the quadrabot forwards or backwards
    # Function to do something when either of the y-axis pads (ABS_HAT0Y) are pressed
    print('ABS_HAT0Y pad pressed --> {}' .format(controller_input['ABS_HAT0Y']) )
    if controller_input['ABS_HAT0Y'] == 1:
        print (" .... go backwards")
        return "backwards"
    elif controller_input['ABS_HAT0Y'] == -1:
        print (" .... go forwards")
        return "forwards"

#-----------------------------------------------------------

def btn_thumbl():  # used to 'squat' the quadrabot
    # Function to do something when BTN_THUMBL is pressed
    print('BTN_THUMBL pressed --> {}' .format(controller_input['BTN_THUMBL']) )
    if controller_input['BTN_THUMBL'] == 1:
        print (" .... squat")
        return "squat"

#-----------------------------------------------------------

def btn_thumbr():  # used to 'bow' the quadrabot
    # Function to do something when BTN_THUMBR is pressed
    print('BTN_THUMBR pressed --> {}' .format(controller_input['BTN_THUMBR']) )
    if controller_input['BTN_THUMBR'] == 1:
        print (" .... bow")
        return "bow"

#-----------------------------------------------------------

def btn_start():  # used to stop quadrabot and reset legs
    # Function to do something when BTN_START is pressed
    print('BTN_START pressed --> {}' .format(controller_input['BTN_START']) )
    if controller_input['BTN_START'] == 1:
        print (" .... reset")
        return "reset"

#-----------------------------------------------------------

def btn_select():  # not used for the 8DOF quadrabot control so nothing 'special' done here
    # Function to do something when BTN_SELECT is pressed
    print('BTN_SELECT pressed --> {}' .format(controller_input['BTN_SELECT']) )

#-----------------------------------------------------------

def btn_mode():  # ANALOG button - not used for the 8DOF quadrabot control so nothing 'special' done here
    # Function to do something when BTN_MODE is pressed
    print('BTN_MODE pressed --> {}' .format(controller_input['BTN_MODE']) )

#-----------------------------------------------------------

def btn_north():
    # Function to do something when BTN_NORTH is pressed
    print('BTN_NORTH pressed --> {}' .format(controller_input['BTN_NORTH']) )
    if controller_input['BTN_NORTH'] == 1:
        print (" .... wave front left")
        return "fLwave"

#-----------------------------------------------------------

def btn_east():
    # Function to do something when BTN_EAST is pressed
    print('BTN_EAST pressed --> {}' .format(controller_input['BTN_EAST']) )
    if controller_input['BTN_EAST'] == 1:
        print (" .... wave back right")
        return "bRwave"

#-----------------------------------------------------------

def btn_south():
    # Function to do something when BTN_SOUTH is pressed
    print('BTN_SOUTH pressed --> {}' .format(controller_input['BTN_SOUTH']) )
    if controller_input['BTN_SOUTH'] == 1:
        print (" .... wave back left")
        return "bLwave"

#-----------------------------------------------------------

def btn_west():
    # Function to do something when BTN_WEST is pressed
    print('BTN_WEST pressed --> {}' .format(controller_input['BTN_WEST']) )
    if controller_input['BTN_WEST'] == 1:
        print (" .... wave front right")
        return "fRwave"

#-----------------------------------------------------------

def btn_tl():  # not used for the 8DOF quadrabot control so nothing 'special' done here
    # Function to do something when BTN_TL is pressed
    print('BTN_TL pressed --> {}' .format(controller_input['BTN_TL']) )

#-----------------------------------------------------------

def btn_tr():  # not used for the 8DOF quadrabot control so nothing 'special' done here
    # Function to do something when BTN_TR is pressed
    print('BTN_TR pressed --> {}' .format(controller_input['BTN_TR']) )

#-----------------------------------------------------------


###################################################################################

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# individual ultrasonic sensor control functions 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Take a distance measurement 
def Measure(): 
    # set the Trigger LOW for a period 
    GPIO.output(pinTrigger, False)
    # Allow module to settle
    time.sleep(0.1)
    # send a 10us HIGH to trigger the sensor's ranging program(8 ultrasound bursts at 40 kHz)
    GPIO.output(pinTrigger, True)
    time.sleep(0.00001)
    GPIO.output(pinTrigger, False)

    InitTime = time.time()
    StartTime = time.time() 
    StopTime = StartTime
    tooshort = "no"
    abort = "no"

    # now record the timestamp for the latest ECHO LOW
    while GPIO.input(pinEcho)==0:
        StartTime = time.time() 
        StopTime = StartTime
        if StartTime-InitTime > 3.0: # taking too long to capture 1st timestamp
            print ("Taking too long to capture 1st timestamp aborting measurement")
            abort = "yes"
            Distance = 0.0
            return (Distance, tooshort, abort)

    while GPIO.input(pinEcho)==1: 
        StopTime = time.time() 
        # If the sensor is too close to an object, the Pi cannot 
        # see the echo quickly enough, so it misses the response and waits and 
        # waits setting a 'trip' time that is unrealistically long so the code can  
        # detect the missed signal problem and say what has happened 
        if StopTime-StartTime >= 0.04:   # a time of 0.04 implies >6.8m !
            print("Hold on there! Return pulse missed or you're too close.") 
            tooshort = "yes"
            Distance = 0.0
            return (Distance, tooshort, abort)

    ElapsedTime = StopTime - StartTime 
    Distance = (ElapsedTime * 34326)/2    # speed of sound in air is 343.26 m/s so distance is in cm
    print ("Distance: " + str(Distance) )
    return (Distance, tooshort, abort)

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Return True if the ultrasonic sensor sees an obstacle within its HowNear limit
def IsNearObstacle(localHowNear): 
    # try 3 times to get a non-zero Distance reading
    sensetry = 0
    goodresult = 0
    while goodresult == 0:
        sensetry = sensetry +1
        Distance, tooshort, abort = Measure()   # use Measure function
        if (Distance > 0.0 and tooshort != "yes" and abort != "yes") or sensetry >=3 :
            goodresult = 1
            print ("sensetry: " + str(sensetry) + " - Distance: " + str(Distance) )

    if tooshort == "yes":
        print ("Obstacle distance: too short to measure")
    elif abort == "yes":
        print ("Missed time stamp - read aborted")
    else:
        print ("Obstacle distance: " + str(Distance)) 
    if Distance < localHowNear and tooshort == "no": 
        print ("** Need to avoid object **")
        return True 
    else: 
        return False


#########################################################################################
# Move back a little, then turn right or left on alternate tries - walking robot version
#########################################################################################
def AvoidObstacle(leftright="right"): 
    # Back off a little 
    print("Backwards a number of movement cycles") 
    # the number of cycles can be 'tuned' and set in the 'defaults' to achieve an optimum result
    walking(filedesc, "backward", ReverseCycles, backFRL, backFRH, backBRL, backBRH, backFLL, backFLH, backBLL, backBLH) 

    # Turn right or left about 120deg (typically 3 cycles) but the number
    #  of cycles can be 'tuned' and set in the 'defaults' to achieve an optimum result
    if leftright == "right":
        print("** turn Right to avoid obstacle **") 
        make_turn(filedesc, "right", TurnCycles, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)
    else:
        print("** turn Left to avoid obstacle **") 
        make_turn(filedesc, "left", TurnCycles, leftFRL, leftFRH, leftBRL, leftBRH, leftFLL, leftFLH, leftBLL, leftBLH)

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to write text to a designated ram drive file  
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def writeramdrive(text,path):
    # open ram drive file to write
    ramfile = open(str(path), "w") # full path with file name passed as a variable
    ramfile.write(str(text))
    ramfile.flush()
    # close the ram drive file
    ramfile.close()
    return();

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to read text from a designated ram drive file   
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def readramdrive(path):
    # open ram drive file to read
    ramfile = open(str(path), "r") # full path with file name passed as a variable
    readtext = ramfile.read()
    # close the ram drive file
    ramfile.close()
    return(readtext);


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to write the last command to its SD 'hard' log file  
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def writecommandlog(lastcommand):
    # open command log file to write
    commandfile = open("/home/pi/logfiles/quadrabot_logs/quadrabot_last_command.txt", "w") # file path hardcoded
    commandfile.write(str(lastcommand))
    # close the log file
    commandfile.close()
    return();


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to write interrupt text to a 'memory' virtual log file using a simple text memory file with io.StringIO 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def writeinterruptlog(interrupttext):
    # assumes the interrupt virtual memory log file has already been established as 'interrupt'
    interrupt.write(str(interrupttext))
    # rewind the log file
    interrupt.seek(0)
    return();


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to read the last command from its SD 'hard' log file  
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def readcommandlog():
    # open command log file to read
    commandfile = open("/home/pi/logfiles/quadrabot_logs/quadrabot_last_command.txt", "r") # file path hardcoded
    lastcommand = commandfile.read()
    # close the log file
    commandfile.close()
    return(lastcommand);


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to read interrupt text from a 'memory' virtual log file using a simple text memory file with io.StringIO  
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def readinterruptlog():
    # assumes the interrupt virtual memory log file has already been established as 'interrupt'
    lastinterrupt = interrupt.getvalue()
    # rewind the log file
    interrupt.seek(0)
    return(lastinterrupt);

#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to write the default set to its log file 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def writedefaults(defaults):
    # open default log file to write
    defaultfile = open("/home/pi/logfiles/quadrabot_logs/quadrabot_default.txt", "w") # file path hardcoded
    defaultfile.write(str(defaults))
    # close the log file
    defaultfile.close()
    return();


#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# function to read the current default set from its log file 
#
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
def readdefaults():
    # open default file to read
    defaultfile = open("/home/pi/logfiles/quadrabot_logs/quadrabot_default.txt", "r") # file path hardcoded
    readdefaults = defaultfile.read()
    defaults = eval(readdefaults)
    # close the log file
    defaultfile.close()
    return(defaults);


###################################################################################
#
# routine to shut down the Flask web server - may not always be used
#
###################################################################################
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    print ("flask shutdown func: " + str(func))

    func()


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
def make_turn(fd, dir, cycles, dirFRL, dirFRH, dirBRL, dirBRH, dirFLL, dirFLH, dirBLL, dirBLH):
    # not using the dir(ection) parameter - but left in just in case
    #loop through the time slices for n cycles
    for n in range(0,int(cycles)):
        # loop through each servo for 16 time slices
        for i in range(0,16):
            quadrabot_servo.setServo(fd, FRONT_RIGHT_LEG, dirFRL[i], 0)
            quadrabot_servo.setServo(fd, FRONT_RIGHT_HIP, dirFRH[i], 0)
            quadrabot_servo.setServo(fd, BACK_RIGHT_LEG, dirBRL[i], 0)
            quadrabot_servo.setServo(fd, BACK_RIGHT_HIP, dirBRH[i], 0)
            quadrabot_servo.setServo(fd, FRONT_LEFT_LEG, dirFLL[i], 0)
            quadrabot_servo.setServo(fd, FRONT_LEFT_HIP, dirFLH[i], 0)
            quadrabot_servo.setServo(fd, BACK_LEFT_LEG, dirBLL[i], 0)
            quadrabot_servo.setServo(fd, BACK_LEFT_HIP, dirBLH[i], 0)
            time.sleep(0.1) # will need to be fine-tuned to ensure the time slice movements complete
    #  reset all the leg servos to the 75% DOWN and midway position
    reset_legs(fd)

    return()
##################

##################################################################################
###        function to walk forwards or backwards using the C library         ####
##################################################################################
def walking(fd, dir, cycles, dirFRL, dirFRH, dirBRL, dirBRH, dirFLL, dirFLH, dirBLL, dirBLH):
    # not using the dir(ection) parameter - but left in just in case
    #loop through the time slices for n cycles
    for n in range(0,int(cycles)):
        # loop through each servo for 16 time slices
        for i in range(0,16):
            quadrabot_servo.setServo(fd, FRONT_RIGHT_LEG, dirFRL[i], 0)
            quadrabot_servo.setServo(fd, FRONT_RIGHT_HIP, dirFRH[i], 0)
            quadrabot_servo.setServo(fd, BACK_RIGHT_LEG, dirBRL[i], 0)
            quadrabot_servo.setServo(fd, BACK_RIGHT_HIP, dirBRH[i], 0)
            quadrabot_servo.setServo(fd, FRONT_LEFT_LEG, dirFLL[i], 0)
            quadrabot_servo.setServo(fd, FRONT_LEFT_HIP, dirFLH[i], 0)
            quadrabot_servo.setServo(fd, BACK_LEFT_LEG, dirBLL[i], 0)
            quadrabot_servo.setServo(fd, BACK_LEFT_HIP, dirBLH[i], 0)
            time.sleep(0.1) # will need to be fine-tuned to ensure the time slice movements complete

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

# /etc/fstab should have been edited to set up a ram drive for the interprocess communication text file
# it should be something like the text below so that both root and the user can read/write to the folder
# none    /mnt/interproc01    ramfs    noauto,user,size=2M,mode=0770    0    0
#   /mnt/interproc01 is a mount point, where the ramfs filesystem will be mounted and this directory should exist.
#   noauto option prevents this to be mounted automatically (e.g. at system's boot up)
#   user makes this mountable by individual regular users
#   size sets this "ramdisk's" size
#   mode is very important, with the octal code 0770 only root and the user who mounted this filesystem, will be able to 
#    read and write to the drive, not the others 
#   PLEASE NOTE only one user can use the ram drive at any one time!

import os            # import the os library
os.system('mount /mnt/interproc01')    # mount the ramdrive in the target folder that must already exist
print("ram drive mounted for the interprocess communication")
# four separate ram drive files set up (just in case!)
writeramdrive("standby","/mnt/interproc01/proc_message01.txt") # write start-up text to interprocess comms file 01
writeramdrive("standby","/mnt/interproc01/proc_message02.txt") # write start-up text to interprocess comms file 02
writeramdrive("no","/mnt/interproc01/proc_message03.txt")      # write start-up text to interprocess comms file 03
writeramdrive("no","/mnt/interproc01/proc_message04.txt")      # write start-up text to interprocess comms file 04
last_procmsg = "startup"    # initialise the last procmsg value to a non-operation value

import time   # this imports the module to allow various time functions to be used

# Get the various defaults from their log file
defaults = readdefaults()

###################################
# 128x64 display with hardware I2C:
###################################

import Adafruit_SSD1306  # this is the set of software functions for the 128x64 OLED display hardware

# import the standard Python Image Library (PIL) modules to draw images
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

RST = None     # on the Pi OLED this pin is not used

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
# use i2cdetect -y 1 to check what is connected

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Use a drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# First define some constants to allow easy resizing of what is put to the display.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Load default font - need to use the full path to any designated font other than the default
# note the default font is quite small (size 8) 
# font = ImageFont.load_default()

# should be able to use any of the fonts that are usually installed at /usr/share/fonts/
# example using /usr/share/fonts/truetype/lato/Lato-Regular.ttf
font = ImageFont.truetype('/usr/share/fonts/truetype/lato/Lato-Regular.ttf', 16)  # using font size 16

# Draw a black filled box to clear the image and then display it.
draw.rectangle((0,0,width,height), outline=0, fill=0)
disp.image(image)
disp.display()

# create and show start-up text
clearOLED(width, height, image)
line1 = "* system starting *"
line2 = " "
line3 = " "
line4 = " "
OLED_update = 0
print ("displaying the system starting text")
clearOLED(width, height, image)
OLED_4lines(line1, line2, line3, line4, top, font, image)
time.sleep(1)   # short pause so that this display stays on a while

####################################
# wireless controller set up
####################################
from inputs import get_gamepad  # the inputs library is from https://pypi.org/project/inputs (https://github.com/zeth/inputs)
from inputs import devices      #  but the main code (inputs.py) is included in the code folder for convenience
                                #  a custom version (inputs_custom.py) is also included but not yet used)
for device in devices:
    print(device)

# Dictionary of the 19 game controller buttons/joysticks on the PiHut witeless controller
# which is recognised by the 'inputs' module as a "MS X-Box 360 pad"
controller_input = {'BTN_THUMBL': 0, 'ABS_X': 0, 'ABS_Y': 0, 'BTN_THUMBR': 0,  'ABS_RX': 0, 'ABS_RY': 0, 
                    'BTN_START': 0, 'BTN_SELECT': 0, 'BTN_MODE': 0,  'ABS_HAT0X': 0, 'ABS_HAT0Y': 0, 
                    'BTN_WEST': 0, 'BTN_NORTH': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0,
                    'BTN_TL': 0, 'BTN_TR': 0, 'ABS_Z': 0, 'ABS_RZ': 0 }

#wautostop = defaults['WautoStop']  # not sure this is needed

# allow C libraries to be used - but just for servo control
from ctypes import *

import RPi.GPIO as GPIO # Import the GPIO Library for slide switch and u/s sensor usage
# set the Broadcom pin numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

####################################
# slide switch set up
####################################
print("slide switch control set up")
# Set pins as output and input
# Set variables for the slide switches connected to the GPIO pins
onoff = int(defaults['onoff'])          # main on/off slide switch usually connected to GPIO#9
auto_demo = int(defaults['auto_demo'])  # auto/demo slide switch usually connected to GPIO#10
web = int(defaults['web'])              # web on/off slide switch usually connected to GPIO#11
print (" slide switch GPIOs: " + str(onoff) + " - " + str(auto_demo) + " - " + str(web) )
# set the slide switch pins as INPUT
GPIO.setup(onoff, GPIO.IN)
GPIO.setup(auto_demo, GPIO.IN)
GPIO.setup(web, GPIO.IN)

# set initial switch states to something undefined so that the program checks can run from the start
state_onoff = 2
state_auto_demo = 2
state_web = 2

####################################
# ultrasonic sensor set up
####################################
print("Ultrasonic Measurement set up")
# Set variables for the ultrasonic sensor Trigger and Echo pins
pinTrigger = int(defaults['pinTrigger'])  # Trigger pin - usually 17
pinEcho = int(defaults['pinEcho'])        # Echo pin - usually 4
print (" ultrasonic sensor GPIOs: " + str(pinTrigger) + " - " + str(pinEcho) )
# set the Trigger and Echo pins as OUTPUT and INPUT respectively
GPIO.setup(pinTrigger, GPIO.OUT)  # Trigger
GPIO.setup(pinEcho, GPIO.IN)      # Echo

####################################
# simple memory 'file'
####################################
# allow simple text memory files with io.StringIO (earlier legacy usage - could have used ramfs instead!)
from io import StringIO
# open the virtual interrupt text file  
interrupt = StringIO()
writeinterruptlog('default')
print ("interrupt file text initial value: " + str(readinterruptlog()))


####################################
# servo set up
####################################
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

#[ 510, 370, 280, 200, 110 ],    # FRL 10
FRONT_RIGHT_LEG_up100   = 110
FRONT_RIGHT_LEG_up75    = 200
FRONT_RIGHT_LEG_down50  = 280
FRONT_RIGHT_LEG_down75  = 370
FRONT_RIGHT_LEG_down100 = 510

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
[ 510, 370, 280, 200, 110 ],    # FRL 10
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

fwdFRL = [ 370, 370, 370, 370, 370, 280, 280, 370, 370, 370, 370, 370, 370, 370, 370, 370 ] # 100%: 110 - 50%: 300
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

backFRL = [ 370, 370, 370, 370, 370, 280, 280, 370, 370, 370, 370, 370, 370, 370, 370, 370 ] # 100%: 110 - 50%: 300
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

rightFRL = [ 370, 370, 370, 370, 370, 280, 280, 370, 370, 370, 370, 370, 370, 370, 370, 370 ] # 100%: 110 - 50%: 300
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

leftFRL = [ 370, 370, 370, 370, 370, 280, 280, 370, 370, 370, 370, 370, 370, 370, 370, 370 ] # 100%: 110 - 50%: 300
leftFRH = [ 252, 218, 184, 150, 150, 310, 490, 490, 490, 490, 456, 422, 388, 354, 320, 286 ]
															
leftBRL = [ 240, 330, 330, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240 ] # 100%: 540 - 50%: 330
leftBRH = [ 205, 350, 520, 520, 520, 520, 489, 458, 427, 396, 365, 334, 303, 272, 241, 205 ]
															
leftFLL = [ 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 240, 350, 350, 240 ] # 100%: 540 - 50%: 350
leftFLH = [ 560, 560, 522, 484, 446, 408, 370, 332, 294, 256, 218, 180, 180, 350, 560, 560 ]
															
leftBLL = [ 415, 415, 415, 415, 415, 415, 415, 415, 415, 300, 300, 415, 415, 415, 415, 415 ] # 100%: 110 - 50%: 300
leftBLH = [ 427, 396, 365, 334, 303, 272, 241, 205, 205, 350, 520, 520, 520, 520, 489, 458 ]


# check_slideswitch(opmode, debug) is the routine to check the state of the slide switches
# the current/last opmode value is passed to the function and the function returns the current value
# debug on/off is 1/0
# opmode = 0 means 'idle'
# opmode = 1 means 'demo'
# opmode = 2 means 'avoid'
# opmode = 3 means 'web'
# opmode = 4 means 'stop_web'
# opmode = 5 means 'wc_mode' i.e. wireless controller mode
# opmode = 9 means an undefined operational mode

# get an initial opmode setting
global opmode
opmode = 10      # initial opmode set to a non-use number: real options as above
opmode = check_slide_switches(10, 1)  # initially send a 'opmode_last' of 10 that is 'impossible'
global opmode_last
opmode_last = 10

# set the squat and then the stand-up mode to show that the robot has fully started up and is ready
set_squat(filedesc)
time.sleep(0.5)
reset_legs(filedesc)

# initialise other miscellaneous movement parameters from the 'read in' defaults array
HowNear = int(defaults['HowNear'])              # distance check made bythe ultrasonic sensor - usually c. 12
TurnCycles = int(defaults['TurnCycles'])        # number of servo cycles to effect a turn during 
                                                #       the avoidance routine - usually 3
ReverseCycles = int(defaults['ReverseCycles'])  # number of servo cycles to reverse during 
                                                #       the avoidance routine - usually 1
Alternate = int(defaults['Alternate'])          # the number of times to turn left/right before changing direction
alt_times = 0                                   # initialise Alternate counter
leftright = "right"                             # just a start value - alternates between left and right

# set some initial defaults for the wireless controller mode
last_left_x = 999
last_left_y = 999
last_right_x = 999
last_right_y = 999

# create and show system ready text
clearOLED(width, height, image)
line1 = "* system ready *"
line2 = " "
line3 = " "
line4 = " "
OLED_update = 0
print ("displaying the system ready text")
clearOLED(width, height, image)
OLED_4lines(line1, line2, line3, line4, top, font, image)
time.sleep(1)   # short pause so that this display stays on a while

########################################################
# code to control the walking robot goes below this line
########################################################

try:        # using try ahead of the 'while' loop allows CTRL-C to be used to cleanly end the cycle

    # the following very large while-loop is continuously checking the slide switch settings
    # and depending upon the 'mix' of settings an opmode value is set to enable a particular operation

    ######################
    #  start of main loop
    ######################
    while True:
        time.sleep(0.1)  # pause for 0.1 seconds to provide a processing gap for other activity
        # get latest opmode update from the switch settings
        opmode = check_slide_switches(opmode, 1)
        if opmode != opmode_last:  # print out the opmode if it has changed but don't reset it now, done later
            print ("new initial switch settings and therefore new opmode: " + str(opmode))


        ###############
        #  'idle' mode
        ###############
        if opmode == 0:
            # if here then in the main 'logical 'off' mode waiting for a slide switch combo to do something
            if opmode_last != 0:
                print ("opmode is idle - in logical OFF mode")
                opmode_last = 0
                # just do the following once when the idle mode is first set
                # set all the servos to a firm standing position
                #  and set all the hip servos to mid position
                reset_legs(filedesc)
                clearOLED(width, height, image)
                line1 = "system idle/OFF"
                line2 = "* legs reset *" 
                line3 = " " 
                line4 = " " 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                time.sleep(2)  # pause for 2 seconds so display can be seen


        ###############################
        ##  obstacle avoidance mode  ##
        ###############################
        elif opmode == 2:
            # if here then do all the avoid obstacle stuff
            if opmode_last != 2:
                print ("obstacle avoidance mode")
                opmode_last = 2
                clearOLED(width, height, image)
                line1 = "* avoid mode *"
                line2 = "** moving **" 
                line3 = "** forward **" 
                line4 = " " 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                #time.sleep(2)  # pause for 2 seconds so display can be seen

            # move forward 1 cycle and then check for an obstacle and avoid it if too near then 
            # allow to loop back through the main WHILE loop to recheck the switches and then it
            # will return here to repeat the move/avoid cycle until the switches are changed

            walking(filedesc, "forward", 1, fwdFRL, fwdFRH, fwdBRL, fwdBRH, fwdFLL, fwdFLH, fwdBLL, fwdBLH)
            #print (" move forward 1 cycle ")
            if IsNearObstacle(HowNear): 
                print (" obstacle detected - taking avoidance action ")
                clearOLED(width, height, image)
                line1 = "* avoid mode *"
                line2 = "** obstacle **" 
                line3 = "** detected **" 
                line4 = " " 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                time.sleep(1)  # pause for 1 seconds so display can be seen
                if leftright == "right":
                    leftright = "left"
                else:
                    leftright = "right"
                print (" moving back and turning " + str(leftright))
                AvoidObstacle(leftright)
                clearOLED(width, height, image)
                line1 = "* avoid mode *"
                line2 = "** moving **" 
                line3 = "** forward **" 
                line4 = " " 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                time.sleep(1)  # pause for 1 seconds so display can be seen


        ################################
        ##  wireless controller mode  ##
        ################################
        elif opmode == 5:
            # if here then use the wireless controller to control movement and to do 'set moves'
            if opmode_last != 5:    # do the one time actions when mode is first changed
                print ("wireless controller mode")
                opmode_last = 5
                # display the wireless controller mode text on the OLED
                print ("displaying the wireless controller mode text")
                clearOLED(width, height, image)
                line1 = "wireless control"
                line2 = "use left keypad" 
                line3 = "    or" 
                line4 = "various buttons" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                #time.sleep(1)  # pause for 1 seconds so display can be seen

            # wireless controller 'actions' are now done with a opmode/slide switch check in the loop
            # this will also trigger an interrupt to allow the flow back thru the main WHILE loop
            # to recheck the slide switches from which a different mode can be selected 

            # wireless controller comms uses the Python 'inputs' module
            wless = True
            while wless == True:   # wless set to either True or False to maintain or stop wireless mode
                                   #  wless is changed to False in the SELECT button press 'event' function 
                # Get next controller Input
                control_code = gamepad_update()
                #print (" controller code: " + str(control_code) )

                # check for key presses using a series of if's rather than if/else 
                # so that they are all checked before the slide switch check 
                # which should keep the movement more continuous
                # Gamepad button/joystick filter

                # check START key for reset/stand movement
                if control_code == 'BTN_START' and btn_start() == "reset":
                    print('START button pressed since last check')
                    print ("reset legs to stand up position")
                    reset_legs(filedesc)

                # check D pad left or right for turn left or right movement
                if control_code == 'ABS_HAT0X':
                    direction = abs_hat0x()
                    if direction == "left":
                        print('D-LEFT pressed since last check')
                        print ("turning left")
                        make_turn(filedesc, "left", 1, leftFRL, leftFRH, leftBRL, leftBRH, leftFLL, leftFLH, leftBLL, leftBLH)
                    elif direction == "right":
                        print('D-RIGHT pressed since last check')
                        print ("turning right")
                        make_turn(filedesc, "right", 1, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)
                    reset_legs(filedesc) # do a reset to realign the legs normally after a turn cycle

                # check D pad up or down for forwards or backwards movement
                if control_code == 'ABS_HAT0Y':
                    direction = abs_hat0y()
                    if direction == "forwards":
                        print('D-UP pressed since last check')
                        # move forward 1 cycle
                        print ("moving forwards")
                        walking(filedesc, "forward", 1, fwdFRL, fwdFRH, fwdBRL, fwdBRH, fwdFLL, fwdFLH, fwdBLL, fwdBLH)
                    if direction == "backwards":
                        print('D-DOWN pressed since last check')
                        print ("moving backwards")
                        walking(filedesc, "backward", 1, backFRL, backFRH, backBRL, backBRH, backFLL, backFLH, backBLL, backBLH)
                    reset_legs(filedesc)  # do a reset to realign the legs normally after a forwards or backwards cycle

                # check the square button for doing a front left leg wave
                if control_code == 'BTN_NORTH' and btn_north() == "fLwave":
                    print('SQUARE pressed since last check')
                    print ("doing a front left leg wave")
                    # move the FRONT_RIGHT_HIP forward then do the wave
                    quadrabot_servo.setServo(filedesc, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd100, 0)
                    time.sleep(0.5)
                    wave_leg(filedesc, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd75, FRONT_LEFT_HIP_back75, FRONT_LEFT_LEG, FRONT_LEFT_LEG_up100, FRONT_LEFT_LEG_down75, 3)
                    #  reset all the leg servos to the 75% DOWN and midway position
                    reset_legs(filedesc)

                # check the triangle button for doing a front right leg wave
                if control_code == 'BTN_WEST' and btn_west() == "fRwave":
                    print('TRIANGLE button pressed since last check')
                    print ("doing a front right leg wave")
                    # move the FRONT_LEFT_HIP forward then do the wave
                    quadrabot_servo.setServo(filedesc, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd100, 0)
                    time.sleep(0.5)
                    wave_leg(filedesc, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd75, FRONT_RIGHT_HIP_back75, FRONT_RIGHT_LEG, FRONT_RIGHT_LEG_up100, FRONT_RIGHT_LEG_down75, 3)
                    #  reset all the leg servos to the 75% DOWN and midway position
                    reset_legs(filedesc)

                # check the cross button for doing a back left leg wave
                if control_code == 'BTN_SOUTH' and btn_south() == "bLwave":
                    print('CROSS pressed since last check')
                    print ("doing a back left leg wave")
                    # move the BACK_RIGHT_HIP forward then do the wave
                    quadrabot_servo.setServo(filedesc, BACK_RIGHT_HIP, BACK_RIGHT_HIP_back75, 0)
                    time.sleep(0.5)
                    wave_leg(filedesc, BACK_LEFT_HIP, BACK_LEFT_HIP_fwd75, BACK_LEFT_HIP_back75, BACK_LEFT_LEG, BACK_LEFT_LEG_up100, BACK_LEFT_LEG_down75, 3)
                    #  reset all the leg servos to the 75% DOWN and midway position
                    reset_legs(filedesc)

                # check the circle button for doing a back right leg wave
                if control_code == 'BTN_EAST' and btn_east() == "bRwave":
                    print('CIRCLE button pressed since last check')
                    print ("doing a back right leg wave")
                    # move the BACK_LEFT_HIP forward then do the wave
                    quadrabot_servo.setServo(filedesc, BACK_LEFT_HIP, BACK_LEFT_HIP_back75, 0)
                    time.sleep(0.5)
                    wave_leg(filedesc, BACK_RIGHT_HIP, BACK_RIGHT_HIP_fwd75, BACK_RIGHT_HIP_back75, BACK_RIGHT_LEG, BACK_RIGHT_LEG_up100, BACK_RIGHT_LEG_down75, 3)
                    #  reset all the leg servos to the 75% DOWN and midway position
                    reset_legs(filedesc)


                # check the right joystick button for doing a front bow
                if control_code == 'BTN_THUMBR' and btn_thumbr() == "bow":
                    print('right JOYSTICK button pressed since last check')
                    print ("doing a forward bow")
                    set_bow(filedesc)
                    time.sleep(2)
                    #  reset all the leg servos to the 75% DOWN and midway position
                    reset_legs(filedesc)

                # check the left joystick button for doing a squat
                if control_code == 'BTN_THUMBL' and btn_thumbl() == "squat":
                    print('left JOYSTICK button pressed since last check')
                    print ("doing a squat")
                    set_squat(filedesc)
                    time.sleep(2)
                    #  reset all the leg servos to the 75% DOWN and midway position
                    reset_legs(filedesc)


                # get latest opmode update from the switch settings
                print ("checking opmode")
                opmode = check_slide_switches(opmode, 1)
                print ("opmode: " + str(opmode) )
                if opmode != opmode_last:  # print out the opmode if it has changed but don't reset it now, done later
                    print ("new switch settings and therefore new opmode: " + str(opmode))
                    wless = False
                    break
                # ....

            # wireless controller mode interrupted...
            reset_legs(filedesc)
            print('wireless controller mode stopped')

        ###############################
        ##         demo mode         ##
        ###############################
        elif opmode == 1:
            # if here then do all the demo stuff
            if opmode_last != 1:   # do the following for just the first 'demo' cycle
                clearOLED(width, height, image)
                line1 = "** demo mode **"
                line2 = "waving, walking" 
                line3 = "turning, squats" 
                line4 = "and a final bow" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                time.sleep(3)  # short pause so that the robot can be positioned after the switches are set
                # just do the following once when the demo mode is first set
                print ("start the various demo routines")
                print ("starting the waving")
                print ("  ")

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                #############################
                # wave the FRONT_RIGHT_LEG
                # move the FRONT_LEFT_HIP forward
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** waving ......" 
                line3 = "front, right leg" 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                quadrabot_servo.setServo(filedesc, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd100, 0)
                time.sleep(1)
                wave_leg(filedesc, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd75, FRONT_RIGHT_HIP_back75, FRONT_RIGHT_LEG, FRONT_RIGHT_LEG_up100, FRONT_RIGHT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                #############################
                # wave the FRONT_LEFT_LEG
                # move the FRONT_RIGHT_HIP forward
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** waving ......" 
                line3 = "front, left leg" 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                quadrabot_servo.setServo(filedesc, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd100, 0)
                time.sleep(1)
                wave_leg(filedesc, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd75, FRONT_LEFT_HIP_back75, FRONT_LEFT_LEG, FRONT_LEFT_LEG_up100, FRONT_LEFT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                #############################
                # wave the BACK_LEFT_LEG
                # move the BACK_RIGHT_HIP slightly backward
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** waving ......" 
                line3 = "back, left leg" 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                quadrabot_servo.setServo(filedesc, BACK_RIGHT_HIP,  BACK_RIGHT_HIP_back75, 0)
                time.sleep(1)
                wave_leg(filedesc, BACK_LEFT_HIP, BACK_LEFT_HIP_fwd75, BACK_LEFT_HIP_back75, BACK_LEFT_LEG, BACK_LEFT_LEG_up100, BACK_LEFT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                #############################
                # wave the BACK_RIGHT_LEG
                # move the BACK_LEFT_HIP slightly backward
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** waving ......" 
                line3 = "back, right leg" 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                quadrabot_servo.setServo(filedesc, BACK_LEFT_HIP, BACK_LEFT_HIP_back75, 0)
                time.sleep(1)
                wave_leg(filedesc, BACK_RIGHT_HIP, BACK_RIGHT_HIP_fwd75, BACK_RIGHT_HIP_back75, BACK_RIGHT_LEG, BACK_RIGHT_LEG_up100, BACK_RIGHT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                ###########################################
                ###     walking forwards 4 cycles       ###
                ###########################################
                print("  ")
                print(" **** forward walking **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** walking......" 
                line3 = "forward 4 cycles" 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)

                walking(filedesc, "forward", 4, fwdFRL, fwdFRH, fwdBRL, fwdBRH, fwdFLL, fwdFLH, fwdBLL, fwdBLH)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                ###########################################
                ###     walking backwards 4 cycles      ###
                ###########################################
                print("  ")
                print(" **** backward walking **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** walking......" 
                line3 = "back 4 cycles" 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)

                walking(filedesc, "backward", 4, backFRL, backFRH, backBRL, backBRH, backFLL, backFLH, backBLL, backBLH)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                ###########################################
                ###          turning right              ###
                ###########################################
                print("  ")
                print(" **** turning right **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** turning......" 
                line3 = "*** right " 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)

                make_turn(filedesc, "right", 2, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                ###########################################
                ###          turning left               ###
                ###########################################
                print("  ")
                print(" **** turning left **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** turning......" 
                line3 = "*** left " 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)

                make_turn(filedesc, "left", 2, leftFRL, leftFRH, leftBRL, leftBRH, leftFLL, leftFLH, leftBLL, leftBLH)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                ###########################################
                ###               squat                 ###
                ###########################################
                print("  ")
                print(" **** squatting **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** squatting...." 
                line3 = "*** --------- " 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)

                set_squat(filedesc)
                time.sleep(5)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)

            # double check the latest opmode update from the switch settings
            opmode = check_slide_switches(opmode, 1)
            if opmode == 1 and opmode_last != 1:    # do this demo if still in demo_mode but only for 1 cycle
                ###########################################
                ###           bow forward               ###
                ###########################################
                print("  ")
                print(" **** bowing **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "*** demo mode ***"
                line2 = "*** bowing......." 
                line3 = "*** forwards  " 
                line4 = "*****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)

                set_bow(filedesc)
                time.sleep(5)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)


            ###########################################
            ###         end of non-web demos        ###
            ###########################################
            # once the above demos are complete the main WHILE loop continues and
            #  the switches need to be changed for the demo to repeat
            
            if opmode == 1 and opmode_last != 1:    # print out where we are but only once
                print(" ****           end of demo                 **** ")
                print(" **** reset switches for further operations **** ")
                opmode_last = 1
                #  reset all the leg servos to the 75% DOWN and midway position again - just in case
                reset_legs(filedesc)
                clearOLED(width, height, image)
                line1 = "*demo mode ended"
                line2 = "*** legs ......" 
                line3 = "*** reset  " 
                line4 = "****************" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)


        ################################
        ##  stopped web control mode  ##
        ################################
        elif opmode == 4:
            if opmode_last != 4:
                print ("web control stopped - ** need to reset sliders **")
                opmode_last = 4
                # just do the following once when the avoid mode is first set
                # set all the servos to a firm standing position
                #  and set all the hip servos to mid position
                reset_legs(filedesc) 
                clearOLED(width, height, image)
                line1 = "web mode stopped"
                line2 = "* reset slide *" 
                line3 = "** switches **" 
                line4 = "* legs reset *" 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                #time.sleep(2)  # pause for 2 seconds so display can be seen

        ########################
        ##  web control mode  ##
        ########################
        elif opmode == 3:
            # if here then read from the interprocess communication file to get 
            # any updated 'actions' set by the 'web' app which runs in parallel
            # but first set the robot into a 'ready stance'
            if opmode_last != 3:
                opmode_last = 3

                # do the following once when the web mode is first set
                #  set all the servos to a firm standing position
                #  and set all the hip servos to mid position
                reset_legs(filedesc)
                clearOLED(width, height, image)
                line1 = "** web mode **"
                line2 = "**************" 
                line3 = "* legs reset *" 
                line4 = " " 
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                #time.sleep(2)  # pause for 2 seconds so display can be seen

            # keep checking the interprocess communication file in /mnt/interproc01/
            procmsg = readramdrive("/mnt/interproc01/proc_message01.txt")
            if procmsg != last_procmsg:
                print ("interprocess message: " + str(procmsg))
                #last_procmsg = procmsg   # don't update here as its done per item later

            #-----------------------------------------------
            # check what the procmsg is and act accordingly
            #-----------------------------------------------

            # first check the various 'standby' or top level menus like 'select_mode', procmsg options:
            if procmsg == "standby" or procmsg == "startup" or procmsg == "select_mode" or procmsg == "demo_mode" or procmsg == "autonomous_mode" or procmsg == "run_about_mode" or procmsg == "switch_control" or procmsg == "maintenance_mode" or procmsg == "reset_defaults" or procmsg == "reboot":
                #print ("top level procmsg found: " + str(procmsg) )
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "** legs reset **" 
                if procmsg == "reboot":
                    line4 = "*system reboot*"
                    clearOLED(width, height, image)
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    time.sleep(2)
                    os.system("sudo reboot")

                if procmsg != last_procmsg:
                    # just put the robot into its stand-up stance
                    reset_legs(filedesc) 
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg
                    clearOLED(width, height, image)
                    if procmsg == "standby" or procmsg == "startup" or procmsg == "select_mode" :
                        line4 = " " 
                    elif procmsg == "demo_mode":
                        line4 = "** demo mode **" 
                    elif procmsg == "autonomous_mode":
                        line4 = "** auto mode **"
                    elif procmsg == "run_about_mode":
                        line4 = "*run about mode*"
                    elif procmsg == "switch_control":
                        line4 = "> switch control"
                    elif procmsg == "maintenance_mode":
                        line4 = "maintenance mode"
                    elif procmsg == "reset_defaults":
                        line4 = "*reset defaults*"
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    #time.sleep(2)  # pause for 2 seconds so display can be seen



            #------------------------------------
            # now check the various demo options
            #------------------------------------

            if procmsg == "leg_reset":
                print("  ")
                print(" **** resetting quadrabot **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "** resetting **" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "turn_left":
                print("  ")
                print(" **** turning left **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "**turning left**" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                make_turn(filedesc, "left", 2, leftFRL, leftFRH, leftBRL, leftBRH, leftFLL, leftFLH, leftBLL, leftBLH)
                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------
 
            elif procmsg == "turn_right":
                print("  ")
                print(" **** turning right **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "**turning right*" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                make_turn(filedesc, "right", 2, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)
                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------
 
            elif procmsg == "forward4":
                print("  ")
                print(" **** forward walking **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "**walking fwd**" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                walking(filedesc, "forward", 4, fwdFRL, fwdFRH, fwdBRL, fwdBRH, fwdFLL, fwdFLH, fwdBLL, fwdBLH)
                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------
 
            elif procmsg == "backwards4":
                print("  ")
                print(" **** backward walking **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "**walking back*" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                walking(filedesc, "backward", 4, backFRL, backFRH, backBRL, backBRH, backFLL, backFLH, backBLL, backBLH)
                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------
 
            elif procmsg == "about_turn_right":
                print("  ")
                print(" **** about turn right **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "about turn right" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                make_turn(filedesc, "right", 4, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)
                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------
 
            elif procmsg == "about_turn_left":
                print("  ")
                print(" **** about turn left **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "about turn left" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                make_turn(filedesc, "left", 4, leftFRL, leftFRH, leftBRL, leftBRH, leftFLL, leftFLH, leftBLL, leftBLH)
                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "wave_front_left":
                print("  ")
                print(" **** wave front left **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "wave front left" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                # move the FRONT_RIGHT_HIP forward
                quadrabot_servo.setServo(filedesc, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd100, 0)
                time.sleep(0.5)
                wave_leg(filedesc, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd75, FRONT_LEFT_HIP_back75, FRONT_LEFT_LEG, FRONT_LEFT_LEG_up100, FRONT_LEFT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "wave_front_right":
                print("  ")
                print(" **** wave front right **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "wave front right" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                # move the FRONT_LEFT_HIP forward
                quadrabot_servo.setServo(filedesc, FRONT_LEFT_HIP, FRONT_LEFT_HIP_fwd100, 0)
                time.sleep(0.5)
                wave_leg(filedesc, FRONT_RIGHT_HIP, FRONT_RIGHT_HIP_fwd75, FRONT_RIGHT_HIP_back75, FRONT_RIGHT_LEG, FRONT_RIGHT_LEG_up100, FRONT_RIGHT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "wave_back_left":
                print("  ")
                print(" **** wave back left **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "*wave back left" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                # move the BACK_RIGHT_HIP slightly backward
                quadrabot_servo.setServo(filedesc, BACK_RIGHT_HIP,  BACK_RIGHT_HIP_back75, 0)
                time.sleep(0.5)
                wave_leg(filedesc, BACK_LEFT_HIP, BACK_LEFT_HIP_fwd75, BACK_LEFT_HIP_back75, BACK_LEFT_LEG, BACK_LEFT_LEG_up100, BACK_LEFT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "wave_back_right":
                print("  ")
                print(" **** wave back right **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "wave back right" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                # move the BACK_LEFT_HIP slightly backward
                quadrabot_servo.setServo(filedesc, BACK_LEFT_HIP, BACK_LEFT_HIP_back75, 0)
                time.sleep(0.5)
                wave_leg(filedesc, BACK_RIGHT_HIP, BACK_RIGHT_HIP_fwd75, BACK_RIGHT_HIP_back75, BACK_RIGHT_LEG, BACK_RIGHT_LEG_up100, BACK_RIGHT_LEG_down75, 3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "squat":
                print("  ")
                print(" **** squatting **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "** squatting **" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                set_squat(filedesc)
                time.sleep(3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "bow":
                print("  ")
                print(" **** bowing forward **** ")
                print("  ")
                clearOLED(width, height, image)
                line1 = "** web usage **"
                line2 = "****************" 
                line3 = "*bowing forward*" 
                #leave line four the same as set above
                OLED_4lines(line1, line2, line3, line4, top, font, image)
                set_bow(filedesc)
                time.sleep(3)

                #  reset all the leg servos to the 75% DOWN and midway position
                reset_legs(filedesc)
                last_procmsg = procmsg

            #------------------------------------

            #------------------------------------------
            # now check the various autonomous options
            #------------------------------------------

            elif procmsg == "auto_go":
                if procmsg != last_procmsg:
                    print("  ")
                    print(" **** moving forward **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* auto forward *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    last_procmsg = procmsg
                # move forward 1 cycle and then check for an obstacle and avoid it if too near then allow 
                # it to loop back through the main WHILE loop to recheck the 'procmsg' value and if unchanged 
                # it will return here to repeat the move/avoid cycle until the 'procmsg' is changed
                walking(filedesc, "forward", 1, fwdFRL, fwdFRH, fwdBRL, fwdBRH, fwdFLL, fwdFLH, fwdBLL, fwdBLH)
                print (" move forward 1 cycle ")

            # turn to the right or left after going in one direction for Alternate times
                if IsNearObstacle(HowNear): 
                    print (" obstacle detected - taking avoidance action ")
                    alt_times = alt_times +1
                    if alt_times > Alternate:
                        alt_times = 0
                        if leftright == "right":
                            leftright = "left"
                        else:
                            leftright = "right"
                    print (" moving back and turning " + str(leftright))
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* obstacle! *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    last_procmsg = "obstacle"  # reset last_procmsg so that the OLED is updated after avoidance process
                    AvoidObstacle(leftright)

            #------------------------------------

            elif procmsg == "auto_stop":
                # if here, simply do nothing other than to put the robot into the stand-up stance
                if procmsg != last_procmsg:
                    print("  ")
                    print(" **** auto stopped **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* auto stopped *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    # now put the robot into its stand-up stance
                    reset_legs(filedesc)
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg

            #------------------------------------

            #------------------------------------------
            # now check the various run about options
            #------------------------------------------

            elif procmsg == "run_stop":
                # if here, simply do nothing other than to put the robot into the stand-up stance

                if procmsg != last_procmsg:
                    print("  ")
                    print(" **** run around stopped **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* run stopped *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    # now put the robot into its stand-up stance
                    reset_legs(filedesc)
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg

            #------------------------------------
            elif procmsg == "run_left":

                if procmsg != last_procmsg:   # only do the following once
                    # if here, turn left and go into stand-up stance
                    print("  ")
                    print(" **** running left **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* running left *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    make_turn(filedesc, "left", 2, leftFRL, leftFRH, leftBRL, leftBRH, leftFLL, leftFLH, leftBLL, leftBLH)
                    # now put the robot into its stand-up stance
                    reset_legs(filedesc)
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "run_right":

                if procmsg != last_procmsg:   # only do the following once
                    # if here, turn right and go into stand-up stance
                    print("  ")
                    print(" **** running right **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* running right *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    make_turn(filedesc, "right", 2, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)
                    # now put the robot into its stand-up stance
                    reset_legs(filedesc) 
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "run_forward":
                # if here, run forward continuously 1 cycle at a time until a different procmsg is received in the while loop
                if procmsg != last_procmsg:   # only do the following once
                    print("  ")
                    print(" **** running forward **** ")
                    print("  ")
                    last_procmsg = procmsg
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* running fwd *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                walking(filedesc, "forward", 1, fwdFRL, fwdFRH, fwdBRL, fwdBRH, fwdFLL, fwdFLH, fwdBLL, fwdBLH)


            #------------------------------------

            elif procmsg == "run_backward":
                # if here, run backward continuously 1 cycle at a time until a different procmsg is received in the while loop
                if procmsg != last_procmsg:   # only do the following once
                    print("  ")
                    print(" **** running backward **** ")
                    print("  ")
                    last_procmsg = procmsg
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "* running back *" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                walking(filedesc, "backward", 1, backFRL, backFRH, backBRL, backBRH, backFLL, backFLH, backBLL, backBLH)


            #------------------------------------
            elif procmsg == "run_spin_left":

                if procmsg != last_procmsg:   # only do the following once
                    # if here, spin left 180deg and go into stand-up stance
                    print("  ")
                    print(" **** spinning left 180deg **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "*spinning left*" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    make_turn(filedesc, "left", 4, leftFRL, leftFRH, leftBRL, leftBRH, leftFLL, leftFLH, leftBLL, leftBLH)
                    # now put the robot into its stand-up stance
                    reset_legs(filedesc) 
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg

            #------------------------------------

            elif procmsg == "run_spin_right":

                if procmsg != last_procmsg:   # only do the following once
                    # if here, spin right 180deg and go into stand-up stance
                    print("  ")
                    print(" **** spinning right 180deg **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "*spinning right*" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    make_turn(filedesc, "right", 4, rightFRL, rightFRH, rightBRL, rightBRH, rightFLL, rightFLH, rightBLL, rightBLH)
                    # now put the robot into its stand-up stance
                    reset_legs(filedesc) 
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg

            #------------------------------------

            #---------------------------------------------
            # now check the ultrasonic sensor test option
            #---------------------------------------------

            elif procmsg == "read_echo_reset":

                if procmsg != last_procmsg:   # only do the following once
                    # if here, we are just resetting the cycle
                    print("  ")
                    print(" **** resetting ultrasonic sensor **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "*us sensor reset*" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)
                    last_procmsg = procmsg

            elif procmsg == "read_echo":

                if procmsg != last_procmsg:   # only do the following once
                    # if here, take a reading from the ultrasonic sensor and write out
                    # the value to the interprocess comms file 02 in the ram disc
                    print("  ")
                    print(" **** taking an ultrasonic sensor reading **** ")
                    print("  ")
                    tooshort = "no"
                    abort = "no"
                    # try 5 times to get a non-zero reading
                    sensetry = 0
                    goodresult = 0
                    while goodresult == 0:
                        sensetry = sensetry +1
                        Distance, tooshort, abort = Measure()   # use Measure function
                        if (Distance > 0.0 and tooshort != "yes" and abort != "yes") or sensetry >=5 :
                            goodresult = 1
                            print ("sensetry: " + str(sensetry) + " - Distance: " + str(Distance) )

                    writeramdrive(abort, "/mnt/interproc01/proc_message04.txt")
                    writeramdrive(tooshort, "/mnt/interproc01/proc_message03.txt")
                    fDistance = "%.2f" %Distance  # reformat as a string with 2 decimal places
                    writeramdrive(str(fDistance),"/mnt/interproc01/proc_message02.txt")

                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = str(fDistance) + "cm echo" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)

                    # now put the robot into its stand-up stance (just in case)
                    reset_legs(filedesc) 
                    print ("robot in stand-up stance")
                    last_procmsg = procmsg

            #------------------------------------

            #--------------------------------------------------------
            # now check the various reset default parameters options
            #--------------------------------------------------------

            elif procmsg == "update_pintrigger" or procmsg == "update_pinecho" or procmsg == "update_pinonoff" or procmsg == "update_pinauto_demo" or procmsg == "update_pinweb" or procmsg == "update_hownear" or procmsg == "update_revcycles" or procmsg == "update_turncycles" or procmsg == "update_alternate":

                if procmsg != last_procmsg:   # only do the following once
                    # if here, just print out the procmsg action
                    print("  ")
                    print(" **** updating the default parameter **** ")
                    print("  ")
                    clearOLED(width, height, image)
                    line1 = "** web usage **"
                    line2 = "****************" 
                    line3 = "*default updated*" 
                    #leave line four the same as set above
                    OLED_4lines(line1, line2, line3, line4, top, font, image)

                    last_procmsg = procmsg


            #####################################################################
            # if here loop back to main While loop so switches can be rechecked


        ##########################################
        # end of While loop
        if opmode != opmode_last:
            print (" if here then we are at the end of the While loop - opmode is: " + str(opmode))


except AssertionError:
    print ("Exception routine - opmode is: " + str(opmode))
    print ("AssertionError made as an exception and now ending the Try loop")
    pass

finally:  
    print ("Cleaning up at the end of the program")
    GPIO.cleanup()
    #  reset all the leg servos to the 75% DOWN and midway position
    stand_all_75down(filedesc)
    set_midway(filedesc)
    time.sleep(0.5)
    # clear display
    disp.clear()
    disp.display()
    print("  ")
    print("*******************************************************")
    print("GPIO pins cleaned up and robot put into stand-up stance")
    print("program end")
    print("*******************************************************")
    print("  ")

