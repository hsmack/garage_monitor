#!/usr/bin/env ruby
# Hard script to monitor garage door activity
#

require 'pi_piper'
require 'pony'
require 'socket'

APP_CONFIG = 
  begin
    YAML.load_file("app_config.yml")
  rescue
    $stderr.puts "Could not find SMTP info"
    exit -1
  end

include PiPiper
GARAGE_DOOR_GPIO = 8

#####################################################################
# main()
#####################################################################

$i = 0
$previous_state = nil
$pin = PiPiper::Pin.new(:pin => GARAGE_DOOR_GPIO)
# $pin = PiPiper::Pin.new(:pin => GARAGE_DOOR_GPIO, :direction => :in, :pull => :up) #:pull => :up

def send_garage_status_email_to(recipient, state="Unknown", email_status)
  host_name = Socket.gethostname
  email_subject = "Garage Door Detector"

  # example
  # Pony.mail(:to => 'you@example.com', :cc => 'him@example.com', :from => 'me@example.com', :subject => 'hi', :body => 'Howsit!')
  Pony.mail({
    :to => recipient,
    :from => APP_CONFIG['sender_email'],
    :via => :smtp,
    :via_options => {
      :address              => APP_CONFIG['smtp']['address'],
      :port                 => APP_CONFIG['smtp']['port'],
      :enable_starttls_auto => true,
      :user_name            => APP_CONFIG['smtp']['user_name'],
      :password             => APP_CONFIG['smtp']['password'],
      :authentication       => APP_CONFIG['smtp']['authentication'], # :plain, :login, :cram_md5, no auth by default
      :domain               => host_name # the HELO domain provided by the client to the server
    },
    :subject => email_subject,
    :body => "#{email_subject}\n\n#{email_status}\n\nGoto http://garage.local/ to view manual settings\n\n",
  
  })
  puts "  email sent..."
end


def pin_changed?
  $previous_state != $pin.value
end

def report_garage_status(value, time, email=false)
  status = "Unknown"
  if value == 0
    status = 'OPEN  '
  else
    status = 'Closed'
  end  
  email_status = "Garage Door #{status}\t#{time}" 
  puts email_status

  send_garage_status_email_to(APP_CONFIG['notify_email'], status, email_status) if email
end

#####################################################################
# main()
#####################################################################

puts "  GARAGE_DOOR_GPIO pin as input: #{GARAGE_DOOR_GPIO}"
puts "  Garage monitor initialized ..."

### The LOOP ###

while (1) do
  value = $pin.read
  if $last_state != value
    sleep 0.6
    if $pin.read == value
      time = Time.now.localtime
      report_garage_status(value, time, true)
      $last_state = value
      $last_time = time
    else
      puts "false trigger"
    end
  else
    # puts "no change, pin: #{$pin.read}"
    # sleep 0.3
    # do nothing
  end
  
end

