# Pi Garage Door Detector

I keep forgetting that my garage door is open.
This design is only to detect the door is open and send emails to notify the state change.

The webserver also allows a Raspberry Pi in my house to turn on/off the LED based on the garage's door state.  This LED is next to my TV, so I always know.

-----

## INSTRUCTIONS
1. Install the Raspian image.  Latest one is fine.
2. Setup wifi dongle.  
  - Mine was from Element 7, Adafruit or other ones will be fine too
  - `lsusb` finds it as:  Ralink Technology, Corp. RT5370 Wireless Adapter
  http://www.howtogeek.com/167425/how-to-setup-wi-fi-on-your-raspberry-pi-via-the-command-line/
3. Setup all the ruby gems that you need

```
# update your Raspian
sudo apt-get update
sudo apt-get upgrade

# optional I use this for 
sudo apt-get install git-core

# install ruby.  The 1.9.1-dev will still allow 1.9.3 to be installed
# These are instructions from pi_piper, otherwise, I'd use ruby 2.0.0
sudo apt-get install ruby ruby1.9.1-dev

# library to control Pi's GPIOs
# https://github.com/jwhitehorn/pi_piper
sudo gem install pi_piper

# web design framework
sudo gem install sinatra

# web server in ruby
sudo gem install thin

# simple ruby library to send email
# https://github.com/benprew/pony
sudo gem install pony
```

4. Copy over the GPIO tests to verify the input detection is good.  A multimeter can also be used to confirm the voltages are 3.3V and 0V.
5. 