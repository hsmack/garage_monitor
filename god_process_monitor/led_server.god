# Watcher that auto-daemonizes and creates the pid file
God.watch do |w|
  w.name = 'led_server'
  w.start = "python /home/pi/garage/led_server/led_server.py"
  # w.log = '/var/log/garage.log'
  w.log_cmd = '/usr/bin/logger -t ledserver'
  w.dir = '/home/pi/garage'
  w.keepalive(:memory_max => 150.megabytes)
  w.behavior(:clean_pid_file)
end

