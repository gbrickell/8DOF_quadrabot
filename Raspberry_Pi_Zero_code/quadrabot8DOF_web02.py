#!/usr/bin/python

# quadrabot8DOF_web02.py - quadrabot 8DOF walking robot web controller
# provides a browser interface and sets the required action into an
# interprocess communication file held in ram disc which is set up in the 'action' app

# must use sudo to run this app since Flask is using its 'production' server on port 80
# command:  sudo python3 /home/pi/quadrabot/quadrabot8DOF_web02.py
# Enmore 220329

## cron ##
# start main python control code for the 8DOF quadrabot
#@reboot python3 /home/pi/quadrabot/quadrabot8DOF_action05.py
# start web interface code for the 8DOF quadrabot
#@reboot sudo python3 /home/pi/quadrabot/quadrabot8DOF_web02.py

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
##################


##################################################################################
###                    main code                                              ####
##################################################################################

import os            # import the os library
import time               # this imports the module to allow various time functions to be used

# Flask web server set up
from flask import Flask, render_template
from flask import request
from flask import Response
quadrabot_app01 = Flask(__name__)  # creates a Flask object called quadrabot_app01 for the web server operation

# allow simple text memory files with io.StringIO
from io import StringIO
# open the virtual interrupt text file  
interrupt = StringIO()
writeinterruptlog('default')
print ("interrupt file text initial value: " + str(readinterruptlog()))

# sleep for a period to ensure that the 'action' app has fully started first
# before trying to read from the ram drive
time.sleep(10)

print ("web server should be operational now")

# ram drive should have been started by the main Python control code (quadrabot8DOF_actionXX.py)
print("ram drive should already be mounted")
procmsg = readramdrive("/mnt/interproc01/proc_message01.txt") # read current msg from interprocess comms file01
print ("interprocess message01: " + str(procmsg))
sensor_read = readramdrive("/mnt/interproc01/proc_message02.txt") # read current msg from interprocess comms file02
print ("interprocess message02: " + str(sensor_read))


##############################################################
# code to manage the Flask web interface goes below this line
##############################################################

