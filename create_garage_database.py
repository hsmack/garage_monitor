#!/usr/bin/env python
#
# creates a clean database
#

import sqlite3
conn = sqlite3.connect('gm.db')
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS door;")
c.execute("""CREATE TABLE door(
  id INTEGER PRIMARY KEY,
  timestamp DATE,
  value INTEGER,
  status TEXT
);""")
c.execute("DROP TABLE IF EXISTS startup;")
c.execute("""CREATE TABLE startup(
  id INTEGER PRIMARY KEY,
  timestamp DATE,
  host TEXT
);""")

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()

