#!/usr/bin/env python
# gmonitor.py
#
# garage monitor, uses ultrasonic distance detection (2 sensors) to determine
# if the garage door is open or not
#
#
import os
import sys
import subprocess
import thread
import time
import signal
import sqlite3
import socket
import RPi.GPIO as GPIO
import numpy as NP
import ConfigParser

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

APP_CONFIG = ConfigParser.ConfigParser()
APP_CONFIG.readfp(open('app_config.cfg'))


# Define GPIO to use on Pi
GPIO_TRIGGER1 = 11
GPIO_ECHO1    = 8

# if using a second sensor
GPIO_TRIGGER2 = 22
GPIO_ECHO2    = 23

db_file = APP_CONFIG.get('DATABASE', 'database')
db_conn = sqlite3.connect(db_file)
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
      sys.stderr.write("measurement processing error, filtered readings are not processed correctly and result maybe inaccurate\n")

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

#
# helper function to get the next insert id from DB
#
def db_next_id(db_cursor, table):
  max_id = db_cursor.execute('SELECT max(id) FROM {}'.format(table)).fetchone()[0]
  if max_id <= 0:
    max_id = 0  
  return max_id+1

#
# send an email from a python script
# relies on alll the information from the APP_CONFIG
#
def send_email(door_state, timestamp):
  global APP_CONFIG
  # me == my email address
  # you == recipient's email address
  from_email = "%s <%s>" % (APP_CONFIG.get('SMTP', 'user_from'), APP_CONFIG.get('SMTP', 'login'))
  to = APP_CONFIG.get('EMAIL NOTIFICATIONS', 'notify_email')

  # Create message container - the correct MIME type is multipart/alternative.
  msg = MIMEMultipart('alternative')
  msg['Subject'] = "Garage Door Detector"
  msg['From'] = from_email
  msg['To'] = to


  # put a timestamp
  human_readable_time = time.strftime("%a, %d %b %Y %H:%M:%S", timestamp)
  # print now

  # Create the body of the message (a plain-text and an HTML version).
  text = "Hi!\n\nGarageDoorStatus: %s\t%s\nGoto http://blue.local/ to view manual settings\n\n" % (door_state, human_readable_time)
  html = """\
  <html>
    <head></head>
    <body>
      <p>Hi!<br><br>
         GarageDoorStatus: %s %s<br>
         Goto <a href="http://blue.local/garage">http://blue.local/garage</a> to view history\n\n
      </p>
    </body>
  </html>
  """ % (door_state, human_readable_time)

  # Record the MIME types of both parts - text/plain and text/html.
  part1 = MIMEText(text, 'plain')
  part2 = MIMEText(html, 'html')

  # Attach parts into message container.
  # According to RFC 2046, the last part of a multipart message, in this case
  # the HTML message, is best and preferred.
  msg.attach(part1)
  msg.attach(part2)

  # Send the message via local SMTP server.
  # s = smtplib.SMTP('localhost')

  # Send the message via Google SMTP
  # http://segfault.in/2010/12/sending-gmail-from-python/
  s = smtplib.SMTP(APP_CONFIG.get('SMTP','address'))
  # s.set_debuglevel(1)
  s.esmtp_features["auth"] = "LOGIN PLAIN"
  # s.ehlo()
  s.starttls()
  # s.ehlo()
  s.login(APP_CONFIG.get('SMTP','login'), APP_CONFIG.get('SMTP','password'))


  # sendmail function takes 3 arguments: sender's address, recipient's address
  # and message to send - here it is sent as one string.
  s.sendmail(from_email, to.split(','), msg.as_string())
  print "Email sent %s" % human_readable_time
  # time.sleep(4)
  s.quit()


#
# runs send_email() inside a thread, so it's non blocking
#
def send_email_in_thread(door_state, timestamp):  
  global APP_CONFIG
  if APP_CONFIG.getboolean('ENABLE NOTIFICATIONS','via_email') == True:
    try:
     thread.start_new_thread(send_email, (door_state, timestamp))
    except:
      sys.stderr.write("EmailSendError: %s \n" % sys.exc_info()[1])

#
# turns on LED on remote display
#
def push_state_to_led_server(data):
  global APP_CONFIG
  
  host = APP_CONFIG.get('PUSH NOTIFICATION REMOTE SERVER', 'host')    # The remote host
  port = APP_CONFIG.getint('PUSH NOTIFICATION REMOTE SERVER', 'port')              # The same port as used by the server

  if APP_CONFIG.getboolean('ENABLE NOTIFICATIONS','via_push_notify') == True:
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((host, port))
      print 'push to LED notify server ...', repr(data)
      s.sendall(data)
      s.close()
    except:
      timenow = time.localtime()
      now = time.strftime("%a, %d %b %Y %H:%M:%S", timenow)
      sys.stderr.write("PushNotificationCommunicationError: %s: %s \n" % (now, sys.exc_info()[1]))
  

#
# main()
#
def main():
  global APP_CONFIG
  timenow = time.localtime()
  now = time.strftime("%a, %d %b %Y %H:%M:%S", timenow)
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
    # flag_changed = True 

    #
    # report status in every method possible
    #
    if flag_changed == True:
      print "  * state change detected.  write db"
      flag_changed = False
      
      # report measurement to STDOUT
      timenow = time.localtime()
      human_readable_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", timenow)
      print "-- Measurement {} --".format(human_readable_time)
      print "door (open {}x{}): {}".format(open_count, closed_count, door_state)
           
      # write into db
      db_time = time.strftime("%Y-%m-%d %H:%M:%S", timenow)
      c.execute( "INSERT into door values (?, ?, ?, ?);", (db_next_id(c, 'door'), db_time, -1, door_state))
      db_conn.commit()

      #
      # report state to push notification server
      #
      data = ','.join(["-1", db_time, door_state])
      push_state_to_led_server(data)
      #
      # spin off a thread to send email notifications
      #
      send_email_in_thread(door_state, timenow)

  # Reset GPIO settings
  GPIO.cleanup()
  db_conn.close() # close database connection

if __name__ == "__main__":
  signal.signal(signal.SIGINT, exit_gracefully)
  main()
