#!/usr/bin/env python
#
# flask web server
#
import os, sys
import yaml
import sqlite3
import inspect
from flask import Flask, render_template, request, g , redirect
app = Flask(__name__)
app.debug = True


# get absolute path, easier for daemons or process monitors (god) to run
current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
config_file_path = "%s/../config/app_config.yml" % current_path

# load universal config file
stream = open(config_file_path, 'r')
APP_CONFIG = yaml.load(stream)

# setup database
DATABASE = "%s/../database/%s" % (current_path, APP_CONFIG['database']['filename'])
# DATABASE = DATABASE_FILE_PATH = "%s/../database/%s" % (current_path, APP_CONFIG['database']['filename'])

# DATABASE
############################################

# conn=sqlite3.connect(DATABASE)
# c=conn.cursor()
# c.execute("SELECT * FROM door")
# entries = [dict(id=row[0], timestamp=row[1], value=row[2], status=row[3]) for row in c.fetchall()]
# conn.commit()
# conn.close()
# print repr(entries)

# print DATABASE
# def connect_db():
#   return sqlite3.connect(DATABASE)

# @app.before_request
# def before_request():
#   g.db = connect_db()
#   # g.db.execute("CREATE TABLE IF NOT EXISTS drawings(fname string primary key, img_data text)")

# @app.after_request
# def after_request(response):
#   g.db.close()
#   return response


# # print DATABASE
# def connect_db():
#   return sqlite3.connect(DATABASE)

# def get_db():
#   db = getattr(g, '_database', None)
#   if db is None:
#     db = g._database = connect_db()
#   return db

# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


# def connect_db():
#   return sqlite3.connect(DATABASE)

# @app.before_request
# def before_request():
#   g.db = connect_db()

# @app.teardown_request
# def teardown_request(exception):
#   if hasattr(g, 'db'):
#     g.db.close()


def connect_db():
  """Connects to the specific database."""
  rv = sqlite3.connect(DATABASE)
  rv.row_factory = sqlite3.Row
  return rv


# def init_db():
#     """Creates the database tables."""
#     with app.app_context():
#         db = get_db()
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()


def get_db():
  """Opens a new database connection if there is none yet for the
  current application context.
  """
  if not hasattr(g, 'sqlite_db'):
    g.sqlite_db = connect_db()
  return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
  """Closes the database again at the end of the request."""
  if hasattr(g, 'sqlite_db'):
    g.sqlite_db.close()




# def query_db(query, args=(), one=False):
#     """Queries the database and returns a list of dictionaries."""
#     cur = g.db.execute(query, args)
#     rv = [dict((cur.description[idx][0], value)
#                for idx, value in enumerate(row)) for row in cur.fetchall()]
#     return (rv[0] if rv else None) if one else rv

# @app.before_request
# def before_request():
#     """Make sure we are connected to the database each request and look
#     up the current user so that we know he's there.
#     """
#     g.db = connect_db()


# @app.after_request
# def after_request(response):
#     """Closes the database again at the end of the request."""
#     g.db.close()
#     return response


db = get_db()
cur = db.execute('select title, text from entries order by id desc')
entries = cur.fetchall()


# cur = g.db.cursor()
# cur.execute('select * from door')
# py_all = {}
# all_data = cur.execute('SELECT * FROM door')
# for data in all_data:
#     py_all[data[0]] = data[1]

# # entries = [dict(id=row[0], timestamp=row[1], value=row[2], status=row[3]) for row in cur.fetchall()]
# print repr(all_data)

# TEMPLATE FILTERS
############################################

@app.template_filter('')
def reverse_filter(s):
  return s[::-1]
app.jinja_env.filters['reverse'] = reverse_filter



# ROUTES
############################################

@app.route("/")
def index():

  door_state = 'open'

  return render_template('index.html', 
    door_state=door_state, 
    house_name="El Rancho")
# def show_entries():
#   cur = g.db.execute('select title, text from entries order by id desc')
#   entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
#   return render_template('show_entries.html', entries=entries)

@app.route("/current")
def current():
  return "{'json'}"


if __name__ == "__main__":
  app.run()



