#!/usr/bin/python

def as_of():
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
