
# Watcher that auto-daemonizes and creates the pid file
God.watch do |w|
  w.name = 'garage_monitor'
  w.start = "python /home/pi/garage/garage_monitor_server/garage_monitor.py"
  # w.log = '/var/log/garage.log'
  w.log_cmd = '/usr/bin/logger -t garage_mon'
  w.dir = '/home/pi/garage'

  w.keepalive(:memory_max => 150.megabytes)
  w.behavior(:clean_pid_file)
end

