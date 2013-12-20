#!/usr/bin/python
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|R|a|s|p|b|e|r|r|y|P|i|-|S|p|y|.|c|o|.|u|k|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# ultrasonic_1.py
# Measure distance using an ultrasonic module
#
# Author : Matt Hawkins
# Date   : 09/01/2013

# Import required Python libraries
import time
import RPi.GPIO as GPIO

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)

# Define GPIO to use on Pi
GPIO_TRIGGER1 = 11
GPIO_ECHO1    = 8

GPIO_TRIGGER2 = 22
GPIO_ECHO2    = 23


print "Ultrasonic Measurement, 2 sensors"

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER1,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO1,GPIO.IN)      # Echo


# Set pins as output and input
GPIO.setup(GPIO_TRIGGER2,GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO2,GPIO.IN)      # Echo


# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER1, False)
GPIO.output(GPIO_TRIGGER2, False)

# Allow module to settle
time.sleep(0.5)

TIMEOUT = 2 #seconds

def meas(trigger_pin, echo_pin):
  # Send 10us pulse to trigger
  GPIO.output(trigger_pin, True)
  time.sleep(0.00001)
  GPIO.output(trigger_pin, False)
  start = time.time()

  timeout_start = time.time()
  timeout_exceeded_flag = False

  while GPIO.input(echo_pin)==0:
    start = time.time()
    # if timeout_exceeded_flag || ((time.time() - timeout_start) > TIMEOUT):
    #   timeout_exceeded_flag = True
    #   break

  while GPIO.input(echo_pin)==1:
    stop = time.time()
    # if timeout_exceeded_flag || ((time.time() - timeout_start) > TIMEOUT):
    #   timeout_exceeded_flag = True
    #   break

  if timeout_exceeded_flag:
    print "TIMEOUT... no measurement"
    return -1

  # Calculate pulse length
  elapsed = stop-start

  # Distance pulse travelled in that time is time
  # multiplied by the speed of sound (cm/s) and /2 the distance
  distance = elapsed * 34029 / 2 / 2.54

  print "Distance : %.1f inches" % distance
  return distance


for i in xrange(15):
  print "meas sensor blue {}".format(i)
  meas(GPIO_TRIGGER1, GPIO_ECHO1)
  
  time.sleep(0.2) # rest the sensor a bit?

  print "meas sensor red {}".format(i)
  meas(GPIO_TRIGGER2, GPIO_ECHO2)
  time.sleep(1)


# Reset GPIO settings
GPIO.cleanup()

