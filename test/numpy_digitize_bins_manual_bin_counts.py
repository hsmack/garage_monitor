#!/usr/bin/env python

import numpy as NP

def count_uniques(arr):
  seen = {}
  for x in arr:
    if x in seen:
      seen[x]+=1
    else:
      seen[x] = 1
  return seen

def high_value_from_dict(in_dict):
  high_value = False
  high_index = False
  for k,v in in_dict.iteritems():
  # print k, v
    if v >= high_value:
      high_value = v
      high_index = k
  return [high_index, high_value]


A = NP.random.randint(0, 100, 100)

bins = NP.array([0., 20., 40., 60., 80., 100.])
print repr(A)

# d is an index array holding the bin id for each point in A
d = NP.digitize(A, bins)   
print repr(d)

s = count_uniques(d)
print repr(s)


#
# get the bin with the most readings (peak histogram)
#
high = []
high = high_value_from_dict(s)

print repr(high)