#!/usr/bin/env python
#
# Garage monitor webapp.
#
# Credit:
# the coding style was copied from tornado web server example blog
# https://github.com/facebook/tornado/tree/master/demos/blog

import os, sys
import yaml
import inspect
import sqlite3
import time
import re
import json

import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))  # script directory
config_file_path = "%s/../config/app_config.yml" % current_path

# load universal config file
stream = open(config_file_path, 'r')
APP_CONFIG = yaml.load(stream)

# setup database
DATABASE_FILE_PATH = "%s/../database/%s" % (current_path, APP_CONFIG['database']['filename'])
db_connection = sqlite3.connect(DATABASE_FILE_PATH)
c = db_connection.cursor()

# database schema specific index
DB_DOOR_TIME_INDEX = 1
DB_DOOR_STATE_INDEX = 3

########################################
# helpers, for templates and handlers
########################################
#
# convert database time format into a float of seconds.
#
def dbtime2secs(db_time):
  parsed_time = time.strptime(db_time , '%Y-%m-%d %H:%M:%S')
  return time.mktime(parsed_time)

#
# convert database time into any strftime format
#
def dbtime2string(db_time, strftime_format):
  parsed_time = time.strptime(db_time , '%Y-%m-%d %H:%M:%S')
  pretty_time = time.strftime(strftime_format, parsed_time)
  return pretty_time


########################################
# Handlers
########################################
class MainHandler(tornado.web.RequestHandler):
    def get(self):
      global c
      c.execute('SELECT * FROM door order by timestamp DESC LIMIT 50')
      last50 = c.fetchall()
      door_state = last50[0][DB_DOOR_STATE_INDEX]
      door_time = dbtime2secs(last50[0][DB_DOOR_TIME_INDEX])
      human_door_time = dbtime2string(last50[0][DB_DOOR_TIME_INDEX], "%a, %d %b %Y %H:%M:%S")

      # compare door state, used for switching images in output template
      door_compare_re = re.compile('open', re.IGNORECASE)
      m_door_state = door_compare_re.match(door_state) 

      self.render('index.html', 
                  door_state=door_state, 
                  human_door_time=human_door_time, 
                  m_door_state=m_door_state,
                  door_compare_re=door_compare_re,
                  last50=last50,
                  DB_DOOR_TIME_INDEX=DB_DOOR_TIME_INDEX,
                  DB_DOOR_STATE_INDEX=DB_DOOR_STATE_INDEX,
                  time=time,
                  dbtime2string=dbtime2string
                  )

class CurrentHandler(tornado.web.RequestHandler):
    def get(self):
      global c
      c.execute('SELECT * FROM door order by timestamp DESC LIMIT 50')
      last50 = c.fetchall()
      self.write(json.dumps(last50))

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
        (r"/", MainHandler),
        (r"/current.json", CurrentHandler),
        (r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler),
    ]

    settings = dict(
        house_name=u"El Rancho",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        # xsrf_cookies=True,
        # cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        debug=True,
    )
    tornado.web.Application.__init__(self, handlers, **settings )

if __name__ == "__main__":
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  # http_server.listen(8888)
  tornado.ioloop.IOLoop.instance().start()
