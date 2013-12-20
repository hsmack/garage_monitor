#!/usr/bin/env ruby
#
# creates a clean database
#

require 'pp'
require 'sqlite3'

def create_table_from_scratch(db)
  sql = <<SQL
DROP TABLE IF EXISTS door;
CREATE TABLE door(
  id INTEGER PRIMARY KEY,
  timestamp DATE,
  value INTEGER,
  status TEXT
);

DROP TABLE IF EXISTS startup;
CREATE TABLE startup(
  id INTEGER PRIMARY KEY,
  timestamp DATE,
  host TEXT
);

SQL

  db.execute_batch( sql )
end

db = SQLite3::Database.new("gm.db")
create_table_from_scratch(db)

