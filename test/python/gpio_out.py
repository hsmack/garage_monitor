#!/usr/bin/python
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|-|S|p|y|.|c|o|.|u|k|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# sonictest.py
# Measure distance using an ultrasonic module
#
# Author : Matt Hawkins
# Date   : 09/01/2013

# Import required Python libraries
import time
import RPi.GPIO as GPIO

# Use BCM GPIO references
# instead of physical pin numbers
#GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BCM)
# Define GPIO to use on Pi
GPIO_TRIGGER = 11
GPIO_ECHO    = 8

GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)

i=0
while True:
  i += 1
  # Send 10us pulse to trigger
  GPIO.output(GPIO_TRIGGER, True)
  print("{}: high ...".format(i));
  time.sleep(2)
  GPIO.output(GPIO_TRIGGER, False)
  print("{}: low ...".format(i));
  time.sleep(2)

