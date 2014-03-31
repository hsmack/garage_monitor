#!/usr/bin/env python

# client program
import socket
import time

# HOST = 'tv.local'    # The remote host
#
# HOST = the remote host
# PORT = the port of the remote host
#
HOST = '127.0.0.1'
PORT = 4003

for i in xrange(4):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  data = '0,OPEN,2013-12-13 14:11:11' + str(i)
  print 'sending payload ...', repr(data)
  s.sendall(data)
  
  #
  # optional server reply
  # 
  # data = s.recv(1024)
  # print 'Received', repr(data)  # if there's a server reply

  s.close()
  time.sleep(1)
  print "sleep..."
