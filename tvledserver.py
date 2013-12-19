#!/usr/bin/env python
#
# server to light up an led from a remote socket command
#

import os, sys, warnings, signal
import time
import socket
import RPi.GPIO as GPIO
from fysom import Fysom
from multiprocessing import Process


HOST = 'tv.local'                 # Symbolic name meaning all available interfaces
PORT = 4001              # Arbitrary non-privileged port

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

# add some global variables, so I can clean up things easier later
conn = False


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

def led_test_for_reset():
  global green_led, red_led
  led_test(green_led)
  led_test(red_led)

def blink_red_led():
  global green_led, red_led
  # 100 times is 1 minute
  # 50 times is 30 seconds
  for i in xrange(15):
    red_led.off()
    time.sleep(0.3)
    red_led.on()
    time.sleep(0.3)


# initialize LED controller hardware
led_controller = Process(target=do_nothing, args=())


#
# state machine setup
#
def onreset(e):
  global green_led, red_led
  global led_controller
  print 'reset'
  led_test_for_reset()

def onopen(e):
  global green_led, red_led
  print 'open'
  green_led.off()
  red_led.on()

def onclosed(e):
  global green_led, red_led
  global led_controller
  print 'closed'
  green_led.on() 
  red_led.off()


def onjust_opened(e):
  global green_led, red_led
  print 'just_opened'
  green_led.off()
  blink_red_led()


fsm = Fysom({'initial': {'state':'reset', 'event':'init'},
             'events': [
               {'name': 'open_now', 'src': ['just_opened', 'closed'], 'dst': 'just_opened'},
               {'name': 'opened_forever', 'src': 'just_opened', 'dst': 'open'},
               {'name': 'close_now', 'src': ['open', 'just_opened', 'closed'], 'dst': 'closed'},
               {'name': 'was_closed', 'src': 'reset', 'dst': 'closed'},
               {'name': 'was_open', 'src': 'reset', 'dst': 'just_opened'}],
             'callbacks': {
               'onreset': onreset,
               'onopen': onopen,
               'onclosed': onclosed,
               'onjust_opened': onjust_opened, }})

# fsm.init()


def main():
  global s, conn
  global fsm
  global green_led, red_led
  global led_controller

  timenow = time.localtime()
  now = time.strftime("%a, %d %b %Y %H:%M:%S", timenow)
  print "Starting TV LED server ... {}".format(now)

  # todo: hook up with a poll to garage.local webserver
  # currently assume that the garage door is closed at the start of this
  # script (most common case)
  fsm.was_closed()

  while True:
    # time.sleep(1)
    # print repr(fsm.current)
    (conn, addr) = s.accept()
    if conn and addr:
      print 'Connected by', addr
      data = conn.recv(1024)
      if len(data) > 0:

        print 'data is: ' + data
        d = data.split(',')
        if d[2] == 'OPEN':
          fsm.open_now()
          fsm.opened_forever()
        else:
          # print "LED RED is off"
          fsm.close_now()

      conn.close()

  s.close()

  pass



#
# cleanup and exit
#
def exit_gracefully(signum, frame):
  global s
  global conn
  print "You pressed Ctrl-C "
  GPIO.cleanup()
  conn.close()
  s.close()
  sys.exit(0)



if __name__ == "__main__":
  signal.signal(signal.SIGINT, exit_gracefully)
  main()

