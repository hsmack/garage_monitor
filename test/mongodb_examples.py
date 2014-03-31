#!/usr/bin/env python
#
# try out mongodb
#
#
import datetime
from pymongo import MongoClient

#
# Need to mimic this!
#
# DROP TABLE IF EXISTS door;
# CREATE TABLE door(
#   id INTEGER PRIMARY KEY,
#   timestamp DATE,
#   value INTEGER,
#   status TEXT
# );

# DROP TABLE IF EXISTS startup;
# CREATE TABLE startup(
#   id INTEGER PRIMARY KEY,
#   timestamp DATE,
#   host TEXT
# );


client = MongoClient()
db = client.garage

doors = db.door
new_door = [{"timestamp": datetime.datetime(2013, 11, 11, 12, 12, 12),
    "value": -1,
    "status": 'CLOSED'},
  {"timestamp": datetime.datetime(2013, 11, 11, 12, 14, 14),
    "value": -1,
    "status": 'OPEN'},
  {"timestamp": datetime.datetime(2013, 11, 11, 12, 16, 16),
    "value": -1,
    "status": 'CLOSED'}]

# doors.insert(new_door)

print doors.count()

print '---- All CLOSED'
for door in doors.find({"status": "CLOSED"}):
  print door

print '---- Last door state'
for door in doors.find().limit(1).sort([("timestamp", 1)]):
  print door
