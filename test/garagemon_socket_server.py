#!python
#
# socket server for debugging
# This simulates the garage_monitor.py script, but makes it simple to
# debug led_server.py
#

import time
import socket
from multiprocessing import Process, Queue


HOST = "127.0.0.1"
PORT = 4003

# start socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

# add as global variables, so I can exit_gracefully()
conn = False


#
# multiprocessing queue to manage incoming data
#
q = Queue()

def run_socket_server(q):  
  global s, conn
  
  while True:
    # DEBUG ONLY
    # time.sleep(1)
    # print "socket server started..."

    #
    # If this server fails, then the TCP stack will hold off the port
    # for about 2 minutes, before it can be used again.  
    # This is a more annoying for debugging, but feasible to get around
    #
    (conn, addr) = s.accept()
    if conn and addr:
      # val = state['door_state']
      # print 'socket: Connected by %s and state is: %s' % (addr, val)
      data = conn.recv(1024)
      print 'socket: Connected by %s and data is: %s' % (addr, data)
      # state[0] = data
      q.put(data)
      # conn.sendall('gotit')  # if you want to talk back
      conn.close()
      
  s.close()
  pass


# initialize 
socket_server = Process(target=run_socket_server, args=(q,))
socket_server.start()



i = 0
while True:
  print "%d: current state is %s" % (i, q.get())
  time.sleep(2)
  i += 1

