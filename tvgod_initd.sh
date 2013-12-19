#!/bin/sh
 
### BEGIN INIT INFO
# Provides:             god
# Required-Start:       $all
# Required-Stop:        $all
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    God
### END INIT INFO
 
NAME=god
DESC=god
GOD_BIN=/usr/local/bin/god
GOD_CONFIG=/home/pi/tv.god
#GOD_LOG=/home/pi/tvgod.log
 
set -e
 
# Make sure the binary and the config file are present before proceeding
test -x $GOD_BIN || exit 0
 
# Create this file and put in a variable called GOD_CONFIG, pointing to
# your God configuration file
test -f $GOD_CONFIG || exit 0
 
RETVAL=0
 
case "$1" in
  start)
    echo -n "Starting $DESC: "
    $GOD_BIN -c $GOD_CONFIG #-l $GOD_LOG
    RETVAL=$?
    echo "$NAME."
    ;;
  stop)
    echo -n "Stopping $DESC: "
    $GOD_BIN quit
    RETVAL=$?
    echo "$NAME."
    ;;
  restart)
    echo -n "Restarting $DESC: "
    $GOD_BIN quit
    $GOD_BIN -c $GOD_CONFIG #-l $GOD_LOG
    RETVAL=$?
    echo "$NAME."
    ;;
  status)
    $GOD_BIN status
    RETVAL=$?
    ;;
  *)
    echo "Usage: god {start|stop|restart|status}"
    exit 1
    ;;
esac
 
exit $RETVAL