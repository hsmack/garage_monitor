#!/usr/bin/env python
# 
# simple socket client example for garage_monitor
#

import os
import socket
import time

#
# HOST = the remote host
# PORT = the port of the remote host
#
HOST = os.getenv('GM_HOST', '127.0.0.1')
PORT = os.getenv('GM_PORT', 4001)

print "remote server is %s:%s ..." % (HOST, PORT)


for i in xrange(4):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, int(PORT)))
  data = '0,OPEN,2013-12-13 14:11:11' + str(i)
  print 'sending payload ...', repr(data)
  s.sendall(data)
  
  #
  # optional server reply
  # 
  # data = s.recv(1024)
  # print 'Received', repr(data)  # if there's a server reply

  s.close()

  time.sleep(1) # easier debug
