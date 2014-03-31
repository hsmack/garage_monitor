#!/usr/bin/env python
#
# server to light up an led from a remote socket command
#

import os, sys, warnings, signal
import time
import inspect
import socket
import yaml
import json
import urllib2
import RPi.GPIO as GPIO
from fysom import Fysom
from multiprocessing import Process, Queue

# get absolute path, easier for daemons or process monitors (god) to run
current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
config_file_path = "%s/../config/app_config.yml" % current_path

# load universal config file
stream = open(config_file_path, 'r')
APP_CONFIG = yaml.load(stream)

# server settings
# HOST = hostname or IP address of led_server.  example: tv.local
# PORT = remote port.  4001 is acceptable, must match garage_monitor_server
HOST = APP_CONFIG['garage_monitor_server']['host']
PORT = APP_CONFIG['garage_monitor_server']['port']

# database schema specific index
DB_DOOR_TIME_INDEX = 1
DB_DOOR_STATE_INDEX = 3

# Use BCM GPIO references
# instead of physical pin numbers
GPIO.setmode(GPIO.BCM)
# clean restart of GPIOs.  This fixes any script restart problems
GPIO.cleanup()

# init the GPIOs
GPIO_GREEN_LED = 18
GPIO_RED_LED = 17

# setup leds
GPIO.setup(GPIO_GREEN_LED, GPIO.OUT)
GPIO.setup(GPIO_RED_LED,   GPIO.OUT)

# Allow module to settle
time.sleep(0.5)

# start socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

# add as global variables, so I can exit_gracefully()
conn = False

#
# multiprocessing queue to manage incoming data
#
q = Queue()


def run_socket_server(q):
  global s, conn  # these are global, so the exit_gracefully() function can close them on exit
  global fsm

  while True:
    # DEBUG ONLY
    # time.sleep(1)
    # print "test..."
    # print repr(fsm.current)

    (conn, addr) = s.accept()
    if conn and addr:
      print 'socket: Connected by', addr
      data = conn.recv(1024)
      q.put(data)
      if len(data) > 0:
        print 'socket: data is: ' + data
      conn.close()
  s.close()
  pass


# initialize 
socket_server = Process(target=run_socket_server, args=(q,))
socket_server.start()

#
# simple output LED
#
class LED:
  """simple led output managment"""
  def __init__(self, gpio, invert=0):
    self.gpio = gpio
    self.blink = False
    self.blink_pid = -1
    GPIO.output(self.gpio, False)

  def on(self):
    GPIO.output(self.gpio, True)

  def off(self):
    GPIO.output(self.gpio, False)



# initialize my hardware
green_led = LED(GPIO_GREEN_LED)
red_led = LED(GPIO_RED_LED)


def do_nothing():
  pass

def led_test(led):
  led.off()
  time.sleep(0.3)
  led.on()
  time.sleep(0.3)
  led.off()

def test_led_for_reset():
  global green_led, red_led
  led_test(green_led)
  led_test(red_led)

def blink_red_led_then_solid():
  global green_led, red_led
  green_led.off()
  # 100 times is 1 minute
  # 50 times is 30 seconds
  for i in xrange(100):
    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)

def blink_green_led_then_solid():
  global green_led, red_led
  red_led.off()
  # 100 times is 1 minute
  # 50 times is 30 seconds
  for i in xrange(100):
    green_led.off()
    time.sleep(0.3)
    green_led.on()
    time.sleep(0.3)


def blink_red_led_with_sos():
  global red_led
  red_led.off()
  # 100 times is 1 minute
  # 50 times is 30 seconds
  for i in xrange(100):
    #
    # 3 shorts
    #
    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)

    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)

    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)

    #
    # 3 longs
    #
    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(1)

    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(1)

    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(1)

    #
    # 3 shorts
    #
    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)

    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)

    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)
    
    red_led.off()
    time.sleep(2)
    

# initialize LED controller hardware
led_controller = Process(target=do_nothing, args=())
led_controller.start()

#
# state machine setup
#
def onreset(e):
  global led_controller
  global green_led, red_led
  print 'reset'
  try:
    #
    # always kill existing process and run new process
    #
    if led_controller.is_alive():
      led_controller.terminate()
      time.sleep(0.01)
    led_controller = Process(target=blink_red_led_with_sos, args=())
    led_controller.start()
  except:
    time.sleep(0.01)

def onopen(e):
  global led_controller
  global green_led, red_led
  print 'open'
  try:
    #
    # always kill existing process and run new process
    #
    if led_controller.is_alive():
      led_controller.terminate()
      time.sleep(0.01)
    led_controller = Process(target=blink_red_led_then_solid, args=())
    led_controller.start()
  except:
    time.sleep(0.01)



def onclosed(e):
  global led_controller
  global green_led, red_led
  print 'closed'
  try:
    #
    # always kill existing process and run new process
    #
    if led_controller.is_alive():
      led_controller.terminate()
      time.sleep(0.01)
    led_controller = Process(target=blink_green_led_then_solid, args=())
    led_controller.start()
  except:
      time.sleep(0.01)


fsm = Fysom({'initial': {'state':'reset', 'event':'init'},
             'events': [
               {'name': 'open_now', 'src': ['reset', 'open', 'closed'], 'dst': 'open'},
               {'name': 'close_now', 'src': ['reset', 'open', 'closed'], 'dst': 'closed'},
               {'name': 'was_closed', 'src': 'reset', 'dst': 'closed'},
               {'name': 'was_open', 'src': 'reset', 'dst': 'open'},
               {'name': 'lost_connection', 'src': ['reset', 'open', 'closed'], 'dst': 'reset'},
               ],
             'callbacks': {
               'onreset': onreset,
               'onopen': onopen,
               'onclosed': onclosed, }})


def main():
  global fsm

  now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
  print "Starting TV garage monitor led server ... {}".format(now)

  # todo: hook up with a poll to garage.local webserver
  # currently assume that the garage door is closed at the start of this
  # script (most common case)
  fsm.was_closed()

  i = 0
  while True:
    
    if (q.qsize() > 0):
      data = q.get()
      d = data.split(',')
      door_state = d[0]
      db_time = d[1]
      print "%d: door_state: %s, time: %s" % (i, door_state, db_time)
      print 'fsm current state: ', fsm.current.upper()

      prev_state = fsm.current.upper()
      if(door_state.upper() == 'CLOSED' and 'CLOSED' != fsm.current.upper()):
        fsm.close_now()
        time.sleep(10)
        print "sleeping 10"
        print "fsm: %s -> CLOSED" % prev_state

      if(door_state.upper() == 'OPEN' and 'OPEN' != fsm.current.upper()):
        fsm.open_now()
        time.sleep(10)
        print "sleeping 10"
        print "poll:  %s -> OPEN" % prev_state

    # print "waiting ..." # debug
    time.sleep(10)
    i += 1


#
# cleanup and exit
#
def exit_gracefully(signum, frame):
  global s
  global conn
  print "You pressed Ctrl-C "
  
  if led_controller.is_alive():
    led_controller.terminate()

  if socket_server.is_alive():
    socket_server.terminate()

  GPIO.cleanup()
  try:
    conn.close()
  except:
    sys.stderr.write("couldn't close socket connection: %s \n" % sys.exc_info()[1])

  try:
    s.close()
  except:
    sys.stderr.write("couldn't close socket server: %s \n" % sys.exc_info()[1])

  sys.exit(0)



if __name__ == "__main__":
  for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, exit_gracefully)
  main()



