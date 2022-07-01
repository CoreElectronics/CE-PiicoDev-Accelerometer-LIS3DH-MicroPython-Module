"""
PiicoDev Accelerometer LIS3DH
Simple example to read acceleration data
"""
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms # cross-platform compatible sleep function

motion = PiicoDev_LIS3DH() # Initialise the accelerometer
# Set the measurement range and sample rate. This can be omitted if you're happy with the default values.
motion.range = 2 # can be 2(default), 4, 8, or 16 (unit: g)
motion.rate = 100 # can be 1, 10, 25, 50, 100, 200 or 400(default) (unit: Hz)

while True:
    x, y, z = motion.acceleration
    x = round(x,2) # round data for a nicer print()
    y = round(y,2)
    z = round(z,2)
    myString = "X: " + str(x) + ", Y: " + str(y) + ", Z: " + str(z) # build a string of data
    print(myString)
    sleep_ms(100)
