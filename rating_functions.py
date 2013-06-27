#!/usr/bin/python

def as_of():
  # TODO this is probably getting the first date, not last
  # check the date fmt and what ORDER BY means?
  last_round_sql = "SELECT short_name FROM rounds LIMIT 1 ORDER BY date"
  return cursor.execute(last_round_sql).fetchone()

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
    (40, "an unreal super-hyper-target"),
    (37, "an indisputably world-class"),
    (36, "an off-the-charts awesome"),
    (35, "a splendiferatageneous"),
    (34, "an absolutely elite"),
    (33, "a world beating"),
    (32, "a truly amazing"),
    (31, "a really quite very smart"),
    (30, "an unoverestimatable"),
    (29, "a soon-to-be-targeted"),
    (28, "an upper crust"),
    (27, "a smashing"),
    (26, "an impressive"),
    (25, "a savvy"),
    (24, "a weighty-brained"),
    (23, "an algorithmically inclined"),
    (22, "a top"),
    (21, "a soon-to-be-red"),
    (20, "a problem gobbling"),
    (19, "a solid"),
    (18, "a good smart"),
    (17, "a tough"),
    (16, "a two-ply extra strong"),
    (15, "a strong"),
    (14, "a soon-to-be-yellow"),
    (13, "a smart"),
    (12, "a well liked"),
    (11, "a soon-to-be-blue"),
    ( 5, "an up-and-coming"),
    ( 0, "a scruffy fighter of a")
  ]
  rating_ind = rating / 100
  for c in compliments:
    if rating_ind >= c[0]:
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
  accomp = []
  accomp.append("Is %s coder (rating %d)" % (get_compliment(rating), rating))
  accomp.append("Ranks %d overall" % get_ranking(coder))
  accomp.append("Ranks %d among coders from %s" % \
      (get_ranking(coder, country=country), country))
  accomp.append("Ranks %d among %s coders" % \
      (get_ranking(coder, lang=lang), lang))
  accomp.append("Ranks %d among %s coders from %s" % \
      (get_ranking(coder, lang=lang, country=country), lang, country))
  limit -= 5
  # TODO skipped participation accomp
  accomp.extend(get_round_accomplishments(coder, limit))
  return accomp

def get_ranking(coder, country=None, lang=None):
  return 0 # TODO

def get_round_accomplishments(coder, limit):
  return [] # TODO

# TODO PvPetr
