#!/usr/bin/python
# quadrabot version of simple_text.py
#
# based upon the Adafruit examples when using the Adafruit SSD1306 library

# command:  python3 /home/pi/quadrabot/OLED_simple_text.py

import time

###################################
# 128x64 display with hardware I2C:
###################################

import Adafruit_SSD1306  # this is the set of software functions for the display hardware

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

# Write four lines of text onto the image: need to adjust the 'spacing' for the font size
# if font size is 16 the maximum #lines is 4 for the 128 x 64 display
draw.text((x, top),    "1st line of text",  font=font, fill=255)
draw.text((x, top+16), "waiting 15 secs",  font=font, fill=255)
draw.text((x, top+32), "before stopping &",  font=font, fill=255)
draw.text((x, top+48), "clearing screen",  font=font, fill=255)


# Display the image.
disp.image(image)  # set the buffer to the values of the Python Imaging Library (PIL) image
                   # the image should be in 1 bit mode and a size equal to the display size.
disp.display()     # write the display buffer to the physical display


time.sleep(15)

# clear display
disp.clear()
disp.display()

