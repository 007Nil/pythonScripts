# Simple Program to set external as main monitor for my netbook setup

from subprocess import check_output
import os
import time


command = "xrandr"

requried_vga_string = "VGA1 connected"
while True:
    output = check_output([command, "-q"])

#print(output)

    # Check if VGA cable is connected or not
    # if connected then make VGA as primary and turn off laptop monitor
    if requried_vga_string in output:
        try:
            os.system("xrandr --output VGA1 --mode 1920x1080")
            os.system("xrandr --output LVDS1 --off")
        except Exception as e:
            print("Error occour: {}".format(e))
    elif requried_vga_string not in output:
        try:
            #print("HIT")
            os.system("xrandr --output LVDS1 --primary --mode 1024x600")
            os.system("xrandr --output VGA1 --off")
        except Exception as e:
            print("Error occour: {}".format(e))

    time.sleep(2)


