#!/usr/bin/env python
#
# python sqlite3 works?
#
import sqlite3
import time
import os
import subprocess

db_conn = sqlite3.connect('gm.db')
c = db_conn.cursor()


def db_next_id(db_cursor, table):
  max_id = db_cursor.execute('SELECT max(id) FROM {}'.format(table)).fetchone()[0]
  if max_id <= 0:
    max_id = 0  
  return max_id+1

# read everything
for row in c.execute('SELECT * FROM door'):
  print(row)


max_id = c.execute('SELECT max(id) FROM startup').fetchone()[0]
print "max {}".format(max_id)

hostname = subprocess.check_output(['hostname'])
hostname = hostname.rstrip(os.linesep)
print hostname
now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# c.execute( "INSERT into startup values (?, ?, ?);", (max_id+1, now, hostname))
# db_conn.commit()


# c.execute( "INSERT into startup values (?, ?, ?, ?);", (db_next_id(c, 'startup'), now,  hostname))
# db_conn.commit()

# read everything
for row in c.execute('SELECT * FROM startup'):
  print(row)

# see that the id has changed
max_id = c.execute('SELECT max(id) FROM startup').fetchone()[0]
print "max {}".format(max_id)

c.execute('SELECT * FROM startup order by timestamp DESC LIMIT 1')
print c.fetchone()
