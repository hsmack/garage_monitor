#!/usr/bin/env python
# gmonitor.py
#
# garage monitor, uses ultrasonic distance detection (2 sensors) to determine
# if the garage door is open or not
#
#
import time
import RPi.GPIO as GPIO


# Define GPIO to use on Pi
GPIO_TRIGGER1 = 11
GPIO_ECHO1    = 8

# if using a second sensor
GPIO_TRIGGER2 = 22
GPIO_ECHO2    = 23


class DistanceDetector:
  """garage monitor, uses ultrasonic distance detection to determine if the garage door is open or not"""
  def __init__(self, trigger_pin, echo_pin):

    self.trigger_pin = trigger_pin
    self.echo_pin = echo_pin

    # Use BCM GPIO references
    # instead of physical pin numbers
    GPIO.setmode(GPIO.BCM)

    # Set pins as output and input
    GPIO.setup(self.trigger_pin,GPIO.OUT)  # Trigger
    GPIO.setup(self.echo_pin,GPIO.IN)      # Echo

    # Allow module to settle
    time.sleep(0.5)

  def measure(self):
    # Send 10us pulse to trigger
    GPIO.output(self.trigger_pin, True)
    time.sleep(0.00001)
    GPIO.output(self.trigger_pin, False)
    start = time.time()

    timeout_start = time.time()
    timeout_exceeded = False

    while GPIO.input(self.echo_pin)==0:
      start = time.time()

    while GPIO.input(self.echo_pin)==1:
      stop = time.time()

    # Calculate pulse length
    elapsed = stop-start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s) and /2 the distance
    distance = elapsed * 34029 / 2

    print "Distance : %.1f cm" % distance
    return distance


#
# main()
#
def main():
  print "Ultrasonic Measurement, 2 sensors"

  blue = DistanceDetector(GPIO_TRIGGER1, GPIO_ECHO1)#, 2)
  red = DistanceDetector(GPIO_TRIGGER2, GPIO_ECHO2)#, 2)

  for i in xrange(15):
    print("{} blue...".format(i))
    blue.measure()
    red.measure()
    time.sleep(1)


  # Reset GPIO settings
  GPIO.cleanup()




if __name__ == "__main__":
    main()
