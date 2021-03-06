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
### default setup for basic push server and python scripts
# update your Raspian
sudo apt-get update
sudo apt-get upgrade

# git is good for deploy or cloning of this code, already installed in latest 1/2014 raspian
sudo apt-get install git

# install ruby.  The 1.9.1-dev actually is the later version of ruby, already installed too
# 1.9.3 to be installed too
sudo apt-get install ruby1.9.1-dev ruby1.9.3

# install god process monitoring
# it will keep the daemons alive, github uses this
sudo gem install god

# easier networking with a <hostname>.local address
# great for any PC or mac user to avoid remembering the IP address
sudo apt-get install avahi-daemon

# get latest dev packages for python
sudo apt-get install python-dev-all
sudo apt-get install python-pip

# install rpi.gpio library for GPIO control
sudo pip install rpi.gpio

# install python yaml
# this is used for app_config.yaml file
sudo apt-get install python-yaml



#### sinatra_app/ requires the below

# sqlite3 and ruby
# python doesn't need this, but ruby needs this for the ruby sqlite3 gem
sudo apt-get install sqlite3 libsqlite3-dev

# --no-ri and --no-rdoc avoids any documentation installation
# 99.9% of the time, people don't use this, so why waste install time and space on your pi
# the install on raspberry pi takes VERY long with RI and RDOC enabled

# install ruby sqlite3 drivers
sudo gem install sqlite3 --no-ri --no-rdoc

# ultrasimple ruby web framework
# the code for the web
sudo gem install sinatra --no-ri --no-rdoc

# web server in ruby which can run sinatra
sudo gem install thin --no-ri --no-rdoc


```

4. Copy over the GPIO tests to verify the input detection is good.  A multimeter can also be used to confirm the voltages are 3.3V and 0V.
5. 


### Start the led server:
screen bash
sudo python garage_monitor_server/led_server.py
# detach from screen
Ctrl-a d 

# start the garage monitor sensor
screen bash
sudo python garage_monitor_server/garage_monitor.py
# detach from screen
Ctrl-a d 


-----
TODO in future versions

1. Fix FSM state machine to have the process automatically poll a shared state to know when to exit.  I want to avoid terminating the process and restarting a new one.  It just seems a bit of overkill to do that.

