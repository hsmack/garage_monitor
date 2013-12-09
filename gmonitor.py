#!/usr/bin/env python
# gmonitor.py
#
# garage monitor, uses ultrasonic distance detection (2 sensors) to determine
# if the garage door is open or not
#
#
import os
import sys
import warnings
import subprocess
import time
import signal
import sqlite3
import socket
import RPi.GPIO as GPIO
import numpy as NP

# Define GPIO to use on Pi
GPIO_TRIGGER1 = 11
GPIO_ECHO1    = 8

# if using a second sensor
GPIO_TRIGGER2 = 22
GPIO_ECHO2    = 23


# push notifications host
HOST = 'kitty.local'    # The remote host
PORT = 4001              # The same port as used by the server


db_conn = sqlite3.connect('gm.db')
c = db_conn.cursor()


class DistanceDetector:
  """garage monitor, uses ultrasonic distance detection to determine if the garage door is open or not"""
  def __init__(self, trigger_pin, echo_pin, timeout=1):

    self.trigger_pin = trigger_pin
    self.echo_pin = echo_pin
    self.timeout = timeout

    # Use BCM GPIO references
    # instead of physical pin numbers
    GPIO.setmode(GPIO.BCM)

    # Set pins as output and input
    GPIO.setup(self.trigger_pin,GPIO.OUT)  # Trigger
    GPIO.setup(self.echo_pin,GPIO.IN)      # Echo

    # Allow module to settle
    time.sleep(0.5)
    return

  #
  # take a single measurement with the ultrasonic sensor
  # this is not very useful, as the accuracy is dependent on the range.
  # I've found ranges from 1in to 70 inches to be accurate,
  # everything else doesn't seem to work.
  # 
  # my garage is 120in (closed garage door) and 41 inches open garage door (retracted door)
  #
  def measure(self):

    # make sure it's low
    GPIO.output(self.trigger_pin, False)
    time.sleep(0.000002)
    
    # Send 10us pulse to trigger
    GPIO.output(self.trigger_pin, True)
    time.sleep(0.00001)
    GPIO.output(self.trigger_pin, False)
    start = time.time()
    stop = time.time()

    timeout_start = time.time()
    timeout_exceeded_flag = False

    while GPIO.input(self.echo_pin)==0:
      start = time.time()
      if timeout_exceeded_flag or ((time.time() - timeout_start) > self.timeout):
        timeout_exceeded_flag = True
        break

    while GPIO.input(self.echo_pin)==1:
      stop = time.time()
      if timeout_exceeded_flag or ((time.time() - timeout_start) > self.timeout):
        timeout_exceeded_flag = True
        break

    if timeout_exceeded_flag:
      # print "TIMEOUT... no measurement"
      return -1

    # Calculate pulse length
    elapsed = stop - start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s) and /2 the distance /2.54 as inches
    distance = elapsed * 34029 / 2 / 2.54

    # print "Distance : %.1f inches" % distance
    return distance

  #
  # take multiple measurements (default 100)
  # filter it and determine accuracy based on filtered samples
  #
  def measure_many(self):
    DEBUG_VERBOSE = False
    MEAUREMENTS_TO_TAKE = 100
    MAX_DISTANCE_IGNORED = 150 # in inches

    # global all_measurements
    raw_readings = []

    #
    # take a bunch of measurements, and filter it to get accuracy
    #
    for i in xrange(MEAUREMENTS_TO_TAKE):
      dist = self.measure()
      if (dist < MAX_DISTANCE_IGNORED): # 300cm is 118in max range of the sensor
        raw_readings.append(dist)

    # print "--- measurements done"
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
    seen = self.count_uniques(digitized_readings)
    #DEBUG
    # print repr(seen)

    #
    # get the bin with the most readings (peak histogram)
    #
    high = []
    high = self.high_value_from_dict(seen)
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
    # print "min: {:.1f}".format(min(filtered_readings))
    # print "max: {:.1f}".format(max(filtered_readings))
    # print "avg(n={}): {:.1f}".format(len(filtered_readings), avg)

    # check all computations
    if high[1] != len(filtered_readings):
      warnings.warn("measurement processing error, filtered readings are not processed correctly and result maybe inaccurate", MeasurementProcessingError)

    # save measurements for analytics
    # all_measurements.append(raw_readings)
    return avg


  def count_uniques(self, arr):
    seen = {}
    for x in arr:
      if x in seen:
        seen[x]+=1
      else:
        seen[x] = 1
    return seen


  def high_value_from_dict(self, in_dict):
    high_value = False
    high_index = False
    for k,v in in_dict.iteritems():
    # print k, v
      if v >= high_value:
        high_value = v
        high_index = k
    return [high_index, high_value]


