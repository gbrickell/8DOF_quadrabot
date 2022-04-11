#!/usr/bin/env python3
"""
based upon:
robot_control_inputs.py
www.bluetin.io
 and further developed by Enmore Green Ltd
command:  python3 /home/pi/quadrabot/robot_control_all_inputs.py
"""

from inputs import get_gamepad
from inputs import devices
for device in devices:
    print(device)


# Dictionary of the 19 game controller buttons/joysticks on the PiHut witeless controller
# which is recognised by the 'inputs' module as a "MS X-Box 360 pad"
controller_input = {'BTN_THUMBL': 0, 'ABS_X': 0, 'ABS_Y': 0, 'BTN_THUMBR': 0,  'ABS_RX': 0, 'ABS_RY': 0, 
                    'BTN_START': 0, 'BTN_SELECT': 0, 'BTN_MODE': 0,  'ABS_HAT0X': 0, 'ABS_HAT0Y': 0, 
                    'BTN_WEST': 0, 'BTN_NORTH': 0, 'BTN_SOUTH': 0, 'BTN_EAST': 0,
                    'BTN_TL': 0, 'BTN_TR': 0, 'ABS_Z': 0, 'ABS_RZ': 0 }

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
        return "bRLwave"

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


def main():
    """ Main entry point of the app """
    while 1:
        # Get next controller Input
        control_code = gamepad_update()
        
        # Gamepad button/joystick filter
        if control_code == 'ABS_X' or control_code == 'ABS_Y':
            # Drive and steering left joystick
            drive_controlxy_left()
        elif control_code == 'ABS_RX' or control_code == 'ABS_RY':
            # Drive and steering right joystick
            drive_controlxy_right()
        elif control_code == 'ABS_Z':
            # rear/left btn held down
            abs_z()
        elif control_code == 'ABS_RZ':
            # rear/right btn held down
            abs_rz()
        elif control_code == 'ABS_HAT0X':
            # joypad pressed
            print (" ... turn " + str(abs_hat0x()) )
        elif control_code == 'ABS_HAT0Y':
            # joypad pressed
            abs_hat0y()
        elif control_code == 'BTN_SOUTH':
            # btn pressed
            btn_south()
        elif control_code == 'BTN_WEST':
            # btn pressed
            btn_west()
        elif control_code == 'BTN_NORTH':
            # btn pressed
            btn_north()
        elif control_code == 'BTN_EAST':
            # btn pressed
            btn_east()
        elif control_code == 'BTN_START':
            # btn pressed
            btn_start()
        elif control_code == 'BTN_SELECT':
            # btn pressed
            btn_select()
        elif control_code == 'BTN_MODE':
            # btn pressed
            btn_mode()
        elif control_code == 'BTN_THUMBR':
            # btn pressed
            btn_thumbr()
        elif control_code == 'BTN_THUMBL':
            # btn pressed
            btn_thumbl()
        elif control_code == 'BTN_TL':
            # btn pressed
            btn_tl()
        elif control_code == 'BTN_TR':
            # btn pressed
            btn_tr()
        #else:
        #    print (str(control_code) + " control not recognised")

#-----------------------------------------------------------

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()