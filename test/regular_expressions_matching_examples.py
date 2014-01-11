#!/usr/bin/env python
#
# python regular expressions
#

import re

s = 'OPEN'

p = re.compile('open', re.IGNORECASE)
m = p.match(s)
if m:
  print 'Match found: ', m.group()
else:
  print 'No match'


# regular matching
# matcher = re.compile('OPEN', re.IGNORECASE)
# print filter(matcher.match, [s])
# if s.match(r'OPEN'):
  # print   "match1"

# case insensitive matching
# if s.match('open/i')