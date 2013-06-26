import math

def erfinv(x):
  lo = -6
  hi = 6
  for i in xrange(64):
    mid = (lo + hi) / 2.0
    if math.erf(mid) > x:
      hi = mid
    else:
      lo = mid
  return lo
