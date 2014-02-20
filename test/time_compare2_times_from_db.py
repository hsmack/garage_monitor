#!python
#
# check if startup is around same time, then don't send email
#
# if was closed, and now closed, no email
# if any other combination, then send email
#

import os, sys
import subprocess
import thread
import time
# from datetime import datetime
import signal
import sqlite3
import socket
import inspect
import yaml

db_conn = sqlite3.connect('gm.db')
c = db_conn.cursor()

#
# helper function to get the next insert id from DB
#
def db_next_id(db_cursor, table):
  max_id = db_cursor.execute('SELECT max(id) FROM {}'.format(table)).fetchone()[0]
  if max_id <= 0:
    max_id = 0  
  return max_id+1

#
# convert database time format into a float of seconds.
#
def dbtime2secs(db_time):
  parsed_time = time.strptime(db_time , '%Y-%m-%d %H:%M:%S')
  print repr(parsed_time)
  return time.mktime(parsed_time)

#
# convert database time into any strftime format
#
def dbtime2string(db_time, strftime_format):
  parsed_time = time.strptime(db_time , '%Y-%m-%d %H:%M:%S')
  pretty_time = time.strftime(strftime_format, parsed_time)
  return pretty_time


timenow = time.localtime()
human_readable_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", timenow)

print "--door--"
# read everything
for row in c.execute('SELECT * FROM door ORDER BY timestamp'):
  print(row)

print "--startup--"
# read everything
for row in c.execute('SELECT * FROM startup ORDER BY timestamp'):
  print(row)

print "-- will comare these 2 ---"
c.execute('SELECT * FROM door ORDER BY timestamp DESC LIMIT 1')
last_door = c.fetchone()
print last_door

c.execute('SELECT * FROM startup ORDER BY timestamp DESC LIMIT 1')
last_startup = c.fetchone()
print last_startup


#
# if within 90 seconds, do the compare and don't send email
#
s = time.strptime(last_startup[1] , '%Y-%m-%d %H:%M:%S')
print s
startup_time = time.mktime(s)
print startup_time

d = time.strptime(last_door[1] , '%Y-%m-%d %H:%M:%S')
print d
door_time = time.mktime(d)
print door_time

if ((door_time - startup_time) < 90) or ((door_time - startup_time) > -90):
  print "within 90 secs"
else:
  print "out of range"


#
# test database conversions
#
secs = dbtime2secs(last_startup[1]) 
print repr(secs)
print "asctime(localtime(secs)): %s" % time.asctime(time.localtime(secs))

pretty_time = dbtime2string(last_startup[1], "%a, %d %b %Y %H:%M:%S +0000")
print pretty_time

# human_readable_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", struct)