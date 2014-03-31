#!/usr/bin/env python
#
# use urllib2 instead of trying to install pycurl
#

url = 'http://garage.local/current.json'

# from StringIO import StringIO    
# import pycurl

# storage = StringIO()
# c = pycurl.Curl()
# c.setopt(c.URL, url)
# c.setopt(c.WRITEFUNCTION, storage.write)
# c.perform()
# c.close()
# content = storage.getvalue()
# print content


#
# example to do password auth
#

# import urllib2
# def getUserData(url):
#   # first encode the username & password 
#   userData = "Basic " + (uName + ":" + pWord).encode("base64").rstrip()
#   # create a new Urllib2 Request object 
#   req = urllib2.Request('https://api.github.com/users/braitsch')
#   # add any additional headers you like 
#   req.add_header('Accept', 'application/json')
#   req.add_header("Content-type", "application/x-www-form-urlencoded")
#   # add the authentication header, required
#   req.add_header('Authorization', userData)
#   # make the request and print the results
#   res = urllib2.urlopen(req)
#   print res.read()
# getUserData()

#
# example for garage_monitor
#

import urllib2
req = urllib2.Request(url)
req.add_header('Accept', 'application/json')
res = urllib2.urlopen(req)
# print res.read()

jdata = res.read()
print jdata


import json
decoded = json.loads(jdata)
print 'DECODED:', decoded

