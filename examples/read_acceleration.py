"""
PiicoDev Accelerometer LIS3DH
Simple example to read acceleration data
"""

from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function

motion = PiicoDev_LIS3DH() # Initialise the accelerometer
motion.range = 2 # Set the range to +-2g

while True:
    x, y, z = motion.acceleration
    x = round(x,2) # round data for a nicer-looking print()
    y = round(y,2)
    z = round(z,2)
    myString = "X: " + str(x) + ", Y: " + str(y) + ", Z: " + str(z) # build a string of data
    print(myString)

    sleep_ms(100)
