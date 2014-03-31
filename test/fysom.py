#!/usr/bin/env python
#
# server to light up an led from a remote socket command
#

import os, sys, signal
import time
from fysom import Fysom


#
# example from internet
#
# def onpanic(e):
#     print 'panic! ' + e.msg
# def oncalm(e):
#     print 'thanks to ' + e.msg + ' done by ' + e.args[0]
# def ongreen(e):
#     print 'green'
# def onyellow(e):
#     print 'yellow'
# def onred(e):
#     print 'red'

# fsm = Fysom({'initial': 'green',
#              'events': [
#                {'name': 'warn', 'src': 'green', 'dst': 'yellow'},
#                {'name': 'panic', 'src': 'yellow', 'dst': 'red'},
#                {'name': 'panic', 'src': 'green', 'dst': 'red'},
#                {'name': 'calm', 'src': 'red', 'dst': 'yellow'},
#                {'name': 'clear', 'src': 'yellow', 'dst': 'green'}],
#              'callbacks': {
#              'onpanic': onpanic,
#              'oncalm': oncalm,
#              'ongreen': ongreen,
#              'onyellow': onyellow,
#              'onred': onred }})

# fsm.panic(msg='killer bees')
# fsm.calm('bob', msg='sedatives in the honey pots')

# ####output is:
#   green
#   red
#   panic! killer bees
#   yellow
#   thanks to sedatives in the honey pots done by bob



# init the GPIOs
GPIO_GREEN_LED = 18
GPIO_RED_LED = 17

#
# simple output LED
#
class LED:
  """simple led output managment"""
  def __init__(self, gpio, name):
    self.gpio = gpio
    self.name = name
    # GPIO.output(self.gpio, False)

  def on(self):
    print "on(%d) %s" % (self.gpio, self.name)
    # GPIO.output(self.gpio, True)

  def off(self):
    print "off(%d) %s" % (self.gpio, self.name)
    # GPIO.output(self.gpio, False)


# initialize my hardware
green_led = LED(GPIO_GREEN_LED, 'green')
red_led = LED(GPIO_RED_LED, 'red')


def led_test(led):
  led.off()
  time.sleep(0.3)
  led.on()
  time.sleep(0.3)
  led.off()

#
# debug
#
led_test(green_led)
led_test(red_led)

#
# state machine setup
#
def onreset(e):
  global green_led, red_led
  print 'reset'
  green_led.off()
  red_led.off()

def onopen(e):
  global green_led, red_led
  print 'open'
  green_led.off()
  red_led.on()

def onclosed(e):
  global green_led, red_led
  print 'closed'
  green_led.on()  # temporary, for debugging only
  red_led.off()

def onjust_opened(e):
  global green_led, red_led
  print 'just_opened'
  green_led.off()
  for i in xrange(15):
    red_led.on()
    time.sleep(0.3)
    red_led.off()
    time.sleep(0.3)


fsm = Fysom({'initial': {'state':'reset', 'event':'init'},
             'events': [
               {'name': 'open_now', 'src': 'closed', 'dst': 'just_opened'},
               {'name': 'opened_forever', 'src': 'just_opened', 'dst': 'open'},
               {'name': 'close_now', 'src': 'open', 'dst': 'closed'},
               {'name': 'was_closed', 'src': 'reset', 'dst': 'closed'},
               {'name': 'was_open', 'src': 'reset', 'dst': 'just_opened'}],
             'callbacks': {
               'onreset': onreset,
               'onopen': onopen,
               'onclosed': onclosed,
               'onjust_opened': onjust_opened, }})


fsm.was_closed()
fsm.open_now()
fsm.opened_forever()
fsm.close_now()
