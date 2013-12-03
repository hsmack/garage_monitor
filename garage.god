
# Watcher that auto-daemonizes and creates the pid file
God.watch do |w|
  w.name = 'garage'
  w.start = "ruby /home/pi/garage_monitor_daemon.rb"
  w.log = '/var/log/garage.log'
  w.dir = '/home/pi'
  w.keepalive(:memory_max => 150.megabytes)
  w.behavior(:clean_pid_file)
end

