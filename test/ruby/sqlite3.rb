#!/usr/bin/env ruby

require 'pp'
require 'sqlite3'

# http://sqlite-ruby.rubyforge.org/sqlite3/faq.html

# sqlite3 test.db
# sqlite> create table door(id INTEGER PRIMARY KEY, timestamp DATE, value INTEGER, status TEXT);
# sqlite> insert into door (id, timestamp, value, status) values (1, '2013-11-11 12:12:12', 1, 'Closed');
# sqlite> insert into door (id, timestamp, value, status) values (2, '2013-11-11 12:14:14', 0, 'Open');
# sqlite> insert into door (id, timestamp, value, status) values (3, '2013-11-11 12:16:16', 1, 'Closed');
# sqlite> select * from door;
# 1|2013-11-11 12:12:12|1|Closed
# 2|2013-11-11 12:14:14|0|Open
# 3|2013-11-11 12:16:16|1|Closed

def load_table_from_scratch(db)
  sql = <<SQL
DROP TABLE IF EXISTS door;
CREATE TABLE door(
  id INTEGER PRIMARY KEY,
  timestamp DATE,
  value INTEGER,
  status TEXT
);

INSERT into door (id, timestamp, value, status) values (1, '2013-11-11 12:12:12', 1, 'Closed');
INSERT into door (id, timestamp, value, status) values (2, '2013-11-11 12:14:14', 0, 'Open');
INSERT into door (id, timestamp, value, status) values (3, '2013-11-11 12:16:16', 1, 'Closed');

DROP TABLE IF EXISTS startup;
CREATE TABLE startup(
  id INTEGER PRIMARY KEY,
  timestamp DATE,
  host TEXT
);
INSERT into startup (id, timestamp, host) values (1, '2013-11-11 20:20:20', 'garage');

SQL

  db.execute_batch( sql )
end

db = SQLite3::Database.new("test.db")
load_table_from_scratch(db)

db.busy_timeout=5000


db.execute( "select * from door" ) do |row|
	pp row
end
# [1, "2013-11-11 12:12:12", 1, "Closed"]
# [2, "2013-11-11 12:14:14", 0, "Open"]
# [3, "2013-11-11 12:16:16", 1, "Closed"]

# json output
require 'json'
all = db.execute( "select * from door" )
p all.to_json


row = db.get_first_row( "select * from door" )
pp row
# [1, "2013-11-11 12:12:12", 1, "Closed"]

#
# get next row id
#
i = db.get_first_value( "select max(id) from door" )
pp i
# => 3
pp (i+=1)
# => 4
pp i
# => 4

#
# ORDER BY [ASC|DESC]
#
row = db.get_first_row( "select * from door order by timestamp desc" )
pp row
# [3, "2013-11-11 12:16:16", 1, "Closed"]


j = db.get_first_value( "select max(id) from startup" )
row = db.execute( "INSERT into startup (id, timestamp, host) values (?, ?, ?);", (j+=1), Time.now.strftime('%F %T'), `hostname`.chomp)
pp row


db.results_as_hash = true

#
# ORDER BY [ASC|DESC]
#
row = db.get_first_row( "select * from startup order by timestamp desc" )
pp row
# [3, "2013-11-11 12:16:16", 1, "Closed"]



  def db_last_id(db, table)
    return db.get_first_value( "select max(id) from #{table}" )
  end
    i = db_last_id(db, 'startup')

    #
    # log the start time into database
    # this is good for debugging
    #
    row = db.execute( "INSERT into startup (id, timestamp, host) values (?, ?, ?);", (i+=1), Time.now.strftime('%F %T'), `hostname`.chomp)