#
# interrupt handler:  exit from application and close gpios
#
def exit_gracefully(signum, frame):
  print "You pressed Ctrl-C, exiting program (status=0) ..."
  GPIO.cleanup()
  db_conn.close() # close database connection
  sys.exit(0)


def db_next_id(db_cursor, table):
  max_id = db_cursor.execute('SELECT max(id) FROM {}'.format(table)).fetchone()[0]
  if max_id <= 0:
    max_id = 0  
  return max_id+1

#
# main()
#
def main():
  timenow = time.localtime()
  now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", timenow)
  print "Ultrasonic Measurement start: {}".format(now)

  # clean restart of GPIOs.  This fixes any script restart problems
  GPIO.setmode(GPIO.BCM)
  # Reset GPIO settings
  GPIO.cleanup()

  blue = DistanceDetector(GPIO_TRIGGER1, GPIO_ECHO1)#, 2)
  red = DistanceDetector(GPIO_TRIGGER2, GPIO_ECHO2)#, 2)
  
  DEBUG_VERBOSE = False
  

  #
  # record into the database that the script started up
  #
  hostname = subprocess.check_output(['hostname'])
  hostname = hostname.rstrip(os.linesep)
  now = time.strftime("%Y-%m-%d %H:%M:%S", timenow)
  c.execute( "INSERT into startup values (?, ?, ?);", (db_next_id(c, 'startup'), now, hostname))
  db_conn.commit()


  #
  # This stores the state in memory to track
  # if the  door changes when the script restarts.
  #
  # the database also uses this to track changes
  #
  door_state = False
  flag_changed = True

  #
  # main() loop
  #
  while True:

    
    #
    # take 5 measurements
    # 3 measurements will confirm the distance
    #
    readings = []
    for i in xrange(5):
      time.sleep(0.5)
      #print("{} red measure...".format(i))
      dist = red.measure_many()
      if dist > 0:
        readings.append(dist)
    
    if DEBUG_VERBOSE:
      print repr(readings)

    open_count = 0
    closed_count = 0
    for dist in readings:
      if dist <= 5:
        open_count += 1
      else:
        closed_count += 1

    
    # 
    # this statement is critical
    # the default is to report the door is open
    # therefore any false positives due to sensor errors
    # will force me to check if the door is open.  
    #
    if closed_count > open_count:
      if door_state != 'CLOSED':
        flag_changed = True
      door_state = 'CLOSED'
    else:
      if door_state != 'OPEN':
        flag_changed = True
      door_state = 'OPEN'

    # debug only
    flag_changed = True 

    #
    # report status in every method possible
    #
    if flag_changed == True:
      print "  * state change detected.  write db"
      flag_changed = False
      
      # report measurement to STDOUT
      timenow = time.localtime()
      now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", timenow)
      print "-- Measurement {} --".format(now)
      print "door (open {}x{}): {}".format(open_count, closed_count, door_state)
           
      # write into db
      now = time.strftime("%Y-%m-%d %H:%M:%S", timenow)
      c.execute( "INSERT into door values (?, ?, ?, ?);", (db_next_id(c, 'door'), now, -1, door_state))
      db_conn.commit()


  # Reset GPIO settings
  GPIO.cleanup()
  db_conn.close() # close database connection

if __name__ == "__main__":
  signal.signal(signal.SIGINT, exit_gracefully)
  main()
