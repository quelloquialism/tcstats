import logging
import sqlite3
import time
import urllib
from xml.dom.minidom import parse

log = logging.getLogger("etl")

base_url = "http://community.topcoder.com/tc?module=BasicData"
round_list_url = base_url + "&c=dd_round_list"
round_list_file = "round_list.xml"
round_results_url = base_url + "&c=dd_round_results&rd={0}"
round_results_file = "round_results_{0}.xml"
tc_data_sql = "tc_data.db"

round_list_desc = [
  ("round_id", "integer"),
  ("full_name", "text"),
  ("short_name", "text"),
  ("round_type_desc", "text"),
  ("date", "text")
]
round_list_table = "CREATE TABLE rounds (" + \
    ",".join([" ".join(field) for field in sorted(round_list_desc)]) + ")"
round_results_desc = [
  ("room_id", "integer"),
  ("room_name", "text"),
  ("coder_id", "integer"),
  ("handle", "text"),
  ("paid", "text"),
  ("old_rating", "integer"),
  ("new_rating", "integer"),
  ("new_vol", "integer"),
  ("num_ratings", "integer"),
  ("room_placed", "integer"),
  ("division_placed", "integer"),
  ("advanced", "text"),
  ("challenge_points", "real"),
  ("system_test_points", "real"),
  ("defense_points", "real"),
  ("submission_points", "real"),
  ("final_points", "real"),
  ("division", "integer"),
  ("problems_presented", "integer"),
  ("problems_submitted", "integer"),
  ("problems_correct", "integer"),
  ("problems_failed_by_system_test", "integer"),
  ("problems_failed_by_challenge", "integer"),
  ("problems_opened", "integer"),
  ("problems_left_open", "integer"),
  ("challenge_attempts_made", "integer"),
  ("challenges_made_successful", "integer"),
  ("challenges_made_failed", "integer"),
  ("challenge_attempts_received", "integer"),
  ("challenges_received_successful", "integer"),
  ("challenges_received_failed", "integer"),
  ("rated_flag", "integer"),
  ("level_one_problem_id", "integer"),
  ("level_one_submission_points", "real"),
  ("level_one_final_points", "real"),
  ("level_one_status", "text"),
  ("level_one_time_elapsed", "integer"),
  ("level_one_placed", "integer"),
  ("level_one_language", "text"),
  ("level_two_problem_id", "integer"),
  ("level_two_submission_points", "real"),
  ("level_two_final_points", "real"),
  ("level_two_status", "text"),
  ("level_two_time_elapsed", "integer"),
  ("level_two_placed", "integer"),
  ("level_two_language", "text"),
  ("level_three_problem_id", "integer"),
  ("level_three_submission_points", "real"),
  ("level_three_final_points", "real"),
  ("level_three_status", "text"),
  ("level_three_time_elapsed", "integer"),
  ("level_three_placed", "integer"),
  ("level_three_language", "text")
]
round_results_table = "CREATE TABLE results_{0} (" + \
    ",".join([" ".join(field) for field in sorted(round_results_desc)]) + ")"

conn = sqlite3.connect(tc_data_sql)
cursor = conn.cursor()

def setup_tc_data():
  cursor.execute(round_list_table)
  cursor.execute(round_results_table)

def read_row(row):
  row_data = {}
  child = row.firstChild
  while child is not None:
    if child.firstChild is not None:
      row_data[child.nodeName] = child.firstChild.nodeValue
    else:
      row_data[child.nodeName] = None
    child = child.nextSibling
  return row_data

def fetch_feeds(to_fetch):
  fetched = []
  for (url, filename) in to_fetch:
    time.sleep(1) # throttle fetches to prevent flooding TC server
    log.debug("Fetching " + url + " to local file " + filename)
    fetched.append(filename)
    (_, headers) = urllib.urlretrieve(url, filename)
  return fetched

def fetch_round_list():
  fetched = fetch_feeds([(round_list_url, round_list_file)])
  if len(fetched) > 0:
    load_round_list()

def fetch_round_results(round_ids):
  fetched = fetch_feeds([(round_results_url.format(rid), \
      round_results_file.format(rid)) for rid in round_ids])
  load_round_results(fetched)

def load_files(to_load):
  for (filename, sql) in to_load:
    feed_dom = parse(filename)
    data = []
    for row in feed_dom.getElementsByTagName("row"):
      data.append(read_row(row))
    for i in xrange(len(data)):
      data[i] = [data[i][x] for x in sorted(data[i].keys())]
    cursor.executemany(sql, data)

def load_round_list():
  field_ct = len(round_list_desc)
  insert_sql = "INSERT INTO rounds VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(round_list_file, insert_sql)])

def load_round_results(round_ids):
  field_ct = len(round_results_desc)
  insert_sql = "INSERT INTO results_{0} VALUES (" + \
      ",".join("?" * field_ct) + ")"
  load_files([(round_results_file.format(rid), insert_sql.format(rid)) \
      for rid in round_ids])
