"""
Shake-detection example
shake() can be called without any arguments, but has the following parameters should you need them:
    shake_threshold = 15 (default. Should not be less than 10)
    avg_count = 40 (default)
    total_delay = 100 (default)

"""
from PiicoDev_LIS3DH import PiicoDev_LIS3DH
from PiicoDev_Unified import sleep_ms

motion = PiicoDev_LIS3DH() # Initialise the accelerometer

while True:
    if motion.shake(threshold=15):
        print("shaken!")
    else:
        print("")
    # shake() is blocking, so can be used instead of sleep_ms() to delay a loop.
