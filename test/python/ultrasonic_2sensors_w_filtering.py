#!/usr/bin/env python
# super house monitor, (garage and home notifications)
#
# Perform 2 functions:
# - Measure distance using an ultrasonic module
# - light LEDs (green and red)
#
# hsmack 12/4/2013

from array import *
import os, sys, warnings, signal
import time
import RPi.GPIO as GPIO
import numpy as NP

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
# clean restart of GPIOs.  This fixes any script restart problems
GPIO.cleanup()

# Define GPIO to use on Pi
# GPIO_TRIGGER1 = 11
# GPIO_ECHO1   = 8

GPIO_TRIGGER2 = 22
GPIO_ECHO2    = 23

GPIO_GREEN_LED = 18
GPIO_RED_LED = 17

print "Ultrasonic Measurement"

# Set pins as output and input
GPIO.setup(GPIO_TRIGGER2, GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO2,    GPIO.IN)      # Echo

# setup leds
GPIO.setup(GPIO_GREEN_LED, GPIO.OUT)
GPIO.setup(GPIO_RED_LED,   GPIO.OUT)

# Set trigger to False (Low)
GPIO.output(GPIO_TRIGGER2, False)

# Allow module to settle
time.sleep(0.5)

TIMEOUT = 1 #seconds

class LED:
  """simple led output managment"""
  def __init__(self, gpio, invert=0):
    self.gpio = gpio

    # set initial state = 0
    GPIO.output(self.gpio, False)
    # if invert == 0 or invert == False:
    #   high = on
    #   low = off
    # else:
    #   high = off
    #   low = on

  def on(self):
    GPIO.output(self.gpio, True)

  def off(self):
    GPIO.output(self.gpio, False)


def meas(trigger_pin, echo_pin):
  
  # make sure it's low
  GPIO.output(trigger_pin, False)
  time.sleep(0.000002)
  
  # Send 10us pulse to trigger
  GPIO.output(trigger_pin, True)
  time.sleep(0.00001)
  GPIO.output(trigger_pin, False)
  start = time.time()

  timeout_start = time.time()
  timeout_exceeded_flag = False

  while GPIO.input(echo_pin)==0:
    start = time.time()
    if timeout_exceeded_flag or ((time.time() - timeout_start) > TIMEOUT):
      timeout_exceeded_flag = True
      break

  while GPIO.input(echo_pin)==1:
    stop = time.time()
    if timeout_exceeded_flag or ((time.time() - timeout_start) > TIMEOUT):
      timeout_exceeded_flag = True
      break

  if timeout_exceeded_flag:
    print "TIMEOUT... no measurement"
    return -1

  # Calculate pulse length
  elapsed = stop-start

  # Distance pulse travelled in that time is time
  # multiplied by the speed of sound (cm/s) and /2 the distance /2.54 as inches
  distance = elapsed * 34029 / 2 / 2.54

  # print "Distance : %.1f cm" % distance
  return distance

def count_uniques(arr):
  seen = {}
  for x in arr:
    if x in seen:
      seen[x]+=1
    else:
      seen[x] = 1
  return seen


def high_value_from_dict(in_dict):
  high_value = False
  high_index = False
  for k,v in in_dict.iteritems():
  # print k, v
    if v >= high_value:
      high_value = v
      high_index = k
  return [high_index, high_value]


def measure_many(trigger_pin, echo_pin):
  DEBUG_VERBOSE = False

  global all_measurements
  raw_readings = []

  # take 10 measurements
  for i in xrange(100):
    dist = meas(trigger_pin, echo_pin)
    if (dist < 150): # 300cm is 118in max range of the sensor
      raw_readings.append(dist)

  # DEBUG: dump stats as debug
  # print repr(raw_readings)
  # print "min: {:.1f}".format(min(raw_readings))
  # print "max: {:.1f}".format(max(raw_readings))
  # print "avg: {:.1f}".format(avg)

  #
  # process all of the readings into bins
  # the bins with a high count will be the readings are the peak of a histogram.
  #
  bins = NP.array([0., 5., 10., 15., 20., 25., 30., 35., 40., 45., 50., 55., 60., 65., 70., 75., 80., 85., 90., 95., 100., 105., 110., 115., 120., 130., 140., 145., 150.])
  digitized_readings = NP.digitize(raw_readings, bins)
  #DEBUG
  # print repr(digitized_readings)
  
  #
  # create histogram by counting the binned readings
  #
  seen = {}
  seen = count_uniques(digitized_readings)
  #DEBUG
  # print repr(seen)

  #
  # get the bin with the most readings (peak histogram)
  #
  high = []
  high = high_value_from_dict(seen)
  # print repr(high)

  #
  # create an array with only the binned readings (for easier debug and processing)
  #
  filtered_readings = []
  for i, val in enumerate(digitized_readings):
    if val == high[0]:
      filtered_readings.append(raw_readings[i])
  #DEBUG
  # print repr(filtered_readings)

  avg = (sum(filtered_readings)/len(filtered_readings))
  print "min: {:.1f}".format(min(filtered_readings))
  print "max: {:.1f}".format(max(filtered_readings))
  print "avg(n={}): {:.1f}".format(len(filtered_readings), avg)

  # check all computations
  if high[1] != len(filtered_readings):
    warnings.warn("measurement processing error, filtered readings are not processed correctly and result maybe inaccurate", MeasurementProcessingError)

  # save measurements for analytics
  all_measurements.append(raw_readings)
  return avg

def led_test(led):
  led.off()
  time.sleep(0.3)
  led.on()
  time.sleep(0.3)
  led.off()


def exit_gracefully(signum, frame):
  print "You pressed Ctrl-C "
  GPIO.cleanup()
  sys.exit(0)


################################################
# GLOBALS
################################################

#
# saves all measurements for logging to a .csv file
#
all_measurements = []


################################################
# main()
################################################
def main():
  green_led = LED(GPIO_GREEN_LED)
  red_led = LED(GPIO_RED_LED)

  # led test
  led_test(green_led)
  led_test(red_led)
  
  for i in xrange(30):
    green_led.on()
    print "meas sensor red {}".format(i)
    distance = measure_many(GPIO_TRIGGER2, GPIO_ECHO2)
    print "Distance : %.1f inches" % distance
    green_led.off()
    time.sleep(1)

  #
  # save all measurements to a file
  #
  if False:
    f = open('meas.csv', 'w')
    for list in all_measurements:
      f.write(','.join([str(x) for x in list]) + "\n")
    f.close
  
  # Reset GPIO settings
  GPIO.cleanup()
  sys.exit(0)



if __name__ == "__main__":
  signal.signal(signal.SIGINT, exit_gracefully)
  main()


