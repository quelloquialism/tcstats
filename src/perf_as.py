#!/usr/bin/python

import math

# invert the error function (erf) using binary search
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

# inverse CDF (quantile) of standard normal distribution (= probit function)
def probit(x):
  return math.sqrt(2) * erfinv(2 * x - 1)

def calc_win_probabiilty(competitor, user):
  return 0.5 * (math.erf((competitor[0] - user[0]) / math.sqrt(2 * \
      (competitor[1] * competitor[1] + user[1] * user[1]))) + 1)

# coders: list of 2-tuples (rating, volatility)
def calc_perf_as(user, rank, coders):
  n = len(coders)
  avg_rating = float(sum(coder["old_rating"] for coder in coders)) / n
  sq_vol = float(sum(coder["old_vol"]**2 for coder in coders)) / n
  sq_rating_diff = float(sum(
      (coder["old_rating"] - avg_rating)**2 for coder in coders)) / (n - 1)
  competition_factor = math.sqrt(sq_vol + sq_rating_diff)
  expected_rank = 0.5
  for coder in coders:
    expected_rank += calc_win_probability(coder, user)
  expected_perf = -probit((expected_rank - 0.5) / n)
  actual_perf = -probit((rank - 0.5) / n)
  return user[0] + competition_factor * (actual_perf - expected_perf)

def calc_new_rating_vol(user, rank, played, coders):
  rating, vol = user["old_rating"], user["old_vol"]
  perf_as = calc_perf_as(user, rank, coders)
  weight = 1 / (1 - (0.42 / (played + 1) + 0.18)) - 1
  cap = 150 + 1500.0 / (played + 2)
  new_rating = (rating + weight * perf_as) / (1 + weight)
  if new_rating > rating + cap:
    new_rating = rating + cap
  elif new_rating < rating - cap:
    new_rating = rating - cap
  new_vol = math.sqrt((new_rating - rating)**2 / weight + vol**2 / \
      (weight + 1))
  return (new_rating, new_vol)

def iterated_perf_as(user, rank, played, coders, iterations=30, rating=1200):
  # TODO check this stuff with jmzero (vol value? is rating change supposed
  #   to be capped? am i supposed to assume played=0 also?)
  fixed_vol = 337
  for i in range(iterations):
    rating, _ = calc_new_rating_vol((rating, fixed_vol), rank, played, coders)
  return rating
