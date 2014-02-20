#!/usr/bin/env python
#
# create processes (that can use multiple processors)
# 
#
from multiprocessing import Process
import time, signal

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
# led_test(green_led)
# led_test(red_led)


def blinky():
  global green_led
  # 100 times is 1 minute
  # 50 times is 30 seconds
  for i in xrange(50):
    green_led.off()
    time.sleep(0.3)
    green_led.on()
    time.sleep(0.3)

if __name__ == '__main__':
  global p
  # global green_led, red_led
  p = Process(target=blinky, args=())
  p.start()
  time.sleep(4)
  print repr(p.is_alive())
  
  # normally the process will go for 30 seconds, but instead, it will go for 4 seconds
  # and be killed.
  p.terminate()

  time.sleep(0.1) # make sure the process quit
  print repr(p.is_alive())
  test = (p.exitcode == -signal.SIGTERM)
  print repr(test)


