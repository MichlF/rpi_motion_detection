"""
This code uses the RPi.GPIO library to interact with the GPIO pins on a Raspberry Pi. 
It monitors the input from a PIR (Passive Infrared) sensor and turns on/off the display accordingly.

Install and upgrade camera
$ sudo apt-get update
$ sudo apt-get install python3-picamera
$ sudo apt-get upgrade
# Install Python modules
pip install deepface

PIR Sensor time range is from ~1-2s to ~3 mins (determined by screw close to the lonely transistor)
"""

import RPi.GPIO as GPIO
import time
from datetime import datetime, timedelta
from subprocess import call

# Setup GPIO module
# Note: the PIR sensor is connected to pin 4 and might need to warm up for a bit first
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)  # Read GPIO in rather than pin numbers (GPIO.BOARD)
pir_pin = 7
GPIO.setup(pir_pin, GPIO.IN)  # Define as input to get status

# Print screen for debugging
verbose = input("Verbose? y: yes / any: no \n")

# Warming up PIR
warmup = GPIO.input(pir_pin)  # Activate sensor (var is overwritten later)
warmup = 20
print(f"Warming up for {warmup}s !")
time.sleep(warmup)
# Screen-on time with smooth loop
still_on = 0
t_window = 20
screen_on = 45 - t_window


# Start the continous loop to monitor movement
try:
    while True:
        pir_input = GPIO.input(pir_pin)
        if pir_input == 1 or still_on == 1:  # Motion detected or still in loop
            # Switch on screen
            call(["/usr/bin/vcgencmd", "display_power", "1"])
            timestamp = datetime.now()
            if verbose == "y":
                print(
                    f"{timestamp.strftime('%Y%m%d_%H-%M-%S')} - Screen on - Waiting {screen_on}s"
                )
            # Prep & cooldown
            still_on = 0
            time.sleep(screen_on)

            # Smooth prolonging loop
            while datetime.now() - timestamp < timedelta(seconds=screen_on + t_window):
                print(datetime.now() - timestamp)
                if GPIO.input(pir_pin) == 1:
                    if verbose == "y":
                        print("activity in on window - breaking & restarting loop")
                    still_on = 1
                    break
                time.sleep(0.5)
            else:
                if verbose == "y":
                    print("No activity in Smooth loop - restarting main loop")

            if verbose == "y":
                print("Full smooth loop time:", datetime.now() - timestamp)

        elif pir_input == 0:  # No motion detected
            # Switch off screen
            call(["/usr/bin/vcgencmd", "display_power", "0"])
            timestamp = datetime.now()
            if verbose == "y":
                print(f"{timestamp.strftime('%Y%m%d_%H-%M-%S')} - Screen off")
            # Cooldown
            time.sleep(0.5)

except Exception as e:
    print(f"Encountered error {e}")
    GPIO.cleanup()
