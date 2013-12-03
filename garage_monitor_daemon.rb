#!/usr/bin/env ruby
# Monitor garage door activity using a Raspberry Pi input pin
# The pin number is specified by the user
#

require 'pi_piper'
require 'pony'
require 'yaml'
require 'sqlite3'
require 'socket'
require 'pp'

# enable daemon
# require 'dante'

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
      $stderr.puts "Could not find SMTP info or the 'app_config.yml' file"
      exit -1
    end

  DEFAULT_GARAGE_DOOR_MONITOR_GPIO = 8
  DATABASE_NAME = APP_CONFIG['database']['database']
  DATABASE_TIMEOUT = APP_CONFIG['database']['timeout']

  PUSH_NOTIFY_HOST = APP_CONFIG['tcp_socket_notifications']['host']
  PUSH_NOTIFY_PORT = APP_CONFIG['tcp_socket_notifications']['port']

  def initialize(selected_pin = DEFAULT_GARAGE_DOOR_MONITOR_GPIO)

    @gpio_pin = selected_pin

    #
    # determine when the monitor was started.  Used to check
    # if the latest garage door status was a new start
    #
    @start_time = Time.now

    db = SQLite3::Database.new(DATABASE_NAME)
    db.busy_timeout = DATABASE_TIMEOUT
    i = db_last_id(db, 'startup')

    #
    # log the start time into database
    # this is good for debugging
    #
    row = db.execute( "INSERT into startup (id, timestamp, host) values (?, ?, ?);", (i+=1), @start_time.strftime('%F %T'), `hostname`.chomp)

    # cleanup memory
    row = nil
    db = nil

    #
    # GPIO setup
    # external pullup attached
    #
    @pin = PiPiper::Pin.new(:pin => @gpio_pin, :direction => :in)

    # internal pullup
    # @pin = PiPiper::Pin.new(:pin => pin, :direction => :in, :pull => :up)


  end

  def db_last_id(db, table)
    i = db.get_first_value( "select max(id) from #{table}" )
    if i.nil?
      i = 0
    end
    return i
  end

  def thread_report_garage_status(*args)
    t = Thread.new do
      Thread.abort_on_exception = true
      report_garage_status(*args)
      Thread.exit
    end
  end

  def translate_garage_gpio_to_human(value)
    if value == 0
      return 'Open'
    else
      return 'Closed'
    end  
  end

  def report_garage_status(value, time, email=false)
    status = translate_garage_gpio_to_human(value).ljust(6)

    #
    # save status into DB
    #
    db = SQLite3::Database.new(DATABASE_NAME)
    i = db_last_id(db, 'door')
    i = i+1 # increment
    #
    # log the start time into database
    # this is good for debugging
    #
    row = db.execute( "INSERT into door (id, timestamp, value, status) values (?, ?, ?, ?);", i, @start_time.strftime('%F %T'), value, status)

    # cleanup memory
    row = nil
    db.close
    
    #
    # email the status, also another form of push notification
    #
    status.upcase! if status =~ /open/i

    email_status = "Garage Door #{status}\t#{time}" 
    puts email_status

    send_garage_status_email_to(APP_CONFIG['email_notifications']['notify_email'], status, email_status) if email

    #
    # send a push notification to the LED server in my house (notification lights will turn on when OPEN)
    # This is ordered last in the push notifications, because any exception from this can top the thread
    #
    push_data = [ 
      i,
      @start_time.strftime('%F %T'),
      value,
      status
    ]
    begin
      streamSock = TCPSocket.new(PUSH_NOTIFY_HOST, PUSH_NOTIFY_PORT)  
      streamSock.puts(push_data.join(','))    
      streamSock.close  
    rescue
      $stderr.puts "connection refused: #{PUSH_NOTIFY_HOST}:#{PUSH_NOTIFY_PORT}"
    end
        
  end

  def send_garage_status_email_to(recipients, state="Unknown", email_status)
    host_name = Socket.gethostname
    email_subject = "Garage Door Detector"

    # example
    # Pony.mail(:to => 'you@example.com', :cc => 'him@example.com', :from => 'me@example.com', :subject => 'hi', :body => 'Howsit!')
    Pony.mail({
      :to => recipients,
      :from => APP_CONFIG['email_notifications']['sender_email'],
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

    while (1) do
      value = @pin.read
      if @last_value != value
        sleep 0.6
        if @pin.read == value
          time = Time.now.localtime
          thread_report_garage_status(value, time, APP_CONFIG['enable_notifications']['via_email'])
          @last_value = value
          @last_time = time
        else
          puts "false trigger\t\t#{Time.now}"
        end
      else
        # do nothing
      end
    end
  end

end


# Dante.run('GarageMonitor') do |opts|
  garage_app = GarageMonitor.new(8)
  garage_app.run
# end

