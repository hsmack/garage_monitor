#!/usr/bin/env ruby
# Monitor garage door activity using a Raspberry Pi input pin
# The pin number is specified by the user
#

require 'pi_piper'
require 'pony'
require 'yaml'
require 'socket'

# enable daemon
require 'dante'

class GarageMonitor

  # Example config file app_config.yml
  #
  #
  # ---
  # notify_email: me@example.com
  # sender_email: pi@example.com
  # smtp:
  #   address: smtp.gmail.com
  #   port: 587
  #   user_name: pi@example.com
  #   password: <mysecretpassword>
  #   authentication: :plain
  #
  APP_CONFIG = 
    begin
      YAML.load_file("app_config.yml")
    rescue
      $stderr.puts "Could not find SMTP info"
      exit -1
    end

  DEFAULT_GARAGE_DOOR_MONITOR_GPIO = 8


  def initialize(selected_pin = DEFAULT_GARAGE_DOOR_MONITOR_GPIO)
    @gpio_pin = selected_pin
    @pin = PiPiper::Pin.new(:pin => @gpio_pin, :direction => :in)
    # @pin = PiPiper::Pin.new(:pin => pin, :direction => :in, :pull => :up) #:pull => :up

  end

  def thread_report_garage_status(*args)
    t = Thread.new do
      report_garage_status(*args)
      Thread.exit
    end
    t.abort_on_exception = true
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

  def send_garage_status_email_to(recipients, state="Unknown", email_status)
    host_name = Socket.gethostname
    email_subject = "Garage Door Detector"

    # example
    # Pony.mail(:to => 'you@example.com', :cc => 'him@example.com', :from => 'me@example.com', :subject => 'hi', :body => 'Howsit!')
    Pony.mail({
      :to => recipients,
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

  def run
    puts "  GARAGE_DOOR_MONITOR_GPIO pin as input: #{@gpio_pin}"
    puts "  Garage monitor initialized ..."

    ### The LOOP ###

    while (1) do
      value = @pin.read
      if @last_state != value
        sleep 0.6
        if @pin.read == value
          time = Time.now.localtime
          thread_report_garage_status(value, time, true)
          @last_state = value
          @last_time = time
        else
          puts "false trigger"
        end
      else
        # do nothing
      end
    end
  end

end


Dante.run('timeprinter') do |opts|
  garage_app = GarageMonitor.new(8)
  garage_app.run
end

