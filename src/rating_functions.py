#!/usr/bin/python

from tcstats import app

from collections import defaultdict

config = app.config

def as_of(conn):
  cursor = conn.cursor()
  last_round_sql = \
      "SELECT short_name, date FROM rounds ORDER BY date DESC LIMIT 1"
  name, date = cursor.execute(last_round_sql).fetchone()
  return "%s (%s)" % (name, date)

pname = {1: "Easy", 2: "Medium", 3: "Hard"}

def ordinal(i):
  last_dig = i % 10
  suffix = ""
  if 10 < i % 100 < 20:
    suffix = "th"
  elif last_dig == 1:
    suffix = "st"
  elif last_dig == 2:
    suffix = "nd"
  elif last_dig == 3:
    suffix = "rd"
  else:
    suffix = "th"
  return str(i) + suffix

def get_compliment(rating):
  compliments = [
    (4000, "an unreal super-hyper-target"),
    (3700, "an indisputably world-class"),
    (3600, "an off-the-charts awesome"),
    (3500, "a splendiferatageneous"),
    (3400, "an absolutely elite"),
    (3300, "a world beating"),
    (3200, "a truly amazing"),
    (3100, "a really quite very smart"),
    (3000, "an unoverestimatable"),
    (2900, "a soon-to-be-targeted"),
    (2800, "an upper crust"),
    (2700, "a smashing"),
    (2600, "an impressive"),
    (2500, "a savvy"),
    (2400, "a weighty-brained"),
    (2300, "an algorithmically inclined"),
    (2200, "a top"),
    (2100, "a soon-to-be-red"),
    (2000, "a problem gobbling"),
    (1900, "a solid"),
    (1800, "a good smart"),
    (1700, "a tough"),
    (1600, "a two-ply extra strong"),
    (1500, "a strong"),
    (1400, "a soon-to-be-yellow"),
    (1300, "a smart"),
    (1200, "a well liked"),
    (1100, "a soon-to-be-blue"),
    ( 500, "an up-and-coming"),
    (   0, "a scruffy fighter of a")
  ]
  for c in compliments:
    if rating >= c[0]:
      return c[1]
  return "an indescribable"

def rating_color(rating, target=True):
  if rating >= 3000 and target:
    return "a targeteer"
  elif rating >= 2200:
    return "red"
  elif rating >= 1500:
    return "yellow"
  elif rating >= 1200:
    return "blue"
  elif rating >= 900:
    return "green"
  else:
    return "gray"

def get_accomplishments(coder, limit):
  rating = coder["alg_rating"]
  country = coder["country_name"]
  lang = coder["pref_language"]
  participation = coder["participation"]
  accomp = []
  accomp.append("Is %s coder (rating %d)" % (get_compliment(rating), rating))
  accomp.append("Ranks %d overall" % get_ranking(rating))
  accomp.append("Ranks %d among coders from %s" % \
      (get_ranking(rating, country=country), country))
  accomp.append("Ranks %d among %s coders" % \
      (get_ranking(rating, lang=lang), lang))
  accomp.append("Ranks %d among %s coders from %s" % \
      (get_ranking(rating, lang=lang, country=country), lang, country))
  if participation > 0:
    place = get_participation_ranking(participation)
    accomp.append("Participated in %s of the last 30 SRMs (that's %s place)" % \
        (participation, ordinal(place)))
    limit -= 1
  limit -= 5
  accomp.extend(get_round_accomplishments(coder, limit))
  return accomp

def get_ranking(rating, country=None, lang=None):
  select_sql = "SELECT COUNT(coder_id) FROM coders WHERE active = 1 AND " + \
      "alg_rating > ?"
  sql_args = [rating]
  if country is not None:
    select_sql += " AND country_name = ?"
    sql_args.append(country)
  if lang is not None:
    select_sql += " AND pref_language = ?"
    sql_args.append(lang)
  cursor = conn.cursor()
  return cursor.execute(select_sql, sql_args).fetchone()[0]

def get_participation_ranking(participation):
  select_sql = "SELECT COUNT(coder_id) FROM coders WHERE participation > ?"
  cursor = conn.cursor()
  return cursor.execute(select_sql, [participation]).fetchone()[0]

def get_round_accomplishments(coder, limit):
  return [] # TODO

def pvpetr(conn, user_cid, opp_cid=10574855):
  cursor = conn.cursor()
  cids = [user_cid, opp_cid]
  fields = ",".join(["round_id", "division"] + \
      ["level_%s_final_points" % level for level in ("one", "two", "three")])
  find_match_scores = \
      "SELECT %s FROM results WHERE coder_id = ? AND rated_flag = 1" % fields
  find_match_name = "SELECT short_name FROM rounds WHERE round_id = ?"
  matches = defaultdict(dict)
  for cid in cids:
    for row in cursor.execute(find_match_scores, [cid]):
      matches[row[0]][cid] = (row[1], row[2], row[3], row[4])
  user_win = []
  opp_win = []
  for round_id in matches:
    results = matches[round_id]
    if len(results) == 2:
      match_name = cursor.execute(find_match_name, [round_id]).fetchone()[0]
      if results[cids[0]][0] != results[cids[1]][0]:
        continue
      for problem in range(1, 4):
        user_score = results[cids[0]][problem]
        opp_score = results[cids[1]][problem]
        # TODO remove when the nulls-in-db issue is fixed
        if user_score is None:
          user_score = 0.0
        if opp_score is None:
          opp_score = 0.0
        if user_score > opp_score:
          user_win.append((match_name, problem, user_score, opp_score))
        elif user_score < opp_score:
          opp_win.append((match_name, problem, user_score, opp_score))
  return (user_win, opp_win)
