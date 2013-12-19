#!/usr/bin/env ruby

# ultrasonic

require 'pi_piper'
# include PiPiper


# Define GPIO to use on Pi
GPIO_TRIGGER1 = 11
GPIO_ECHO1    = 8

GPIO_TRIGGER2 = 22
GPIO_ECHO2    = 23

class DistanceDetector

  def initialize(trigger_pin, echo_pin, timeout)
    @trigger = PiPiper::Pin.new(:pin => trigger_pin, :direction => :out)
    @echo = PiPiper::Pin.new(:pin => echo_pin, :direction => :in)
    @timeout = timeout

    # initialize as false
    @trigger.off
    
  end

  def measure
    
    s = Time.now

    # Send 10us pulse to trigger
    @trigger.on
    sleep(0.00001)
    @trigger.off
    start = Time.now#.to_f

    timeout_start = start
    timeout_exceeded = false
    # @echo.read

    e = Time.now#.to_f
    c = e-s
    puts "time for triggering and 1 read #{c.to_f}"

    while @echo.read == 0
      start = Time.now.to_f
      if timeout_exceeded || ((Time.now.to_f - timeout_start) > @timeout)
        timeout_exceeded = true
        break
      end
    end

      puts "got here1 #{timeout_exceeded}"

    while @echo.read == 1
      stop = Time.now.to_f
      if timeout_exceeded || ((Time.now.to_f - timeout_start) > timeout)
        timeout_exceeded = true
        break
      end
    end

    if timeout_exceeded
      puts "Timeout exceeded ... no distance measurement"
      return -1
    end

    elapsed = stop - start

    # Distance pulse travelled in that time is time
    # multiplied by the speed of sound (cm/s) and /2 the distance
    distance = elapsed * 34029 / 2

    puts "Distance : #{distance} cm"
    return distance
  end

end

blue = DistanceDetector.new(GPIO_TRIGGER1, GPIO_ECHO1, 2)
red = DistanceDetector.new(GPIO_TRIGGER2, GPIO_ECHO2, 2)
puts "got here"
1.upto(15) do |i|
  puts "#{i}"
  blue.measure
  #red.measure
  sleep 1
end