###############################################################################
# this route goes to the selection mode routine when the URL root is selected
###############################################################################
@quadrabot_app01.route("/") # run the code below this function when the URL root is accessed
def start():
    # update time now
    timenow = time.strftime('%H:%M %Z')

    select_mode = "selection routine"
    template_data = {
        'time_now' : timenow,         # this sets the current time template parameter
        'title' : select_mode,        # this sets the browser title template parameter
    }
    writeramdrive("select_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
    return render_template('select_mode.html', **template_data)


#########################################################################################################
# this route initiates a system reboot & returns to the slider switch control mode by suspending web use 
#########################################################################################################
@quadrabot_app01.route("/reboot")  # run the code below this function when URL /reboot option is accessed
def reboot():
    # update time now
    timenow = time.strftime('%H:%M %Z')
    reboot_mode = "rebooting system"
    writecommandlog('reboot')
    template_data = {
        'time_now' : timenow,         # this sets the current time template parameter
        'title' : reboot_mode,        # this sets the browser title template parameter
    }
    print(" going to stop web mode and initiate a system reboot")
    writeramdrive("reboot","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
    return render_template('system_reboot.html', **template_data)

################################################################################################
# this route returns to the slider switch control mode by suspending web use 
################################################################################################
@quadrabot_app01.route("/switch_control_mode")  # run the code below this function when URL /switch_control_mode is accessed from select_mode.html
def switch_control():
    # update time now
    timenow = time.strftime('%H:%M %Z')
    switch_mode = "suspending web control"
    writecommandlog('suspend_web')
    template_data = {
        'time_now' : timenow,         # this sets the current time template parameter
        'title' : switch_mode,        # this sets the browser title template parameter
    }
    print(" going to stop web mode")
    writeramdrive("switch_control","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
    return render_template('web_suspended.html', **template_data)


##################################################################################
# this route defines the actions selected when the robot is in the selection mode
##################################################################################
@quadrabot_app01.route("/<robot_mode>")  # run the code below this function when URL /<robot_mode> is accessed from select_mode.html where <robot_mode> is a variable
def mode_selection(robot_mode=None):
    # update time now
    timenow = time.strftime('%H:%M %Z')
    none_selected = "no mode selected"

    if robot_mode == 'demo_mode':
        # set the last command to 'empty' as a default start position
        writecommandlog('demo_mode')  

        # set the virtual interrupt text to 'demo_mode'  
        writeinterruptlog('demo_mode')
        print ("select mode: interrupt file text select value: " + str(readinterruptlog()))
        writeramdrive("demo_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        template_data = {
            'time_now' : timenow,         # this sets the current time template parameter
            'title' : "demo mode",        # this sets the browser title template parameter
        }

        return render_template('demo_mode.html', **template_data)

    elif robot_mode == 'autonomous_mode':
        # set the last command to 'empty' as a default start position
        writecommandlog('autonomous_mode')  

        # set the virtual interrupt text to 'autonomousonly'  
        writeinterruptlog('autonomousonly')
        print ("interrupt file text select autonomous value: " + str(readinterruptlog()))
        writeramdrive("autonomous_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        template_data = {
            'time_now' : timenow,         # this sets the current time template parameter
            'title' : "autonomous mode",        # this sets the browser title template parameter
        }

        return render_template('autonomous_mode.html', **template_data)

    elif robot_mode == 'run_about_mode':
        # set the last command to 'empty' as a default start position
        writecommandlog('run_about_mode')  

        # set the virtual interrupt text to 'autonomousonly'  
        writeinterruptlog('autonomousonly')
        print ("interrupt file text select autonomous value: " + str(readinterruptlog()))
        writeramdrive("run_about_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        template_data = {
            'time_now' : timenow,         # this sets the current time template parameter
            'title' : "run about mode",        # this sets the browser title template parameter
        }

        return render_template('run_about.html', **template_data)

    elif robot_mode == 'maintenance_mode':
        # set the last command to 'empty' as a default start position
        writecommandlog('empty')

        # set the virtual interrupt text to 'maintenance'  
        writeinterruptlog('maintenance')
        print ("select mode: interrupt file text select value: " + str(readinterruptlog()))
        writeramdrive("maintenance_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        template_data = {
            'time_now' : timenow,          # this sets the current time template parameter
            'title' : "maintenance mode",  # this sets the browser title template parameter
        }

        return render_template('maintain_mode.html', **template_data)


    else:
        template_data = {
            'time_now' : timenow,        # this sets the current time template parameter
            'title' : "unknown action",        # this sets the browser title template parameter
        }
        return render_template('select_mode.html', **template_data)


####################################################################################
# this route defines the actions selected when the robot is in autonomous mode
####################################################################################
@quadrabot_app01.route("/autonomous_mode/<auto_option>")  # run the code below this function when URL /autonomous_mode/auto_option> is accessed where <auto_option> is a variable
def robot_auto(auto_option=None):
    # update time now
    timenow = time.strftime('%H:%M %Z')
    none_selected = "no action selected"

    # get the last command from its log file
    lastcommand = str(readcommandlog())
    print ("demo_mode: last command from file: " + str(lastcommand))

    if auto_option == 'stop':
        ###########################################
        print("  ")
        print(" **** autonomous mode stop **** ")
        writeramdrive("auto_stop","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('stop')

        # return to the web interface here without updating the interprocess msg so that the action persists
        template_data = {
            'time_now' : timenow,         # this sets the current time template parameter
            'title' : "auto stop",        # this sets the browser title template parameter
        }
        return render_template('autonomous_mode.html', **template_data)

    elif auto_option == 'go':
        ###########################################
        print("  ")
        print(" **** autonomous mode go  **** ")
        writeramdrive("auto_go","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('go')

        # return to the web interface here without updating the interprocess msg so that the action persists
        template_data = {
            'time_now' : timenow,       # this sets the current time template parameter
            'title' : "auto go",        # this sets the browser title template parameter
        }
        return render_template('autonomous_mode.html', **template_data)

    else:   # add an else option just in case - but should never arrive here
        writeramdrive("auto_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        template_data = {
            'time_now' : timenow,         # this sets the current time template parameter
            'title' : "unknown action",   # this sets the browser title template parameter
        }
        return render_template('autonomous_mode.html', **template_data)

    # should never drop through to here but added another return to web interface just in case
    template_data = {
        'time_now' : timenow,         # this sets the current time template parameter
        'title' : "unknown action",   # this sets the browser title template parameter
        }
    writeramdrive("autonomous_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
    return render_template('autonomous_mode.html', **template_data)


####################################################################################
# this route defines the actions selected when the robot is in run about mode
####################################################################################
@quadrabot_app01.route("/run_about_mode/<run_option>")  # run the code below this function when URL /run_about_mode/run_option> is accessed where <run_option> is a variable
def robot_run(run_option=None):
    # update time now
    timenow = time.strftime('%H:%M %Z')
    none_selected = "no action selected"
    selected = ""
    # get the last command from its log file
    lastcommand = str(readcommandlog())
    print ("run_about_mode: last command from file: " + str(lastcommand))

    if run_option == 'stop':
        ###########################################
        print("  ")
        print(" **** run about mode - stop **** ")
        writeramdrive("run_stop","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('stop')

        selected = "run about stopped"
        # once off action so allow flow to drop through to the end

    elif run_option == 'left':
        ###########################################
        print("  ")
        print(" **** run about mode - left turn  **** ")
        writeramdrive("run_left","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('left')

        selected = "running left"
        # once off action so allow flow to drop through to the end

    elif run_option == 'forward':
        ###########################################
        print("  ")
        print(" **** run about mode - forward  **** ")
        writeramdrive("run_forward","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('forward')

        # return to the web interface here without updating the interprocess msg so that the action persists
        template_data = {
            'time_now' : timenow,        # this sets the current time template parameter
            'title' : "running forwards", # this sets the browser title template parameter
        }
        return render_template('run_about.html', **template_data)

    elif run_option == 'right':
        ###########################################
        print("  ")
        print(" **** run about mode - right turn  **** ")
        writeramdrive("run_right","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command

        selected = "running right"
        # once off action so allow flow to drop through to the end)

    elif run_option == 'spin_left':
        ###########################################
        print("  ")
        print(" **** run about mode - about turn left  **** ")
        writeramdrive("run_spin_left","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('spin_left')

        selected = "spinning left"
        # once off action so allow flow to drop through to the end)

    elif run_option == 'back':
        ###########################################
        print("  ")
        print(" **** run about mode - backward  **** ")
        writeramdrive("run_backward","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('back')

        # return to the web interface here without updating the interprocess msg so that the action persists
        template_data = {
            'time_now' : timenow,      # this sets the current time template parameter
            'title' : "running backwards",      # this sets the browser title template parameter
        }
        return render_template('run_about.html', **template_data)

    elif run_option == 'spin_right':
        ###########################################
        print("  ")
        print(" **** run about mode - about turn right  **** ")
        writeramdrive("run_spin_right","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('spin_right')

        selected = "spinning right"
        # once off action so allow flow to drop through to the end)

    else:   # add an else option just in case - but should never arrive here
        writeramdrive("run_about_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        template_data = {
            'time_now' : timenow,         # this sets the current time template parameter
            'title' : "unknown action",      # this sets the browser title template parameter
        }
        return render_template('run_about.html', **template_data)

    # will drop through to here for non-persistant actions so another return to web interface here
    if selected != "":
        seltitle = selected
    else:
        seltitle = none_selected

    template_data = {
        'time_now' : timenow,    # this sets the current time template parameter
        'title' : seltitle,      # this sets the browser title template parameter
    }

    return render_template('run_about.html', **template_data)


####################################################################################
# this route defines the actions selected when the robot is in demo mode
####################################################################################
@quadrabot_app01.route("/demo_mode/<demo_option>")  # run the code below this function when URL /demo_mode/<demo_option> is accessed where <demo_option> is a variable
def robot_demos(demo_option=None):
    # update time now
    timenow = time.strftime('%H:%M %Z')
    none_selected = "no mode selected"
    selected_title = ""

    # get the last command from its log file
    lastcommand = str(readcommandlog())
    print ("demo_mode: last command from file: " + str(lastcommand))

    if demo_option == 'reset':
        ###########################################
        print("  ")
        print(" **** resetting quadrabot **** ")
        writeramdrive("leg_reset","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "reset quadrabot"
        # set new last command with the latest command
        writecommandlog('leg_reset')

    elif demo_option == 'left':
        ###########################################
        print("  ")
        print(" **** turning left **** ")
        writeramdrive("turn_left","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "turned left"
        # set new last command with the latest command
        writecommandlog('left')

    elif demo_option == 'forward':
        ###########################################
        print("  ")
        print(" **** forward walking **** ")
        writeramdrive("forward4","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "ran forwards"
        # set new last command with the latest command
        writecommandlog('forward')


    elif demo_option == 'right':
        ###########################################
        print("  ")
        print(" **** turning right **** ")
        writeramdrive("turn_right","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "turned right"
        # set new last command with the latest command
        writecommandlog('right')


    elif demo_option == 'anti-clockwise':
        ###########################################
        print("  ")
        print(" **** about turn left **** ")
        writeramdrive("about_turn_left","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "spun left"
        # set new last command with the latest command
        writecommandlog('anti-clockwise')


    elif demo_option == 'back':
        ###########################################
        print("  ")
        print(" **** backward walking **** ")
        writeramdrive("backwards4","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "ran backwards"
        # set new last command with the latest command
        writecommandlog('back')


    elif demo_option == 'clockwise':
        ###########################################
        print("  ")
        print(" **** about turn right **** ")
        writeramdrive("about_turn_right","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "spun right"
        # set new last command with the latest command
        writecommandlog('clockwise')


    elif demo_option == 'wavefll':
        #############################
        print("  ")
        print(" **** wave front left **** ")
        writeramdrive("wave_front_left","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "waved front left"
        # set new last command with the latest command
        writecommandlog('wavefll')


    elif demo_option == 'wavefrl':
        #############################
        print("  ")
        print(" **** wave front right **** ")
        writeramdrive("wave_front_right","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "waved front right"
        # set new last command with the latest command
        writecommandlog('wavefrl')


    elif demo_option == 'wavebll':
        #############################
        print("  ")
        print(" **** wave back left **** ")
        writeramdrive("wave_back_left","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "waved back left"
        # set new last command with the latest command
        writecommandlog('wavebll')


    elif demo_option == 'wavebrl':
        #############################
        print("  ")
        print(" **** wave back right **** ")
        writeramdrive("wave_back_right","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "waved back right"
        # set new last command with the latest command
        writecommandlog('wavebrl')


    elif demo_option == 'squat':
        #############################
        print("  ")
        print(" **** squat **** ")
        writeramdrive("squat","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "squatted"
        # set new last command with the latest command
        writecommandlog('squat')


    elif demo_option == 'bow':
        #############################
        print("  ")
        print(" **** bow **** ")
        writeramdrive("bow","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        selected_title = "bowed"
        # set new last command with the latest command
        writecommandlog('bow')

    else:
        writeramdrive("demo_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        template_data = {
            'title' : none_selected,
        }
        return render_template('demo_mode.html', **template_data)


    template_data = {
        'time_now' : timenow,       # this sets the current time template parameter
        'title' : selected_title,   # this sets the browser title template parameter
        }
    time.sleep(3) # delay so that whatever 'procmsg action' is in hand can be completed before procmsg is overwritten below
    writeramdrive("demo_mode","/mnt/interproc01/proc_message01.txt") # write new general msg to interprocess comms file
    return render_template('demo_mode.html', **template_data)


####################################################################################
# this route defines the actions selected when the quadrabot is in maintenance mode
####################################################################################
@quadrabot_app01.route("/maintenance_mode/<maintain_option>")  # run the code below this function when URL /maintenance_mode/<maintain_option> is accessed where <maintain_option> is a variable
def robot_maintain(maintain_option=None):
    # update time now
    timenow = time.strftime('%H:%M %Z')
    none_selected = "no mode selected"

    # get the last command from its log file
    lastcommand = str(readcommandlog())
    print ("maintenance_mode: last command from file: " + str(lastcommand))

    if maintain_option == 'check_sensors':
        print("  ")
        print(" **** checking ultrasonic sensor **** ")
        # keep the procmsg as maintenance_mode for now - only set it to read_echo within the detailed reading section
        writeramdrive("maintenance_mode","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('check_sensors')
        # Get the various defaults from their log file
        defaults = readdefaults()

        template_data = {
            'time_now' : timenow,        # this sets the current time template parameter
            'title' : "check sensors",   # this sets the browser title template parameter
            'sensor_type' : "none",
            'abort_read' : "no",
            'too_short' : "no",
            'echo_distance' : "999",
        }

        return render_template('check_sensors.html', **template_data)

    elif maintain_option == 'reset_defaults':
        print("  ")
        print(" **** reset default parameters **** ")
        writeramdrive("reset_defaults","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('reset_defaults')

        # Get the various defaults from their log file as a start set of values for the template
        defaults = readdefaults()

        template_data = {
            'time_now' : timenow,        # this sets the current time template parameter
            'title' : "reset defaults",   # this sets the browser title template parameter
            'pin_trigger' : defaults['pinTrigger'],
            'pin_echo' : defaults['pinEcho'],
            'how_near' : defaults['HowNear'],
            'turn_cycles' : defaults['TurnCycles'],
            'reverse_cycles' : defaults['ReverseCycles'],
            'alt_times' : defaults['Alternate'],
            'pin_onoff' : defaults['onoff'],
            'pin_auto_demo' : defaults['auto_demo'],
            'pin_web' : defaults['web'],
        }

        return render_template('defaults.html', **template_data)

    #elif maintain_option == 'reboot':

        # set new last command with the latest command
        #writecommandlog('reboot')

        #os.system("sudo reboot")


####################################################################################
# this route defines the actions selected when the quadrabot is in sensor check mode
####################################################################################
@quadrabot_app01.route("/check_sensors/<sensor_option>")  # run the code below this function when URL /check_sensors/<sensor_option> is accessed where <sensor_option> is a variable
def robot_sensor(sensor_option=None):
    # update time now
    timenow = time.strftime('%H:%M %Z')
    none_selected = "no sensor option selected"

    if sensor_option == 'check_echo':
        print("  ")
        print(" **** getting ultrasonic sensor reading **** ")
        # set the procmsg initially to "read_echo_reset" to ensure a repeat cycle in the 'action' app 
        writeramdrive("read_echo_reset","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file
        time.sleep(0.2)  # short wait to allow the 'action' app to capture the reset above
        # now set the actual procmsg
        writeramdrive("read_echo","/mnt/interproc01/proc_message01.txt") # write new msg to interprocess comms file

        # set new last command with the latest command
        writecommandlog('check_sensors')

        # wait a short period to allow the action app to get a reading
        time.sleep(1)
        # now read the 'latest' distance/tooshort readings from the 2nd/3rd/4th interprocess comm files
        sensor_reading = readramdrive("/mnt/interproc01/proc_message02.txt")
        tooshort = readramdrive("/mnt/interproc01/proc_message03.txt")        
        abort = readramdrive("/mnt/interproc01/proc_message04.txt") 

        template_data = {
            'time_now' : timenow,        # this sets the current time template parameter
            'title' : "object detection",     # this sets the browser title template parameter
            'sensor_type' : "ultrasonic",
            'abort_read' : abort,
            'too_short' : tooshort,
            'echo_distance' : sensor_reading,
        }

        return render_template('check_sensors.html', **template_data)


#######################################################################################
# this route defines the actions selected when the quadrabot is in reset defaults mode
#######################################################################################
@quadrabot_app01.route("/reset_defaults/<default_input>")  # run the code below this function when URL /reset_defaults/<default_input> is accessed where <default_input> is a variable
def robot_reset_defaults(default_input=None):
    # update time now
    timenow = time.strftime('%H:%M %Z')
    none_selected = "no defaults input"
    print("  ")
    print(" **** updating default parameters **** ")
    # write new msg to interprocess comms file - but no action needed in the 'action' app
    writeramdrive(default_input,"/mnt/interproc01/proc_message01.txt")

    # set new last command with the latest command
    writecommandlog(default_input)

    # read the current set of defaults from its log file
    defaults = readdefaults()

    if default_input == 'update_pintrigger':
        print ("request method: " + str(request.method))
        print ("new pinTrigger value: " + str(request.args.get('pintrig')))
        defaults['pinTrigger'] = str(request.args.get('pintrig'))

    elif default_input == 'update_pinecho':
        print ("request method: " + str(request.method))
        print( "new pinEcho value: " + str(request.args.get('pinecho')))
        defaults['pinEcho'] = str(request.args.get('pinecho'))

    elif default_input == 'update_pinonoff':
        print ("request method: " + str(request.method))
        print ("new pin onoff value: " + str(request.args.get('pinonoff')))
        defaults['onoff'] = str(request.args.get('pinonoff'))

    elif default_input == 'update_pinweb':
        print ("request method: " + str(request.method))
        print ("new pin web value: " + str(request.args.get('pinweb')))
        defaults['web'] = str(request.args.get('pinweb'))

    elif default_input == 'update_pinautodemo':
        print ("request method: " + str(request.method))
        print ("new pin auto_demo value: " + str(request.args.get('pinautodemo')))
        defaults['auto_demo'] = str(request.args.get('pinautodemo'))

    elif default_input == 'update_hownear':
        print ("request method: " + str(request.method))
        print ("new HowNear value: " + str(request.args.get('hownear')))
        defaults['HowNear'] = str(request.args.get('hownear'))

    elif default_input == 'update_revcycles':
        print ("request method: " + str(request.method))
        print ("new ReverseCycles value: " + str(request.args.get('revcycles')))
        defaults['ReverseCycles'] = str(request.args.get('revcycles'))

    elif default_input == 'update_turncycles':
        print ("request method: " + str(request.method))
        print ("new TurnCycles value: " + str(request.args.get('turncycles')))
        defaults['TurnCycles'] = str(request.args.get('turncycles'))

    elif default_input == 'update_alternate':
        print ("request method: " + str(request.method))
        print ("new Alternate value: " + str(request.args.get('alternate')))
        defaults['Alternate'] = str(request.args.get('alternate'))

    else:
        print ("default input not set")
        template_data = {
            'time_now' : timenow,        # this sets the current time template parameter
            'title' : none_selected,     # this sets the browser title template parameter
        }

    # write out the revised set of defaults to the log file if an update has been done
    if "update" in default_input:
        writedefaults(defaults)

    template_data = {
        'time_now' : timenow,        # this sets the current time template parameter
        'title' : default_input,     # this sets the browser title template parameter
        'pin_trigger' : defaults['pinTrigger'],
        'pin_echo' : defaults['pinEcho'],
        'how_near' : defaults['HowNear'],
        'turn_cycles' : defaults['TurnCycles'],
        'reverse_cycles' : defaults['ReverseCycles'],
        'alt_times' : defaults['Alternate'],
        'pin_onoff' : defaults['onoff'],
        'pin_auto_demo' : defaults['auto_demo'],
        'pin_web' : defaults['web'],
    }

    return render_template('defaults.html', **template_data)

##################################################################################
# the code below is the last code in the web part of the system
# using the Flask 'production' server i.e. port 80 
#  so sudo needs to be used to run the code
##################################################################################
print ("starting web server")
if __name__ == "__main__":
    quadrabot_app01.run(host='0.0.0.0', port=80, debug=False, threaded=True)   
    # 0.0.0.0 means any device on the network can access the web app



