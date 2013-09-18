#!/usr/bin/python

from math import erf, sqrt

# invert the error function (erf) using binary search
def erfinv(x):
  lo = -6
  hi = 6
  for i in xrange(64):
    mid = (lo + hi) / 2.0
    if erf(mid) > x:
      hi = mid
    else:
      lo = mid
  return lo

# inverse CDF (quantile) of standard normal distribution (= probit function)
def probit(x):
  return sqrt(2) * erfinv(2 * x - 1)

def calc_win_probabiilty(user, other):
  return 0.5 * (erf((other["old_rating"] - user["old_rating"]) / sqrt(2 * \
      (other["old_vol"] ** 2 + user["old_vol"] ** 2))) + 1)

def calc_perf_as(user, rank, coders):
  n = len(coders)
  avg_rating = float(sum(coder["old_rating"] for coder in coders)) / n
  sq_vol = float(sum(coder["old_vol"]**2 for coder in coders)) / n
  sq_rating_diff = float(sum(
      (coder["old_rating"] - avg_rating)**2 for coder in coders)) / (n - 1)
  competition_factor = sqrt(sq_vol + sq_rating_diff)
  expected_rank = 0.5
  for coder in coders:
    expected_rank += calc_win_probability(user, coder)
  expected_perf = -probit((expected_rank - 0.5) / n)
  actual_perf = -probit((rank - 0.5) / n)
  return user["old_rating"] + competition_factor * (actual_perf - expected_perf)

def calc_new_rating_vol(user, rank, played, coders):
  rating, vol = user["old_rating"], user["old_vol"]
  perf_as = calc_perf_as(user, rank, coders)
  weight = 1 / (1 - (0.42 / (played + 1) + 0.18)) - 1
  if new_rating > rating + cap:
    new_rating = rating + cap
  elif new_rating < rating - cap:
    new_rating = rating - cap
  new_vol = sqrt((new_rating - rating)**2 / weight + vol**2 / \
      (weight + 1))
  return (new_rating, new_vol)

def iterated_perf_as(coder_id, round_id, iterations=30):
  dummy = {"old_rating": 1200, "old_vol": 337}
  rank = get_round_ranking(coder_id, round_id)
  coders = get_coders(round_id)
  for i in range(iterations):
    dummy["old_rating"] = calc_perf_as(dummy, rank, coders)
  return dummy["old_rating"]

def get_round_ranking(coder_id, round_id):
  rank_sql = "SELECT division_placed FROM results WHERE round_id = ? " + \
      "AND coder_id = ?"
  cursor = conn.cursor()
  return cursor.execute(rank_sql, [coder_id, round_id]).fetchone()[0]

def get_coders(round_id):
  select_sql = "SELECT old_rating, old_vol FROM results WHERE round_id = ?"
  cursor = conn.cursor()
  return cursor.execute(select_sql, [round_id]).fetchall()
