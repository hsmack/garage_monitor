#!/usr/bin/env python
import ConfigParser, os

config = ConfigParser.ConfigParser()
config.readfp(open('config.cfg'))

print config.get('Section 1','foodir')



config = ConfigParser.ConfigParser()
config.readfp(open('app_config.cfg'))

print config.items('ENABLE NOTIFICATIONS')
print config.items('EMAIL NOTIFICATIONS')
print config.items('PUSH NOTIFICATION CLIENT')
print config.items('DATABASE')
print config.items('SMTP')


print config.get('SMTP','password')
print "%s <%s>" % (config.get('SMTP', 'user_from'), config.get('SMTP', 'login'))
print config.get('EMAIL NOTIFICATIONS', 'notify_email').split(',')
