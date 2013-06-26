#!/usr/bin/python

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

def stupid_adjective(rating):
  compliments = {
    35: "a splendiferatageneous",
    34: "an absolutely elite",
    33: "a world beating",
    32: "a truly amazing",
    31: "a really quite very smart",
    30: "an unoverestimatable",
    29: "a soon-to-be-targeted",
    28: "an upper crust",
    27: "a smashing",
    26: "an impressive",
    25: "a savvy",
    24: "a weighty-brained",
    23: "an algorithmically inclined",
    22: "a top",
    21: "a soon-to-be-red",
    20: "a problem gobbling",
    19: "a solid",
    18: "a good smart",
    17: "a tough",
    16: "a two-ply extra strong",
    15: "a strong",
    14: "a soon-to-be-yellow",
    13: "a smart",
    12: "a well liked",
    11: "a soon-to-be-blue",
     5: "an up-and-coming",
     0: "a scruffy fighter of a"
  }
  rating_ind = rating / 100
  if rating_ind < 5:
    rating_ind = 0
  elif rating_ind < 11:
    rating_ind = 5
  elif rating_ind > 35:
    rating_ind = 35
  return compliments[rating_ind]

