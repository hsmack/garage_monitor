
# Watcher that auto-daemonizes and creates the pid file
God.watch do |w|
  w.name = 'garage_webapp'
  w.start = "ruby /home/pi/garage/garage_monitor_webapp/garage_webapp.rb"
  # w.log = '/var/log/garage.log'
  w.log_cmd = '/usr/bin/logger -t garage_web'
  w.dir = '/home/pi/garage'

  w.keepalive(:memory_max => 150.megabytes)
  w.behavior(:clean_pid_file)
end

