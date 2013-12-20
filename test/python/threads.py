#!/usr/bin/env python

import thread
import time

test = False
# Define a function for the thread
def print_time( threadName, delay):
  global test
  count = 0
  while count < 15:
    if test = True:
        print 'got signal'
    time.sleep(delay)
    count += 1
    print "%s: %s" % ( threadName, time.ctime(time.time()) )


# Create two threads as follows
try:
   thread.start_new_thread( print_time, ("Thread-1", 2, ) )
   thread.start_new_thread( print_time, ("Thread-2", 4, ) )
except:
   print "Error: unable to start thread"

while 1:
   pass
