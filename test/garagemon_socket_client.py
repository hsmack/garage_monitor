#!/usr/bin/env python

# client program
import socket

HOST = 'garage.local'    # The remote host
PORT = 4001              # The same port as used by the server

for i in xrange(4):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  # data = '0,OPEN,2013-12-13 14:11:11'
  data = 'get_state'
  print 'sending payload ...', repr(data)
  s.sendall(data)
  data = s.recv(1024)
  s.close()
  print 'Received', repr(data)

