#!/usr/bin/env python

# only need to test threaded sending
import thread
import time


import smtplib


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


import ConfigParser, os

APP_CONFIG = ConfigParser.ConfigParser()
APP_CONFIG.readfp(open('app_config.cfg'))


#
# send an email from a python script
# relies on alll the information from the APP_CONFIG
#
def send_email(door_state, timestamp):
  global APP_CONFIG
  # me == my email address
  # you == recipient's email address
  from_email = "%s <%s>" % (APP_CONFIG.get('SMTP', 'user_from'), APP_CONFIG.get('SMTP', 'login'))
  to = APP_CONFIG.get('EMAIL NOTIFICATIONS', 'notify_email')

  # Create message container - the correct MIME type is multipart/alternative.
  msg = MIMEMultipart('alternative')
  msg['Subject'] = "Garage Door Detector"
  msg['From'] = from_email
  msg['To'] = to


  # put a timestamp
  human_readable_time = time.strftime("%a, %d %b %Y %H:%M:%S", timestamp)
  # print now

  # Create the body of the message (a plain-text and an HTML version).
  text = "Hi!\n\nGarageDoorStatus: %s\t%s\nGoto http://blue.local/ to view manual settings\n\n" % (door_state, human_readable_time)
  html = """\
  <html>
    <head></head>
    <body>
      <p>Hi!<br><br>
         GarageDoorStatus: %s %s<br>
         Goto <a href="http://blue.local/garage">http://blue.local/garage</a> to view history\n\n
      </p>
    </body>
  </html>
  """ % (door_state, human_readable_time)

  # Record the MIME types of both parts - text/plain and text/html.
  part1 = MIMEText(text, 'plain')
  part2 = MIMEText(html, 'html')

  # Attach parts into message container.
  # According to RFC 2046, the last part of a multipart message, in this case
  # the HTML message, is best and preferred.
  msg.attach(part1)
  msg.attach(part2)

  # Send the message via local SMTP server.
  # s = smtplib.SMTP('localhost')

  # Send the message via Google SMTP
  # http://segfault.in/2010/12/sending-gmail-from-python/
  s = smtplib.SMTP(APP_CONFIG.get('SMTP','address'))
  # s.set_debuglevel(1)
  s.esmtp_features["auth"] = "LOGIN PLAIN"
  # s.ehlo()
  s.starttls()
  # s.ehlo()
  s.login(APP_CONFIG.get('SMTP','login'), APP_CONFIG.get('SMTP','password'))


  # sendmail function takes 3 arguments: sender's address, recipient's address
  # and message to send - here it is sent as one string.
  s.sendmail(from_email, to.split(','), msg.as_string())
  print "Email sent %s" % human_readable_time
  # time.sleep(4)
  s.quit()


#
# runs send_email() inside a thread, so it's non blocking
#
def send_email_in_thread(door_state, timestamp):  
  # Create two threads as follows
  try:
     thread.start_new_thread(send_email, (door_state, timestamp))
  except:
     print "Error: unable to send email in a thread"

timestamp = time.localtime()
send_email_in_thread('OPEN', timestamp)

while 1:
   pass
