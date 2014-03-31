#!/usr/bin/env python
#
# creates a clean database
#

import sqlite3
import yaml

# load universal config file
stream = open("../config/app_config.yml", 'r')
APP_CONFIG = yaml.load(stream)

# create db_path loction
db_file = APP_CONFIG['database']['filename']
db_path = "../database/%s" % db_file

conn = sqlite3.connect(db_path)
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

